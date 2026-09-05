"""
CYBERGUARD AI - Data Generation & Validation Tests
Validates synthetic dataset integrity, required schemas, and realistic value boundaries.
"""

import pytest
import pandas as pd
import numpy as np

from src.data_generator import (
    generate_candidate_locations,
    generate_synthetic_historical_data,
    haversine_np
)


def test_candidate_locations_generation():
    """Verify candidate locations have 100 entries and correct schema."""
    df_locs = generate_candidate_locations(num_locations=100, seed=42)
    assert len(df_locs) == 100
    
    required_cols = [
        "location_id", "location_name", "location_type",
        "latitude", "longitude", "historical_risk_score",
        "transaction_volume_score", "night_activity_score",
        "previous_incident_count", "area_risk_score"
    ]
    for col in required_cols:
        assert col in df_locs.columns, f"Missing required column: {col}"

    # Verify Hyderabad geographic boundaries
    assert df_locs["latitude"].between(17.2, 17.6).all(), "Coordinates outside Hyderabad range"
    assert df_locs["longitude"].between(78.2, 78.7).all(), "Coordinates outside Hyderabad range"

    # Verify score boundaries
    assert df_locs["historical_risk_score"].between(0.0, 1.0).all()
    assert df_locs["transaction_volume_score"].between(0.0, 1.0).all()
    assert (df_locs["previous_incident_count"] >= 0).all()


def test_synthetic_historical_complaints():
    """Verify complaint dataset generates >= 5000 records without NaNs."""
    locs = generate_candidate_locations(num_locations=100, seed=42)
    complaints_df, _ = generate_synthetic_historical_data(
        num_complaints=100, candidate_locations_df=locs, seed=42
    )
    assert len(complaints_df) == 100
    assert not complaints_df.isnull().any().any(), "Dataset contains unexpected NaNs"

    # Verify amounts are positive
    assert (complaints_df["transaction_amount"] > 0).all()

    # Verify hours are valid
    assert complaints_df["transaction_hour"].between(0, 23).all()


def test_haversine_formula():
    """Verify geographic distance computation."""
    # Hyderabad Center to Secunderabad ~ 8-10 km
    lat1, lon1 = 17.3850, 78.4867
    lat2, lon2 = 17.4399, 78.4983
    dist = haversine_np(lat1, lon1, lat2, lon2)
    assert 5.0 <= dist <= 12.0
    
    # Distance to self should be 0
    assert haversine_np(lat1, lon1, lat1, lon1) == pytest.approx(0.0, abs=1e-4)
