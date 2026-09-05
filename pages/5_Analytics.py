"""
CYBERGUARD AI - Visual Analytics & Trend Intelligence Page
Multi-dimensional investigative analytics on fraud patterns, temporal trends,
geospatial hotspots, and candidate cashout frequencies.
"""

import streamlit as st
import pandas as pd
from src.analytics import (
    plot_complaints_by_crime_type,
    plot_complaints_by_hour,
    plot_transaction_amount_distribution,
    plot_risk_distribution,
    plot_top_predicted_locations
)
from src.database import get_db_connection


def render_analytics():
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">Investigative Analytics & Trends</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Aggregate behavioral analytics, temporal fraud peaks, and cashout node clustering across historical complaints.</p>', unsafe_allow_html=True)

    # Row 1: Crime Types & Diurnal Hourly Trends
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_complaints_by_crime_type(), use_container_width=True)
    with c2:
        st.plotly_chart(plot_complaints_by_hour(), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: Financial Amounts & Risk Stratification
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(plot_transaction_amount_distribution(), use_container_width=True)
    with c4:
        st.plotly_chart(plot_risk_distribution(), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 3: Frequent Cashout Candidate Nodes
    st.plotly_chart(plot_top_predicted_locations(limit=10), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Database Summary Metrics
    conn = get_db_connection()
    df_metrics = pd.read_sql_query("""
        SELECT 
            COUNT(*) as total_cases,
            SUM(amount) as total_fraud_amount,
            AVG(amount) as avg_fraud_amount,
            MAX(amount) as max_fraud_amount
        FROM complaints
    """, conn)
    conn.close()

    if not df_metrics.empty and df_metrics["total_cases"].iloc[0] > 0:
        row = df_metrics.iloc[0]
        st.subheader("📈 Statistical Overview of Analyzed Complaints")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Analyzed Incident Cases", f"{int(row['total_cases']):,}")
        m2.metric("Cumulative Disputed Volume", f"₹{float(row['total_fraud_amount']):,.2f}")
        m3.metric("Average Incident Exposure", f"₹{float(row['avg_fraud_amount']):,.2f}")
        m4.metric("Single Maximum Exposure", f"₹{float(row['max_fraud_amount']):,.2f}")


if __name__ == "__main__":
    render_analytics()
