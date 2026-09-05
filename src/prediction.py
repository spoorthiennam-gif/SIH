"""
CYBERGUARD AI - Predictive Intelligence & Ranking Engine
Scores all candidate locations for a given complaint, ranks them by final risk score,
generates forecasted time windows, and produces decision-support intelligence.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

from src.feature_engineering import (
    haversine_distance, calculate_proximity_score,
    build_candidate_feature_row, FEATURE_COLUMNS
)
from src.risk_scoring import compute_final_risk_score, classify_risk_level
from src.explainability import generate_location_explanation
from src.database import save_predictions, get_candidate_locations
from src.model_training import load_trained_model

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def calculate_forecast_time_window(hour: int, crime_type: str) -> str:
    """
    Generate an explainable estimated risk time window based on complaint hour and crime velocity.
    Transparently labeled as a forecast, not a guaranteed event time.
    """
    # Rapid digital fraud (UPI) tends to cashout within 1 to 2 hours
    # Card / account fraud often cashes out within 2 to 4 hours or overnight
    if crime_type in ["UPI Fraud", "Phishing"]:
        start_h = hour
        end_h = (hour + 2) % 24
    else:
        start_h = hour
        end_h = (hour + 3) % 24

    return f"{start_h:02d}:00 – {end_h:02d}:00 (Elevated Synthetic Risk Window)"


def predict_candidate_locations(
    complaint: Dict[str, Any],
    top_n: int = 5,
    candidates_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Execute full candidate location ranking pipeline for a cybercrime complaint:
    1. Evaluate all candidate locations (100 in synthetic Hyderabad environment)
    2. Compute geospatial Haversine distance and proximity index
    3. Generate feature vectors and compute ML model probabilities
    4. Apply transparent prototype risk formula (0.60 ML + 0.25 Hist + 0.15 Prox)
    5. Rank descending and attach explainability factor breakdown
    """
    if candidates_df is None or candidates_df.empty:
        candidates_df = get_candidate_locations()
        if candidates_df.empty:
            loc_csv = os.path.join(DATA_DIR, "synthetic_locations.csv")
            if os.path.exists(loc_csv):
                candidates_df = pd.read_csv(loc_csv)
            else:
                raise ValueError("No candidate locations found. Please generate the synthetic dataset first.")

    model, metadata = load_trained_model()
    if model is None:
        raise FileNotFoundError("Trained prediction model not found. Please train the model before running predictions.")

    v_lat = float(complaint["latitude"])
    v_lon = float(complaint["longitude"])
    complaint_id = str(complaint["complaint_id"])
    c_type = str(complaint.get("crime_type", "UPI Fraud"))
    hour = int(complaint.get("transaction_hour", 12))

    # Pre-build feature matrix for all candidates in vector batch for high speed
    feature_rows = []
    candidate_meta = []

    for _, cand in candidates_df.iterrows():
        c_lat = float(cand["latitude"])
        c_lon = float(cand["longitude"])
        dist_km = haversine_distance(v_lat, v_lon, c_lat, c_lon)
        prox_score = calculate_proximity_score(dist_km)

        row_dict = build_candidate_feature_row(complaint, cand.to_dict())
        feature_rows.append([row_dict[col] for col in FEATURE_COLUMNS])

        hist_risk = float(cand.get("historical_risk_score", cand.get("historical_risk", 0.5)))
        candidate_meta.append({
            "location_id": str(cand.get("location_id", f"LOC_{_}")),
            "location_name": str(cand.get("location_name") or cand.get("name") or cand.get("location_id", "Unknown Node")),
            "location_type": str(cand.get("location_type", "ATM Kiosk")),
            "latitude": c_lat,
            "longitude": c_lon,
            "distance_km": round(dist_km, 2),
            "proximity_score": round(prox_score, 4),
            "historical_risk": round(hist_risk, 3),
            "transaction_volume_score": float(cand.get("transaction_volume_score", 0.5)),
            "night_activity_score": float(cand.get("night_activity_score", 0.5)),
            "previous_incident_count": int(cand.get("previous_incident_count", 0)),
            "area_risk_score": float(cand.get("area_risk_score", 0.5))
        })

    # Batch ML probability inference
    X_batch = pd.DataFrame(feature_rows, columns=FEATURE_COLUMNS)
    ml_probs = model.predict_proba(X_batch)[:, 1]

    # Combine with prototype formula and categorize
    scored_candidates = []
    for i, meta in enumerate(candidate_meta):
        prob = float(ml_probs[i])
        final_score = compute_final_risk_score(
            ml_probability=prob,
            historical_risk=meta["historical_risk"],
            proximity_score=meta["proximity_score"]
        )
        risk_level, color, badge = classify_risk_level(final_score)

        meta["ml_probability"] = round(prob, 4)
        meta["final_risk_score"] = final_score
        meta["risk_percentage"] = round(final_score * 100, 1)
        meta["risk_level"] = risk_level
        meta["risk_color"] = color
        meta["risk_badge"] = badge
        scored_candidates.append(meta)

    # Sort all candidates by final_risk_score descending
    scored_candidates.sort(key=lambda x: x["final_risk_score"], reverse=True)

    # Assign ranks and generate explainability for top candidates
    for rank_idx, cand in enumerate(scored_candidates, 1):
        cand["rank"] = rank_idx
        if rank_idx <= 10:
            explanation = generate_location_explanation(
                complaint=complaint,
                candidate=cand,
                ml_prob=cand["ml_probability"],
                proximity_score=cand["proximity_score"],
                distance_km=cand["distance_km"],
                final_score=cand["final_risk_score"]
            )
            cand["explanation_factors"] = explanation["factors"]
            cand["explanation"] = explanation["summary_text"]
            cand["recommended_priority"] = explanation["recommended_priority"]
        else:
            cand["explanation_factors"] = []
            cand["explanation"] = "Standard algorithmic ranking based on geospatial proximity and historical risk metrics."
            cand["recommended_priority"] = "ROUTINE"

    # Persist predictions to SQLite database
    save_predictions(complaint_id, scored_candidates)

    forecast_window = calculate_forecast_time_window(hour, c_type)

    top_candidates = scored_candidates[:top_n]
    top_1 = scored_candidates[0] if scored_candidates else {}

    intelligence_summary = {
        "complaint_id": complaint_id,
        "crime_type": c_type,
        "amount": float(complaint.get("amount", 0.0)),
        "top_candidate_name": top_1.get("location_name", "N/A"),
        "top_risk_percentage": top_1.get("risk_percentage", 0.0),
        "top_risk_level": top_1.get("risk_level", "UNKNOWN"),
        "top_risk_color": top_1.get("risk_color", "#ef4444"),
        "top_distance_km": top_1.get("distance_km", 0.0),
        "forecast_time_window": forecast_window,
        "top_explanation": top_1.get("explanation", ""),
        "recommended_priority": top_1.get("recommended_priority", "HIGH PRIORITY"),
        "disclaimer": "Decision-support output only. Investigators must independently verify information and follow applicable legal and departmental procedures."
    }

    return {
        "complaint_id": complaint_id,
        "top_candidates": top_candidates,
        "all_ranked_candidates": scored_candidates,
        "forecast_time_window": forecast_window,
        "intelligence_summary": intelligence_summary,
        "metadata": metadata
    }
