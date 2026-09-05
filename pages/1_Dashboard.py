"""
CYBERGUARD AI - Dashboard Page
Presents high-level KPIs, recent registered complaints, active high-risk withdrawal locations,
and summary risk stratification charts.
"""

import streamlit as st
import pandas as pd
from src.database import get_dashboard_kpis, get_recent_complaints, get_all_predictions
from src.analytics import plot_risk_distribution, plot_complaints_by_hour


def render_dashboard():
    # Header Banner
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">CYBERGUARD AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Predictive Cybercrime Intelligence & Withdrawal Risk Analytics</p>', unsafe_allow_html=True)

    # 1. Live KPI Cards (Dynamically computed from actual SQLite data)
    kpis = get_dashboard_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Complaints</div>
            <div class="kpi-value">{kpis['total_complaints']:,}</div>
            <div class="kpi-delta">Registered in system</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Predictions Generated</div>
            <div class="kpi-value">{kpis['predictions_generated']:,}</div>
            <div class="kpi-delta">Dynamic ML assessments</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">High-Risk Nodes</div>
            <div class="kpi-value">{kpis['high_risk_locations']}</div>
            <div class="kpi-delta">Historical index &ge; 0.70</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        top5_pct = kpis['model_top5_accuracy'] * 100
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Model Top-5 Accuracy</div>
            <div class="kpi-value">{top5_pct:.1f}%</div>
            <div class="kpi-delta">Verified test set hit-rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Charts Section
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.plotly_chart(plot_risk_distribution(), use_container_width=True)
    with col_chart2:
        st.plotly_chart(plot_complaints_by_hour(), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Recent Complaints Table
    st.subheader("📋 Recent Cybercrime Financial Complaints")
    recent = get_recent_complaints(limit=8)
    if recent:
        df_recent = pd.DataFrame(recent)
        display_df = df_recent[[
            "complaint_id", "crime_type", "transaction_type", "amount", "timestamp", "status"
        ]].copy()
        display_df.columns = ["Complaint ID", "Crime Type", "Tx Type", "Amount (₹)", "Date/Time", "Status"]
        display_df["Amount (₹)"] = display_df["Amount (₹)"].apply(lambda x: f"₹{x:,.2f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No complaints registered yet. Register a complaint on the 'New Complaint' page.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Current High-Risk Predictions
    st.subheader("⚠️ High-Risk Candidate Locations (Recent Predictions)")
    all_preds = get_all_predictions(limit=10)
    if all_preds:
        df_preds = pd.DataFrame(all_preds)
        # Filter High & Medium
        high_preds = df_preds[df_preds["final_risk_score"] >= 0.65].copy()
        if not high_preds.empty:
            disp_preds = high_preds[[
                "complaint_id", "location_name", "risk_level", "final_risk_score", "distance_km", "created_at"
            ]].copy()
            disp_preds.columns = ["Case Ref", "Candidate Location", "Risk Level", "Score", "Distance", "Timestamp"]
            disp_preds["Score"] = disp_preds["Score"].apply(lambda s: f"{s*100:.1f}%")
            disp_preds["Distance"] = disp_preds["Distance"].apply(lambda d: f"{d:.2f} km")
            st.dataframe(disp_preds, use_container_width=True, hide_index=True)
        else:
            st.info("Run predictions to view ranked high-risk candidates.")
    else:
        st.info("Run a prediction on the 'New Complaint' page to populate high-risk candidate intelligence.")

    # Legal Disclaimer
    st.markdown("""
    <div class="disclaimer-box">
        <b>⚖️ DECISION-SUPPORT PROTOCOL NOTICE:</b><br>
        CYBERGUARD AI produces probabilistic risk estimates derived from synthetic demonstration patterns.
        This system is engineered strictly for investigative decision-support and prioritization.
        It does not make deterministic claims or replace authorized human operational verification.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_dashboard()
