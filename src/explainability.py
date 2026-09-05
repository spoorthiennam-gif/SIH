"""
CYBERGUARD AI - Explainable AI (XAI) Engine
Dynamically constructs transparent, factor-level explanations for ranked candidate locations
using actual feature values, proximity metrics, and domain-grounded decision support logic.
"""

from typing import Dict, Any, List


def generate_location_explanation(
    complaint: Dict[str, Any],
    candidate: Dict[str, Any],
    ml_prob: float,
    proximity_score: float,
    distance_km: float,
    final_score: float
) -> Dict[str, Any]:
    """
    Generate dynamic, explainable intelligence factors for a ranked candidate location.
    Transparently itemizes why this candidate received its elevated risk score.
    """
    factors = []
    
    # 1. Geographic proximity factor
    if distance_km < 3.0:
        factors.append(f"Immediate Geographic Proximity: {distance_km:.2f} km away (Proximity index {proximity_score:.2f})")
    elif distance_km < 7.0:
        factors.append(f"Accessible Transit Corridor: {distance_km:.2f} km from reported incident epicenter")
    else:
        factors.append(f"Extended Perimeter Location: {distance_km:.2f} km (lower spatial weight, elevated behavioral risk)")

    # 2. Historical location risk factor
    hist_risk = float(candidate.get("historical_risk_score", candidate.get("historical_risk", 0.5)))
    incidents = int(candidate.get("previous_incident_count", 0))
    if hist_risk >= 0.70:
        factors.append(f"Elevated Historical Risk: {hist_risk:.2f} historical risk score with {incidents} prior reported incidents")
    elif hist_risk >= 0.50:
        factors.append(f"Moderate Historical Risk: {hist_risk:.2f} risk index with moderate past withdrawal activity ({incidents} cases)")
    else:
        factors.append(f"Baseline Historical Risk: {hist_risk:.2f} historical index in commercial cluster")

    # 3. Temporal & Night Activity alignment
    hour = int(complaint.get("transaction_hour", 12))
    night_act = float(candidate.get("night_activity_score", 0.5))
    if (hour >= 20 or hour <= 5) and night_act >= 0.60:
        factors.append(f"Nighttime Cashout Vulnerability: Incident reported during night window ({hour:02d}:00) matching high 24/7 ATM activity ({night_act:.2f})")
    elif 10 <= hour <= 18:
        factors.append(f"Peak Business Hours: Peak commercial hours ({hour:02d}:00) favor high-volume teller and ATM queues")

    # 4. Crime type and amount pattern match
    crime_type = complaint.get("crime_type", "UPI Fraud")
    amount = float(complaint.get("amount", complaint.get("transaction_amount", 50000.0)))
    if amount >= 100000:
        factors.append(f"High-Value Transaction Pattern: Amount ₹{amount:,.2f} correlates with multi-ATM split withdrawals in commercial hubs")
    elif crime_type == "UPI Fraud":
        factors.append(f"Rapid UPI Extraction Profile: Fast digital transfers historically channel into immediate transit ATM cashouts")
    elif crime_type == "Card Fraud":
        factors.append(f"Card Skimming / Cloning Cluster: Card fraud complaints show strong affinity to unmonitored stand-alone kiosks")

    # 5. ML Model Confidence
    if ml_prob >= 0.70:
        factors.append(f"Machine Learning Pattern Match: High classifier probability ({ml_prob*100:.1f}%) based on multi-feature historical correlation")
    else:
        factors.append(f"Machine Learning Baseline: Probabilistic estimate {ml_prob*100:.1f}% combined with environmental risk indices")

    # Recommended priority
    if final_score >= 0.75:
        priority = "HIGH PRIORITY - Immediate field / surveillance verification recommended"
    elif final_score >= 0.50:
        priority = "MEDIUM PRIORITY - Secondary patrol sweep and CCTV query log request"
    else:
        priority = "ROUTINE MONITORING - Record candidate in comparative analytics log"

    summary_text = " • " + "\n • ".join(factors)

    return {
        "factors": factors,
        "summary_text": summary_text,
        "recommended_priority": priority,
        "disclaimer": "Decision-support output only. Investigators must independently verify information and follow applicable legal and departmental procedures."
    }
