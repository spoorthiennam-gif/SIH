"""
CYBERGUARD AI - Predictive Intelligence Page
Ranks candidate withdrawal locations, displays decision-support intelligence summary,
explains feature factor contributions, and provides CSV export.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import get_recent_complaints, get_predictions_by_complaint
from src.prediction import predict_candidate_locations


def render_predictive_intelligence():
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">Predictive Intelligence & Location Ranking</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Decision-support risk ranking of candidate cash-withdrawal nodes based on ML inference and geospatial scoring.</p>', unsafe_allow_html=True)

    # Check session state or allow selecting from complaints
    curr_pred = st.session_state.get("current_prediction")
    curr_complaint = st.session_state.get("current_complaint")

    # If no prediction in session, let user select from registered complaints
    if not curr_pred or not curr_complaint:
        st.info("No active complaint analysis selected in session memory.")
        recent_complaints = get_recent_complaints(limit=10)
        if recent_complaints:
            cid_options = [f"{c['complaint_id']} — {c['crime_type']} (₹{c['amount']:,.0f})" for c in recent_complaints]
            selected_option = st.selectbox("Select a registered complaint to analyze/view:", cid_options)
            sel_cid = selected_option.split(" — ")[0]
            sel_comp = next(c for c in recent_complaints if c["complaint_id"] == sel_cid)
            
            if st.button("Load & Compute Intelligence for Selected Complaint"):
                with st.spinner("Analyzing candidate locations..."):
                    pred_res = predict_candidate_locations(sel_comp, top_n=10)
                    st.session_state["current_complaint"] = sel_comp
                    st.session_state["current_prediction"] = pred_res
                    st.rerun()
            return
        else:
            st.warning("No complaints exist in the database yet. Please register a complaint first.")
            return

    # Top-K toggle: Top 5 vs Top 10
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"### Incident Reference: `{curr_complaint['complaint_id']}` ({curr_complaint['crime_type']} — ₹{float(curr_complaint['amount']):,.2f})")
    with col_t2:
        top_k = st.radio("Candidate Pool View:", [5, 10], index=0, horizontal=True)

    candidates = curr_pred["top_candidates"][:top_k]
    intel_summary = curr_pred["intelligence_summary"]

    # 1. Actionable Intelligence Summary Card
    st.markdown(f"""
    <div class="intel-card">
        <div class="intel-card-header">
            <div>
                <span class="demo-badge">INVESTIGATIVE INTELLIGENCE CARD</span>
                <h3 style="margin: 4px 0 0 0; color: #ffffff;">Primary Forecast Node: {intel_summary['top_candidate_name']}</h3>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Confidence Score</div>
                <div style="font-size: 28px; font-weight: 800; color: {intel_summary['top_risk_color']};">{intel_summary['top_risk_percentage']:.1f}%</div>
                <span class="{ 'badge-high' if intel_summary['top_risk_level'] == 'HIGH' else ('badge-medium' if intel_summary['top_risk_level'] == 'MEDIUM' else 'badge-low') }">
                    {intel_summary['top_risk_level']} RISK
                </span>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 16px;">
            <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #94a3b8;">DISTANCE FROM INCIDENT</div>
                <div style="font-size: 18px; font-weight: 700; color: #ffffff;">{intel_summary['top_distance_km']:.2f} km</div>
            </div>
            <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #94a3b8;">FORECAST TIME RISK WINDOW</div>
                <div style="font-size: 15px; font-weight: 700; color: #38bdf8;">{intel_summary['forecast_time_window']}</div>
                <div style="font-size: 10px; color: #64748b;">Forecast — not a guaranteed event time</div>
            </div>
            <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #94a3b8;">RECOMMENDED PRIORITY</div>
                <div style="font-size: 15px; font-weight: 700; color: #fbbf24;">{intel_summary['recommended_priority']}</div>
            </div>
        </div>
        <div style="font-size: 12px; color: #cbd5e1; line-height: 1.6;">
            <b>Primary Ranking Factors:</b><br>
            <pre style="background: transparent; border: none; color: #cbd5e1; font-family: inherit; font-size: 12px; margin: 4px 0 0 0; white-space: pre-wrap;">{intel_summary['top_explanation']}</pre>
        </div>
        <div class="disclaimer-box" style="margin-top: 15px;">
            <b>Decision-support output only.</b> Investigators must independently verify information and follow applicable legal and departmental procedures.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Ranked Candidate Locations Table
    st.subheader(f"📊 Ranked Candidate Locations (Top {top_k})")
    table_rows = []
    for c in candidates:
        table_rows.append({
            "Rank": f"#{c['rank']}",
            "Location Name": c["location_name"],
            "Location Type": c.get("location_type", "ATM"),
            "Final Risk Score": f"{c['risk_percentage']:.1f}%",
            "Risk Level": c["risk_level"],
            "Distance": f"{c['distance_km']:.2f} km",
            "Proximity Index": f"{c['proximity_score']:.2f}",
            "Historical Risk": f"{c['historical_risk']:.2f}",
            "ML Probability": f"{c['ml_probability']*100:.1f}%"
        })
    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # CSV Export
    csv_data = df_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 EXPORT RANKED INTELLIGENCE AS CSV",
        data=csv_data,
        file_name=f"cyberguard_predictions_{curr_complaint['complaint_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Dynamic Explainable AI Factor Breakdown
    st.subheader("🔍 Explainable AI: Why Candidate Locations Ranked Highly")
    st.markdown("Detailed breakdown of algorithmic contributions for each top-ranked candidate location:")

    for c in candidates[:5]:
        with st.expander(f"Rank #{c['rank']}: {c['location_name']} — {c['risk_percentage']:.1f}% {c['risk_level']} Risk ({c['distance_km']:.2f} km)"):
            c_col1, c_col2 = st.columns([2, 1])
            with c_col1:
                st.markdown("<b>Dynamic Contributing Factors:</b>", unsafe_allow_html=True)
                for f in c.get("explanation_factors", []):
                    st.markdown(f"- {f}")
                st.markdown(f"<b>Recommended Action:</b> `{c.get('recommended_priority', 'ROUTINE')}`", unsafe_allow_html=True)
            with c_col2:
                st.markdown(f"""
                <div style="background: rgba(15,23,42,0.8); border: 1px solid #334155; padding: 12px; border-radius: 8px; font-size: 12px;">
                    <div><b>ML Probability:</b> {c['ml_probability']*100:.1f}% (Weight: 60%)</div>
                    <div><b>Historical Risk:</b> {c['historical_risk']:.2f} (Weight: 25%)</div>
                    <div><b>Proximity Score:</b> {c['proximity_score']:.2f} (Weight: 15%)</div>
                    <hr style="margin: 6px 0; border-top: 1px solid #334155;">
                    <div style="color: {c['risk_color']}; font-weight: bold;">Final Combined Score: {c['risk_percentage']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_predictive_intelligence()
