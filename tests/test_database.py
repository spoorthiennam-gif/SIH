"""
CYBERGUARD AI - SQLite Database Layer Tests
Verifies schema initialization, complaint lifecycle, predictions persistence, and feedback logging.
"""

import pytest
import sqlite3
import os

from src.database import (
    init_db, save_complaint, get_complaint_by_id,
    save_predictions, get_predictions_by_complaint,
    save_feedback, get_all_feedback, get_dashboard_kpis
)


def test_database_crud_flow():
    """Verify end-to-end database operations."""
    init_db()

    # 1. Insert complaint
    test_complaint = {
        "complaint_id": "TEST-CYB-9999",
        "crime_type": "UPI Fraud",
        "transaction_type": "UPI",
        "amount": 45000.0,
        "timestamp": "2026-09-04 18:30:00",
        "latitude": 17.4150,
        "longitude": 78.4350,
        "previous_transaction_count": 2,
        "previous_transaction_amount": 12000.0,
        "time_since_previous_transaction": 30.0,
        "suspicious_activity_score": 0.85,
        "victim_area_risk_score": 0.70,
        "status": "TEST_READY"
    }
    save_complaint(test_complaint)

    # 2. Retrieve complaint
    retrieved = get_complaint_by_id("TEST-CYB-9999")
    assert retrieved is not None
    assert retrieved["crime_type"] == "UPI Fraud"
    assert retrieved["amount"] == 45000.0

    # 3. Save mock predictions
    mock_preds = [
        {
            "location_id": "LOC_001",
            "location_name": "Test Node A",
            "ml_probability": 0.82,
            "historical_risk": 0.75,
            "proximity_score": 0.88,
            "final_risk_score": 0.81,
            "risk_level": "HIGH",
            "distance_km": 1.2,
            "rank": 1,
            "explanation": "High proximity test"
        }
    ]
    save_predictions("TEST-CYB-9999", mock_preds)

    # 4. Fetch predictions
    preds = get_predictions_by_complaint("TEST-CYB-9999")
    assert len(preds) == 1
    assert preds[0]["location_id"] == "LOC_001"
    assert preds[0]["final_risk_score"] == pytest.approx(0.81)

    # 5. Save and fetch feedback
    save_feedback(
        complaint_id="TEST-CYB-9999",
        location_id="LOC_001",
        status="Confirmed useful",
        notes="Automated test validation note"
    )
    all_fb = get_all_feedback()
    assert any(fb["complaint_id"] == "TEST-CYB-9999" for fb in all_fb)

    # 6. Dashboard KPIs
    kpis = get_dashboard_kpis()
    assert kpis["total_complaints"] >= 1
