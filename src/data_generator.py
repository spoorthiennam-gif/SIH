"""
CYBERGUARD AI - Synthetic Dataset Generator
Generates realistic demonstration data centered around Hyderabad, Telangana.
Ensures zero PII, zero real-world police/banking secrets, and clear synthetic marking.
"""

import os
import numpy as np
import pandas as pd
from typing import Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


# Realistic Hyderabad neighborhood hubs for synthetic candidate locations
HYDERABAD_HUBS = [
    {"name": "Banjara Hills Rd 12", "lat": 17.4156, "lon": 78.4350, "risk_base": 0.65},
    {"name": "Hitec City Cyber Towers", "lat": 17.4504, "lon": 78.3808, "risk_base": 0.72},
    {"name": "Begumpet Main Road", "lat": 17.4440, "lon": 78.4650, "risk_base": 0.60},
    {"name": "Gachibowli DLF Kiosk", "lat": 17.4401, "lon": 78.3582, "risk_base": 0.75},
    {"name": "Ameerpet Metro Hub", "lat": 17.4375, "lon": 78.4483, "risk_base": 0.85},
    {"name": "Secunderabad Railway Stn", "lat": 17.4339, "lon": 78.5015, "risk_base": 0.82},
    {"name": "Dilsukhnagar Cross Roads", "lat": 17.3688, "lon": 78.5247, "risk_base": 0.80},
    {"name": "Charminar Old City Center", "lat": 17.3616, "lon": 78.4747, "risk_base": 0.78},
    {"name": "Kukatpally KPHB Colony", "lat": 17.4938, "lon": 78.3995, "risk_base": 0.70},
    {"name": "Madhapur 100ft Road", "lat": 17.4483, "lon": 78.3915, "risk_base": 0.68},
    {"name": "Mehdipatnam Rythu Bazar", "lat": 17.3917, "lon": 78.4410, "risk_base": 0.76},
    {"name": "Jubilee Hills Checkpost", "lat": 17.4294, "lon": 78.4095, "risk_base": 0.55},
    {"name": "Tolichowki X Roads", "lat": 17.4011, "lon": 78.4124, "risk_base": 0.74},
    {"name": "Uppal Ring Road", "lat": 17.4018, "lon": 78.5602, "risk_base": 0.62},
    {"name": "Kondapur Botanical Garden", "lat": 17.4610, "lon": 78.3670, "risk_base": 0.58},
    {"name": "Abids Commercial Center", "lat": 17.3888, "lon": 78.4735, "risk_base": 0.73},
    {"name": "Miyapur Metro Terminal", "lat": 17.4968, "lon": 78.3551, "risk_base": 0.64},
    {"name": "Somajiguda Circle", "lat": 17.4243, "lon": 78.4578, "risk_base": 0.59},
    {"name": "Malakpet Super Bazar", "lat": 17.3752, "lon": 78.5020, "risk_base": 0.71},
    {"name": "Sanath Nagar Industrial", "lat": 17.4580, "lon": 78.4411, "risk_base": 0.66}
]

BANK_NAMES = [
    "State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank",
    "Kotak Mahindra Bank", "Punjab National Bank", "Bank of Baroda",
    "Union Bank of India", "Canara Bank", "IndusInd Bank", "Tata Indicash", "Hitachi Money Spot"
]

LOCATION_TYPES = ["ATM Kiosk", "Bank Branch Counter", "Customer Service Point (CSP)"]

CRIME_TYPES = [
    "UPI Fraud", "Card Fraud", "Account Takeover", "Phishing", "Other Financial Fraud"
]

TRANSACTION_TYPES = [
    "UPI", "ATM", "POS", "IMPS", "NEFT", "Other"
]


def generate_candidate_locations(num_locations: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate 100 synthetic candidate cash-withdrawal locations across Hyderabad."""
    np.random.seed(seed)
    records = []

    for i in range(num_locations):
        hub = HYDERABAD_HUBS[i % len(HYDERABAD_HUBS)]
        bank = BANK_NAMES[i % len(BANK_NAMES)]
        loc_type = np.random.choice(LOCATION_TYPES, p=[0.70, 0.15, 0.15])
        
        # Add slight spatial variance around hub (+- 0.015 deg ~ 1.5 km)
        lat = round(hub["lat"] + np.random.normal(0, 0.012), 5)
        lon = round(hub["lon"] + np.random.normal(0, 0.012), 5)
        
        # Base risk + variance
        hist_risk = float(np.clip(hub["risk_base"] + np.random.normal(0, 0.10), 0.15, 0.95))
        hist_risk = round(hist_risk, 3)
        
        volume_score = round(float(np.clip(0.4 + 0.5 * hist_risk + np.random.normal(0, 0.1), 0.1, 0.99)), 3)
        night_score = round(float(np.clip(0.3 + 0.4 * (1 if "ATM" in loc_type else 0.1) + np.random.normal(0, 0.15), 0.1, 0.95)), 3)
        incident_count = int(np.clip(hist_risk * 35 + np.random.normal(0, 4), 0, 40))
        area_risk = round(float(np.clip(hub["risk_base"] + np.random.normal(0, 0.08), 0.1, 0.95)), 3)

        records.append({
            "location_id": f"LOC_{i+1:03d}",
            "location_name": f"Synthetic {bank} - {hub['name']} #{i+1}",
            "location_type": loc_type,
            "latitude": lat,
            "longitude": lon,
            "historical_risk_score": hist_risk,
            "transaction_volume_score": volume_score,
            "night_activity_score": night_score,
            "previous_incident_count": incident_count,
            "area_risk_score": area_risk
        })

    df = pd.DataFrame(records)
    return df


def haversine_np(lat1, lon1, lat2, lon2):
    """Compute Haversine distance in km between coordinates."""
    r = 6371.0  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))
    return r * c


def generate_synthetic_historical_data(
    num_complaints: int = 5000,
    candidate_locations_df: pd.DataFrame = None,
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate 5,000+ synthetic complaints and paired training examples.
    Ensures realistic non-trivial correlations without target leakage.
    """
    np.random.seed(seed)
    if candidate_locations_df is None:
        candidate_locations_df = generate_candidate_locations(num_locations=100, seed=seed)

    complaints_list = []
    training_pairs = []

    # Amount distributions per crime type (synthetic)
    amount_params = {
        "UPI Fraud": (45000, 25000, 2000, 100000),
        "Card Fraud": (30000, 18000, 1000, 80000),
        "Account Takeover": (110000, 45000, 20000, 250000),
        "Phishing": (55000, 30000, 3000, 120000),
        "Other Financial Fraud": (40000, 22000, 1500, 90000)
    }

    # Center around Hyderabad
    center_lat, center_lon = 17.4100, 78.4500

    for idx in range(num_complaints):
        case_id = f"CASE_{10000 + idx + 1}"
        crime_type = np.random.choice(
            CRIME_TYPES,
            p=[0.40, 0.25, 0.15, 0.12, 0.08]
        )
        tx_type = np.random.choice(
            TRANSACTION_TYPES,
            p=[0.45, 0.20, 0.15, 0.10, 0.08, 0.02]
        )

        mean_amt, std_amt, min_amt, max_amt = amount_params[crime_type]
        amount = round(float(np.clip(np.random.normal(mean_amt, std_amt), min_amt, max_amt)), 2)

        # Realistic hour distribution: evening/afternoon peaks
        raw_hour_weights = np.array([
            0.02, 0.01, 0.01, 0.01, 0.01, 0.02,  # 00-05
            0.03, 0.04, 0.05, 0.06, 0.07, 0.08,  # 06-11
            0.07, 0.08, 0.09, 0.07, 0.06, 0.08,  # 12-17
            0.09, 0.09, 0.08, 0.06, 0.04, 0.02   # 18-23
        ], dtype=float)
        hour_weights = raw_hour_weights / raw_hour_weights.sum()
        hour = int(np.random.choice(range(24), p=hour_weights))
        day = int(np.random.choice(range(7)))

        # Incident / victim location
        v_lat = round(center_lat + np.random.normal(0, 0.045), 5)
        v_lon = round(center_lon + np.random.normal(0, 0.055), 5)

        prev_tx_cnt = int(np.random.choice(range(8), p=[0.25, 0.30, 0.20, 0.12, 0.08, 0.03, 0.01, 0.01]))
        prev_tx_amt = round(float(prev_tx_cnt * np.random.uniform(5000, 30000)), 2)
        time_since_prev = round(float(np.random.exponential(60.0) + 10.0), 1)
        
        suspicious_score = round(float(np.clip(
            (amount / max_amt) * 0.4 + (prev_tx_cnt / 7.0) * 0.3 + np.random.normal(0.2, 0.1),
            0.1, 0.98
        )), 3)
        victim_area_risk = round(float(np.clip(np.random.beta(2, 2), 0.1, 0.95)), 3)

        complaint_dict = {
            "case_id": case_id,
            "crime_type": crime_type,
            "transaction_type": tx_type,
            "transaction_amount": amount,
            "transaction_hour": hour,
            "transaction_day": day,
            "victim_latitude": v_lat,
            "victim_longitude": v_lon,
            "previous_transaction_count": prev_tx_cnt,
            "previous_transaction_amount": prev_tx_amt,
            "time_since_previous_transaction": time_since_prev,
            "suspicious_activity_score": suspicious_score,
            "victim_area_risk_score": victim_area_risk,
            "timestamp": f"2026-08-{(idx % 28) + 1:02d} {hour:02d}:{(idx * 7) % 60:02d}:00"
        }
        complaints_list.append(complaint_dict)

        # Now sample training pairs: for this complaint, select a true withdrawal location and 4 negative locations
        # Probability of choosing location depends on proximity and location risk
        dists = haversine_np(
            v_lat, v_lon,
            candidate_locations_df["latitude"].values,
            candidate_locations_df["longitude"].values
        )
        proximity_scores = 1.0 / (1.0 + dists / 4.0)
        hist_risks = candidate_locations_df["historical_risk_score"].values
        night_scores = candidate_locations_df["night_activity_score"].values
        
        # Is night
        is_night = 1.0 if (hour >= 20 or hour <= 5) else 0.0
        
        # Synthetic preference weights for true withdrawal location selection
        selection_scores = (
            0.45 * proximity_scores +
            0.30 * hist_risks +
            0.15 * (night_scores * is_night + (1 - is_night) * (1 - night_scores)) +
            0.10 * np.random.uniform(0, 0.3, len(dists))
        )
        
        # Pick 1 positive withdrawal location
        pos_idx = int(np.argmax(selection_scores))
        
        # Pick 4 negative locations (at various distances)
        other_indices = [i for i in range(len(candidate_locations_df)) if i != pos_idx]
        neg_indices = list(np.random.choice(other_indices, size=4, replace=False))

        # Add positive example
        pos_row = candidate_locations_df.iloc[pos_idx]
        training_pairs.append({
            "case_id": case_id,
            "crime_type": crime_type,
            "transaction_type": tx_type,
            "transaction_amount": amount,
            "transaction_hour": hour,
            "transaction_day": day,
            "is_night": int(is_night),
            "victim_latitude": v_lat,
            "victim_longitude": v_lon,
            "candidate_latitude": float(pos_row["latitude"]),
            "candidate_longitude": float(pos_row["longitude"]),
            "distance_km": float(dists[pos_idx]),
            "proximity_score": float(proximity_scores[pos_idx]),
            "candidate_historical_risk": float(pos_row["historical_risk_score"]),
            "candidate_volume_score": float(pos_row["transaction_volume_score"]),
            "candidate_night_activity": float(pos_row["night_activity_score"]),
            "candidate_incident_count": int(pos_row["previous_incident_count"]),
            "suspicious_activity_score": suspicious_score,
            "victim_area_risk_score": victim_area_risk,
            "withdrawal_occurred": 1
        })

        # Add negative examples
        for n_idx in neg_indices:
            neg_row = candidate_locations_df.iloc[n_idx]
            training_pairs.append({
                "case_id": case_id,
                "crime_type": crime_type,
                "transaction_type": tx_type,
                "transaction_amount": amount,
                "transaction_hour": hour,
                "transaction_day": day,
                "is_night": int(is_night),
                "victim_latitude": v_lat,
                "victim_longitude": v_lon,
                "candidate_latitude": float(neg_row["latitude"]),
                "candidate_longitude": float(neg_row["longitude"]),
                "distance_km": float(dists[n_idx]),
                "proximity_score": float(proximity_scores[n_idx]),
                "candidate_historical_risk": float(neg_row["historical_risk_score"]),
                "candidate_volume_score": float(neg_row["transaction_volume_score"]),
                "candidate_night_activity": float(neg_row["night_activity_score"]),
                "candidate_incident_count": int(neg_row["previous_incident_count"]),
                "suspicious_activity_score": suspicious_score,
                "victim_area_risk_score": victim_area_risk,
                "withdrawal_occurred": 0
            })

    complaints_df = pd.DataFrame(complaints_list)
    training_df = pd.DataFrame(training_pairs)

    # Save CSVs to data/
    os.makedirs(DATA_DIR, exist_ok=True)
    complaints_df.to_csv(os.path.join(DATA_DIR, "synthetic_complaints.csv"), index=False)
    candidate_locations_df.to_csv(os.path.join(DATA_DIR, "synthetic_locations.csv"), index=False)
    training_df.to_csv(os.path.join(DATA_DIR, "synthetic_training_pairs.csv"), index=False)

    return complaints_df, candidate_locations_df
