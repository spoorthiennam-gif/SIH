"""
CYBERGUARD AI - New Complaint Registration & Demo Scenarios Page
Allows authorized investigators to register cybercrime complaints with strict validation
and provides one-click SIH Demo Scenarios for fast live demonstration.
"""

import streamlit as st
from datetime import datetime, date, time
import random

from src.database import save_complaint
from src.prediction import predict_candidate_locations

# 3 SIH Demo Scenarios
SCENARIOS = {
    "Scenario 1: UPI Fraud (₹75,000 @ 18:30)": {
        "complaint_id": "CYB-2026-UPI-7701",
        "crime_type": "UPI Fraud",
        "transaction_type": "UPI",
        "amount": 75000.0,
        "date": date(2026, 9, 4),
        "time": time(18, 30),
        "latitude": 17.4156,
        "longitude": 78.4350,
        "location_label": "Banjara Hills Corridor, Hyderabad",
        "previous_count": 3,
        "previous_amount": 18000.0,
        "time_since": 45.0,
        "suspicious_score": 0.82,
        "area_risk": 0.68
    },
    "Scenario 2: Card Fraud (₹35,000 @ 22:15)": {
        "complaint_id": "CYB-2026-CRD-8824",
        "crime_type": "Card Fraud",
        "transaction_type": "ATM",
        "amount": 35000.0,
        "date": date(2026, 9, 4),
        "time": time(22, 15),
        "latitude": 17.4339,
        "longitude": 78.5015,
        "location_label": "Secunderabad Station Hub, Hyderabad",
        "previous_count": 1,
        "previous_amount": 5000.0,
        "time_since": 120.0,
        "suspicious_score": 0.74,
        "area_risk": 0.75
    },
    "Scenario 3: Account Takeover (₹1,20,000 @ 14:20)": {
        "complaint_id": "CYB-2026-ATO-9931",
        "crime_type": "Account Takeover",
        "transaction_type": "IMPS",
        "amount": 120000.0,
        "date": date(2026, 9, 4),
        "time": time(14, 20),
        "latitude": 17.4483,
        "longitude": 78.3915,
        "location_label": "Hitec City / Madhapur Cyber Cluster",
        "previous_count": 4,
        "previous_amount": 42000.0,
        "time_since": 25.0,
        "suspicious_score": 0.91,
        "area_risk": 0.72
    }
}


def render_new_complaint():
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">Register Cybercrime Complaint</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Enter verified FIR / portal incident details or load a pre-configured SIH demonstration scenario.</p>', unsafe_allow_html=True)

    # Demo Scenario Quick Loader Box
    st.markdown("""
    <div class="scenario-box">
        <b style="color: #38bdf8;">⚡ FAST DEMONSTRATION SELECTOR:</b> Load synthetic scenarios calibrated for live SIH demonstration.
    </div>
    """, unsafe_allow_html=True)

    scenario_choice = st.selectbox(
        "Select Demo Scenario (Auto-populates fields):",
        ["-- Manual Input / Custom Incident --"] + list(SCENARIOS.keys()),
        index=1 if "scenario_index" not in st.session_state else st.session_state["scenario_index"]
    )

    defaults = None
    if scenario_choice in SCENARIOS:
        defaults = SCENARIOS[scenario_choice]

    # Initialize or populate form defaults
    cid_default = defaults["complaint_id"] if defaults else f"CYB-2026-{random.randint(10000, 99999)}"
    ctype_default = defaults["crime_type"] if defaults else "UPI Fraud"
    ttype_default = defaults["transaction_type"] if defaults else "UPI"
    amount_default = float(defaults["amount"]) if defaults else 50000.0
    date_default = defaults["date"] if defaults else date.today()
    time_default = defaults["time"] if defaults else time(18, 0)
    lat_default = float(defaults["latitude"]) if defaults else 17.4100
    lon_default = float(defaults["longitude"]) if defaults else 78.4500
    prev_cnt_default = int(defaults["previous_count"]) if defaults else 1
    prev_amt_default = float(defaults["previous_amount"]) if defaults else 10000.0
    time_since_default = float(defaults["time_since"]) if defaults else 60.0
    susp_default = float(defaults["suspicious_score"]) if defaults else 0.75
    area_default = float(defaults["area_risk"]) if defaults else 0.65

    with st.form("new_complaint_form"):
        st.subheader("1. Complaint & Incident Identity")
        c1, c2, c3 = st.columns(3)
        with c1:
            complaint_id = st.text_input("Complaint / Incident ID *", value=cid_default)
        with c2:
            crime_types = ["UPI Fraud", "Card Fraud", "Account Takeover", "Phishing", "Other Financial Fraud"]
            crime_type = st.selectbox("Cybercrime Type *", crime_types, index=crime_types.index(ctype_default) if ctype_default in crime_types else 0)
        with c3:
            tx_types = ["UPI", "ATM", "POS", "IMPS", "NEFT", "Other"]
            transaction_type = st.selectbox("Transaction Channel *", tx_types, index=tx_types.index(ttype_default) if ttype_default in tx_types else 0)

        st.subheader("2. Financial & Temporal Information")
        f1, f2, f3 = st.columns(3)
        with f1:
            amount = st.number_input("Transaction Amount (₹) *", min_value=1.0, max_value=10000000.0, value=amount_default, step=1000.0)
        with f2:
            tx_date = st.date_input("Transaction Date *", value=date_default)
        with f3:
            tx_time = st.time_input("Transaction Time *", value=time_default)

        st.subheader("3. Incident Coordinates (Victim / Incident Location)")
        l1, l2, l3 = st.columns(3)
        with l1:
            latitude = st.number_input("Victim Latitude *", min_value=16.0, max_value=19.0, value=lat_default, format="%.5f")
        with l2:
            longitude = st.number_input("Victim Longitude *", min_value=77.0, max_value=80.0, value=lon_default, format="%.5f")
        with l3:
            st.info("💡 Hyderabad Region: Lat ~17.38°N, Lon ~78.48°E")

        st.subheader("4. Historical Context & Behavioral Indicators")
        h1, h2, h3 = st.columns(3)
        with h1:
            prev_tx_cnt = st.number_input("Previous Transactions (24h)", min_value=0, max_value=50, value=prev_cnt_default)
        with h2:
            prev_tx_amt = st.number_input("Previous Amount (₹)", min_value=0.0, max_value=1000000.0, value=prev_amt_default, step=5000.0)
        with h3:
            time_since = st.number_input("Minutes Since Last Activity", min_value=0.0, max_value=2880.0, value=time_since_default, step=5.0)

        b1, b2 = st.columns(2)
        with b1:
            susp_score = st.slider("Suspicious Activity Risk Score", min_value=0.0, max_value=1.0, value=susp_default, step=0.01)
        with b2:
            area_score = st.slider("Victim Area Environmental Risk Score", min_value=0.0, max_value=1.0, value=area_default, step=0.01)

        submit_predict = st.form_submit_button("⚡ ANALYZE & PREDICT WITH CYBERGUARD AI", use_container_width=True)

    if submit_predict:
        # Strict validation
        if not complaint_id or complaint_id.strip() == "":
            st.error("Error: Complaint ID is required.")
            return

        if amount <= 0:
            st.error("Error: Transaction amount must be positive.")
            return

        if not (16.0 <= latitude <= 19.0 and 77.0 <= longitude <= 80.0):
            st.error("Error: Coordinates must be within the demonstration region (Hyderabad metropolitan area).")
            return

        # Prepare payload
        timestamp_str = f"{tx_date} {tx_time.strftime('%H:%M:%S')}"
        complaint_dict = {
            "complaint_id": complaint_id.strip(),
            "crime_type": crime_type,
            "transaction_type": transaction_type,
            "amount": float(amount),
            "timestamp": timestamp_str,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "transaction_hour": tx_time.hour,
            "transaction_day": tx_date.weekday(),
            "previous_transaction_count": int(prev_tx_cnt),
            "previous_transaction_amount": float(prev_tx_amt),
            "time_since_previous_transaction": float(time_since),
            "suspicious_activity_score": float(susp_score),
            "victim_area_risk_score": float(area_score),
            "status": "ANALYZED"
        }

        with st.spinner("Executing geospatial risk engine & Random Forest inference..."):
            try:
                # Save complaint to database
                save_complaint(complaint_dict)

                # Run prediction
                pred_results = predict_candidate_locations(complaint_dict, top_n=10)

                # Store in session state for instant multi-page inspection
                st.session_state["current_complaint"] = complaint_dict
                st.session_state["current_prediction"] = pred_results

                st.success(f"✅ Prediction Completed Successfully for Complaint **{complaint_id}**!")
                st.balloons()

                st.info("👉 Switch to **Predictive Intelligence** or **Intelligence Map** to review ranked candidate locations and explainability summaries.")

                # Render Top-3 mini preview
                st.markdown("### 🏆 Immediate High-Probability Forecast Preview (Top 3 Candidates):")
                top_3 = pred_results["top_candidates"][:3]
                cols = st.columns(3)
                for idx, c in enumerate(top_3):
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="kpi-card" style="border-left: 4px solid {c['risk_color']};">
                            <span class="demo-badge" style="border-color: {c['risk_color']}; color: {c['risk_color']};">RANK #{c['rank']}</span>
                            <div style="font-weight: 700; color: #ffffff; margin-top: 6px;">{c['location_name']}</div>
                            <div style="color: {c['risk_color']}; font-size: 22px; font-weight: 800; margin: 4px 0;">{c['risk_percentage']:.1f}% Risk</div>
                            <div style="font-size: 12px; color: #94a3b8;">Distance: {c['distance_km']:.2f} km</div>
                            <div style="font-size: 12px; color: #94a3b8;">ML Prob: {c['ml_probability']*100:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Prediction Pipeline Error: {str(e)}")


if __name__ == "__main__":
    render_new_complaint()
