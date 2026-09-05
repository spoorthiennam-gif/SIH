"""
CYBERGUARD AI - Feature Engineering & Spatial Utilities
Calculates Haversine distance, normalized proximity, spatiotemporal features, and feature matrices.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List

FEATURE_COLUMNS = [
    "distance_km",
    "proximity_score",
    "candidate_historical_risk",
    "candidate_volume_score",
    "candidate_night_activity",
    "candidate_incident_count",
    "transaction_amount",
    "transaction_hour",
    "transaction_day",
    "is_night",
    "suspicious_activity_score",
    "victim_area_risk_score",
    "crime_type_Card Fraud",
    "crime_type_Other Financial Fraud",
    "crime_type_Phishing",
    "crime_type_UPI Fraud",
    "transaction_type_IMPS",
    "transaction_type_NEFT",
    "transaction_type_Other",
    "transaction_type_POS",
    "transaction_type_UPI"
]

ALL_CRIME_TYPES = ["Account Takeover", "Card Fraud", "Other Financial Fraud", "Phishing", "UPI Fraud"]
ALL_TRANSACTION_TYPES = ["ATM", "IMPS", "NEFT", "Other", "POS", "UPI"]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate geographic distance between two coordinates in kilometers using Haversine formula.
    """
    r = 6371.0  # Earth radius in kilometers
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))
    return float(r * c)


def calculate_proximity_score(distance_km: float, scale: float = 5.0) -> float:
    """
    Convert geographic distance into a normalized proximity score between 0 and 1.
    Higher means closer. At 0 km -> 1.0, at scale km (5 km) -> 0.5.
    """
    return float(1.0 / (1.0 + (distance_km / scale)))


def build_candidate_feature_row(complaint: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct model feature dict for a single complaint and candidate location pair.
    Zero target leakage: uses complaint inputs and location attributes only.
    """
    v_lat = float(complaint["latitude"])
    v_lon = float(complaint["longitude"])
    c_lat = float(candidate["latitude"])
    c_lon = float(candidate["longitude"])

    dist_km = haversine_distance(v_lat, v_lon, c_lat, c_lon)
    prox_score = calculate_proximity_score(dist_km)

    hour = int(complaint.get("transaction_hour", 12))
    day = int(complaint.get("transaction_day", 1))
    is_night = 1 if (hour >= 20 or hour <= 5) else 0

    c_type = complaint.get("crime_type", "UPI Fraud")
    t_type = complaint.get("transaction_type", "UPI")

    feat = {
        "distance_km": round(dist_km, 3),
        "proximity_score": round(prox_score, 4),
        "candidate_historical_risk": float(candidate.get("historical_risk_score", candidate.get("historical_risk", 0.5))),
        "candidate_volume_score": float(candidate.get("transaction_volume_score", 0.5)),
        "candidate_night_activity": float(candidate.get("night_activity_score", 0.5)),
        "candidate_incident_count": int(candidate.get("previous_incident_count", 0)),
        "transaction_amount": float(complaint.get("amount", complaint.get("transaction_amount", 50000.0))),
        "transaction_hour": hour,
        "transaction_day": day,
        "is_night": is_night,
        "suspicious_activity_score": float(complaint.get("suspicious_activity_score", 0.5)),
        "victim_area_risk_score": float(complaint.get("victim_area_risk_score", 0.5)),
    }

    # One-hot encoding dummy columns (consistent with FEATURE_COLUMNS)
    for ct in ["Card Fraud", "Other Financial Fraud", "Phishing", "UPI Fraud"]:
        feat[f"crime_type_{ct}"] = 1 if c_type == ct else 0

    for tt in ["IMPS", "NEFT", "Other", "POS", "UPI"]:
        feat[f"transaction_type_{tt}"] = 1 if t_type == tt else 0

    return feat


def prepare_training_matrices(df: pd.DataFrame) -> tuple:
    """
    Transform training dataframe into X feature matrix and y target vector.
    """
    # Create one-hot columns if not present
    df_encoded = pd.get_dummies(df, columns=["crime_type", "transaction_type"], drop_first=True)
    
    # Ensure all expected columns exist
    for col in FEATURE_COLUMNS:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    X = df_encoded[FEATURE_COLUMNS].copy()
    y = df_encoded["withdrawal_occurred"].astype(int).values
    return X, y
