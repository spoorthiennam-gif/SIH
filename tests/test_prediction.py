"""
CYBERGUARD AI - Prediction Engine & Risk Scoring Tests
Verifies transparent prototype scoring formula, boundary preservation, and risk classification.
"""

import pytest
from src.risk_scoring import compute_final_risk_score, classify_risk_level
from src.feature_engineering import calculate_proximity_score, haversine_distance


def test_proximity_score_behavior():
    """Verify proximity function yields expected normalized decay."""
    assert calculate_proximity_score(0.0) == pytest.approx(1.0)
    assert calculate_proximity_score(5.0) == pytest.approx(0.5)
    assert calculate_proximity_score(15.0) == pytest.approx(0.25)
    # Further away must always be strictly lower
    assert calculate_proximity_score(10.0) < calculate_proximity_score(2.0)


def test_risk_scoring_bounds():
    """Verify final risk score is strictly bounded in [0.0, 1.0]."""
    # Minimum possible
    min_score = compute_final_risk_score(0.0, 0.0, 0.0)
    assert min_score == 0.0

    # Maximum possible
    max_score = compute_final_risk_score(1.0, 1.0, 1.0)
    assert max_score == 1.0

    # Mid range
    mid_score = compute_final_risk_score(0.70, 0.80, 0.60)
    # 0.60*0.70 + 0.25*0.80 + 0.15*0.60 = 0.42 + 0.20 + 0.09 = 0.71
    assert mid_score == pytest.approx(0.71, abs=1e-3)


def test_risk_level_classification():
    """Verify risk levels categorize correctly at exact thresholds."""
    assert classify_risk_level(0.80)[0] == "HIGH"
    assert classify_risk_level(0.75)[0] == "HIGH"
    assert classify_risk_level(0.74)[0] == "MEDIUM"
    assert classify_risk_level(0.50)[0] == "MEDIUM"
    assert classify_risk_level(0.49)[0] == "LOW"
    assert classify_risk_level(0.10)[0] == "LOW"
