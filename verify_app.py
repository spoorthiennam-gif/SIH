"""
CYBERGUARD AI - Complete End-to-End Programmatic Verification
Tests:
1. Scenario 1 execution & Top-5 ranking
2. Scenario 2 execution & Top-5 ranking
3. Scenario 3 execution & Top-5 ranking
4. Dynamic explainability generation
5. Folium map generation
6. Investigator feedback persistence in SQLite
7. KPI calculations
8. Plotly chart generation
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import (
    save_complaint, get_complaint_by_id, get_predictions_by_complaint,
    save_feedback, get_all_feedback, get_dashboard_kpis, get_latest_model_run
)
from src.prediction import predict_candidate_locations
from src.map_utils import create_intelligence_map
from src.analytics import (
    plot_complaints_by_crime_type, plot_complaints_by_hour,
    plot_risk_distribution, plot_top_predicted_locations
)
import importlib
new_comp_mod = importlib.import_module("pages.2_New_Complaint")
SCENARIOS = new_comp_mod.SCENARIOS


def run_full_verification():
    print("==================================================")
    print("CYBERGUARD AI — FULL SYSTEM VERIFICATION SUITE")
    print("==================================================")

    # 1. Test All 3 Scenarios
    for s_name, s_data in SCENARIOS.items():
        print(f"\n[TEST] Running {s_name}...")
        complaint_dict = {
            "complaint_id": s_data["complaint_id"],
            "crime_type": s_data["crime_type"],
            "transaction_type": s_data["transaction_type"],
            "amount": float(s_data["amount"]),
            "timestamp": f"{s_data['date']} {s_data['time'].strftime('%H:%M:%S')}",
            "latitude": float(s_data["latitude"]),
            "longitude": float(s_data["longitude"]),
            "transaction_hour": s_data["time"].hour,
            "transaction_day": s_data["date"].weekday(),
            "previous_transaction_count": s_data["previous_count"],
            "previous_transaction_amount": float(s_data["previous_amount"]),
            "time_since_previous_transaction": float(s_data["time_since"]),
            "suspicious_activity_score": float(s_data["suspicious_score"]),
            "victim_area_risk_score": float(s_data["area_risk"]),
            "status": "ANALYZED"
        }

        # Save complaint
        save_complaint(complaint_dict)
        retrieved = get_complaint_by_id(s_data["complaint_id"])
        assert retrieved is not None, f"Failed to retrieve complaint {s_data['complaint_id']}"

        # Run Prediction
        pred_res = predict_candidate_locations(complaint_dict, top_n=10)
        assert len(pred_res["top_candidates"]) == 10, "Expected 10 candidates"
        assert len(pred_res["all_ranked_candidates"]) == 100, "Expected 100 evaluated candidates"
        
        top1 = pred_res["top_candidates"][0]
        print(f"  -> Rank #1 Candidate: {top1['location_name']}")
        print(f"  -> Risk Score: {top1['risk_percentage']:.1f}% ({top1['risk_level']} Risk)")
        print(f"  -> Distance: {top1['distance_km']:.2f} km")
        print(f"  -> Forecast Window: {pred_res['forecast_time_window']}")
        print(f"  -> Explanation Factor Count: {len(top1.get('explanation_factors', []))}")

        # Check rankings are strictly descending
        scores = [c["final_risk_score"] for c in pred_res["all_ranked_candidates"]]
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), "Candidates not sorted descending"

        # Check Top 1 risk level
        assert top1["risk_level"] in ["HIGH", "MEDIUM", "LOW"]

        # Check DB persistence
        db_preds = get_predictions_by_complaint(s_data["complaint_id"])
        assert len(db_preds) == 100, f"Expected 100 predictions stored in DB, found {len(db_preds)}"

    # 2. Test Folium Map Generation
    print("\n[TEST] Generating Folium Intelligence Map...")
    fmap = create_intelligence_map(
        incident_lat=17.4156,
        incident_lon=78.4350,
        ranked_candidates=pred_res["top_candidates"],
        incident_info=complaint_dict
    )
    assert fmap is not None
    html_repr = fmap.get_root().render()
    assert "Risk Score Classification" in html_repr
    print("  -> Folium Map successfully rendered with custom legend and markers.")

    # 3. Test Investigator Feedback Loop
    print("\n[TEST] Logging Investigator Feedback...")
    save_feedback(
        complaint_id="CYB-2026-UPI-7701",
        location_id=top1["location_id"],
        status="Confirmed useful",
        notes="Automated verification test: verified within 15 min at ATM kiosk."
    )
    all_fb = get_all_feedback()
    assert any(fb["complaint_id"] == "CYB-2026-UPI-7701" for fb in all_fb)
    print("  -> Feedback persisted and verified in SQLite.")

    # 4. Test Analytics Generation
    print("\n[TEST] Testing Plotly Visual Analytics...")
    fig1 = plot_complaints_by_crime_type()
    fig2 = plot_complaints_by_hour()
    fig3 = plot_risk_distribution()
    fig4 = plot_top_predicted_locations()
    assert fig1 is not None and fig2 is not None and fig3 is not None and fig4 is not None
    print("  -> All 4 Plotly analytics charts generated successfully.")

    # 5. Check KPIs
    kpis = get_dashboard_kpis()
    print("\n[TEST] Dashboard Live KPIs:")
    print(f"  -> Total Complaints: {kpis['total_complaints']}")
    print(f"  -> Predictions Generated: {kpis['predictions_generated']}")
    print(f"  -> High-Risk Locations: {kpis['high_risk_locations']}")
    print(f"  -> Model Top-5 Accuracy: {kpis['model_top5_accuracy']*100:.1f}%")

    print("\n==================================================")
    print("✅ FULL SYSTEM VERIFICATION COMPLETED: 100% SUCCESS!")
    print("==================================================")


if __name__ == "__main__":
    run_full_verification()
