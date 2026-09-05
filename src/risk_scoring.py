"""
CYBERGUARD AI - Risk Scoring Engine
Implements the transparent prototype scoring formula, weighting, and risk tier categorization.
"""

from typing import Dict, Any, Tuple

# Prototype scoring weights (Configurable)
DEFAULT_WEIGHTS = {
    "w_ml": 0.60,
    "w_hist": 0.25,
    "w_prox": 0.15
}

# Risk level thresholds
HIGH_RISK_THRESHOLD = 0.75
MEDIUM_RISK_THRESHOLD = 0.50

# Professional SIH visual styling colors
RISK_COLORS = {
    "HIGH": "#ef4444",      # Vibrant Red
    "MEDIUM": "#f59e0b",    # Amber/Orange
    "LOW": "#10b981"        # Emerald Green
}

RISK_BADGES = {
    "HIGH": "🔴 HIGH RISK",
    "MEDIUM": "🟠 MEDIUM RISK",
    "LOW": "🟢 LOW RISK"
}


def compute_final_risk_score(
    ml_probability: float,
    historical_risk: float,
    proximity_score: float,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculate transparent prototype risk score:
    Final Risk Score = (0.60 * ML Probability) + (0.25 * Historical Risk) + (0.15 * Proximity Score)
    Guaranteed bounded strictly in [0.0, 1.0].
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    w_ml = weights.get("w_ml", 0.60)
    w_hist = weights.get("w_hist", 0.25)
    w_prox = weights.get("w_prox", 0.15)

    # Normalize inputs to [0, 1]
    p_ml = max(0.0, min(1.0, float(ml_probability)))
    p_hist = max(0.0, min(1.0, float(historical_risk)))
    p_prox = max(0.0, min(1.0, float(proximity_score)))

    # Compute weighted sum
    raw_score = (w_ml * p_ml) + (w_hist * p_hist) + (w_prox * p_prox)
    total_weight = w_ml + w_hist + w_prox

    normalized_score = raw_score / total_weight if total_weight > 0 else 0.0
    return round(float(max(0.0, min(1.0, normalized_score))), 4)


def classify_risk_level(final_score: float) -> Tuple[str, str, str]:
    """
    Classify risk score into HIGH, MEDIUM, or LOW tier with color and badge.
    """
    if final_score >= HIGH_RISK_THRESHOLD:
        level = "HIGH"
    elif final_score >= MEDIUM_RISK_THRESHOLD:
        level = "MEDIUM"
    else:
        level = "LOW"

    return level, RISK_COLORS[level], RISK_BADGES[level]


def get_risk_metadata(final_score: float) -> Dict[str, Any]:
    """Return complete risk classification metadata."""
    level, color, badge = classify_risk_level(final_score)
    return {
        "final_risk_score": final_score,
        "percentage": round(final_score * 100, 1),
        "risk_level": level,
        "color": color,
        "badge": badge
    }
