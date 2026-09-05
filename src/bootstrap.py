"""
CYBERGUARD AI - Self-Healing Bootstrap Initialization Module
Ensures the database, 5,000+ synthetic historical records, 100 candidate locations,
and trained RandomForest model exist and are ready on startup.
"""

import os
import pandas as pd
from src.database import (
    init_db, save_candidate_locations, get_candidate_locations,
    save_complaint, get_latest_model_run, DB_PATH
)
from src.data_generator import (
    generate_candidate_locations, generate_synthetic_historical_data
)
from src.model_training import train_prediction_model, load_trained_model

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


def bootstrap_system(force_retrain: bool = False):
    """
    Check all required components and initialize anything missing:
    1. Initialize SQLite database schema
    2. Generate 100 synthetic candidate locations if missing
    3. Generate 5,000 synthetic historical cases if missing
    4. Train and persist Random Forest model if missing
    5. Seed initial complaints into SQLite if empty
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1. Initialize SQLite schema
    init_db()

    # 2. Check Candidate Locations
    locations_csv = os.path.join(DATA_DIR, "synthetic_locations.csv")
    if not os.path.exists(locations_csv):
        locations_df = generate_candidate_locations(num_locations=100, seed=42)
        save_candidate_locations(locations_df)
    else:
        locations_df = pd.read_csv(locations_csv)
        # Ensure DB has candidate locations
        db_locations = get_candidate_locations()
        if db_locations.empty:
            save_candidate_locations(locations_df)

    # 3. Check Synthetic Historical Cases & Training Pairs
    complaints_csv = os.path.join(DATA_DIR, "synthetic_complaints.csv")
    training_csv = os.path.join(DATA_DIR, "synthetic_training_pairs.csv")
    if not os.path.exists(complaints_csv) or not os.path.exists(training_csv):
        complaints_df, _ = generate_synthetic_historical_data(
            num_complaints=5000,
            candidate_locations_df=locations_df,
            seed=42
        )
        # Seed first 20 complaints into DB for immediate dashboard display
        for _, row in complaints_df.head(25).iterrows():
            save_complaint({
                "complaint_id": row["case_id"],
                "crime_type": row["crime_type"],
                "transaction_type": row["transaction_type"],
                "amount": float(row["transaction_amount"]),
                "timestamp": str(row["timestamp"]),
                "latitude": float(row["victim_latitude"]),
                "longitude": float(row["victim_longitude"]),
                "previous_transaction_count": int(row["previous_transaction_count"]),
                "previous_transaction_amount": float(row["previous_transaction_amount"]),
                "time_since_previous_transaction": float(row["time_since_previous_transaction"]),
                "suspicious_activity_score": float(row["suspicious_activity_score"]),
                "victim_area_risk_score": float(row["victim_area_risk_score"]),
                "status": "INITIAL_SEED"
            })
    else:
        complaints_df = pd.read_csv(complaints_csv)

    # 4. Check Trained Model
    model, metadata = load_trained_model()
    if model is None or force_retrain or get_latest_model_run() is None:
        metrics = train_prediction_model(training_csv)
    else:
        metrics = metadata

    return {
        "status": "READY",
        "num_locations": len(locations_df),
        "num_complaints": len(complaints_df),
        "model_accuracy": metrics.get("accuracy", 0.0),
        "top5_accuracy": metrics.get("top5", 0.0)
    }
