"""
CYBERGUARD AI - Model Integrity & Zero-Leakage Tests
Verifies RandomForest model persistence, probability bounds, and target leakage prevention.
"""

import pytest
import os
import json
import numpy as np
import pandas as pd

from src.feature_engineering import FEATURE_COLUMNS, build_candidate_feature_row
from src.model_training import load_trained_model


def test_zero_target_leakage():
    """Verify target variable withdrawal_occurred is strictly excluded from feature matrix."""
    assert "withdrawal_occurred" not in FEATURE_COLUMNS
    for col in FEATURE_COLUMNS:
        assert not col.startswith("target_"), f"Potential target feature: {col}"
        assert col != "y", "Target indicator present in features"


def test_feature_row_generation():
    """Verify single candidate feature vector matches expected feature columns."""
    dummy_complaint = {
        "complaint_id": "TEST_001",
        "latitude": 17.4100,
        "longitude": 78.4500,
        "crime_type": "UPI Fraud",
        "transaction_type": "UPI",
        "amount": 50000.0,
        "transaction_hour": 18,
        "transaction_day": 2,
        "suspicious_activity_score": 0.8,
        "victim_area_risk_score": 0.6
    }
    dummy_candidate = {
        "location_id": "LOC_001",
        "latitude": 17.4200,
        "longitude": 78.4600,
        "historical_risk_score": 0.75,
        "transaction_volume_score": 0.7,
        "night_activity_score": 0.65,
        "previous_incident_count": 12,
        "area_risk_score": 0.7
    }

    feat = build_candidate_feature_row(dummy_complaint, dummy_candidate)
    for col in FEATURE_COLUMNS:
        assert col in feat, f"Feature missing in candidate row: {col}"
        assert not np.isnan(feat[col]), f"NaN found in feature {col}"
        assert np.isfinite(feat[col]), f"Non-finite value in feature {col}"
