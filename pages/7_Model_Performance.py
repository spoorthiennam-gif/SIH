"""
CYBERGUARD AI - Model Performance & Validation Metrics Page
Displays genuine evaluation metrics from the trained RandomForestClassifier,
including Top-K ranking accuracy, confusion matrix, ROC-AUC, and feature importances.
"""

import streamlit as st
import json
import os
import pandas as pd

from src.database import get_latest_model_run
from src.analytics import plot_confusion_matrix, plot_feature_importances

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


def render_model_performance():
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">Machine Learning Model Performance</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Empirical evaluation metrics and Top-K ranking verification calculated strictly on held-out test splits.</p>', unsafe_allow_html=True)

    meta_file = os.path.join(MODEL_DIR, "model_metadata.json")
    metadata = {}
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            metadata = json.load(f)
    else:
        db_run = get_latest_model_run()
        if db_run:
            metadata = db_run

    if not metadata:
        st.warning("No model metadata found. Please initialize and train the prediction model.")
        return

    # Model Overview Banner
    st.markdown(f"""
    <div class="intel-card" style="margin-top: 0; padding: 16px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <b style="color: #38bdf8; font-size: 15px;">Active Model:</b> {metadata.get('model_name', 'RandomForestClassifier')}<br>
                <span style="font-size: 12px; color: #94a3b8;"><b>Trained At:</b> {metadata.get('training_timestamp', 'N/A')[:19]}</span>
            </div>
            <div style="text-align: right; font-size: 12px; color: #94a3b8;">
                <b>Total Dataset:</b> {metadata.get('dataset_size', 0):,} records<br>
                <b>Train / Test Split:</b> {metadata.get('train_size', 0):,} train / {metadata.get('test_size', 0):,} test (80/20 Stratified)
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Primary Classification Metrics
    st.subheader("🎯 Primary Classification Metrics")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Accuracy", f"{metadata.get('accuracy', 0.0)*100:.2f}%")
    m2.metric("Precision", f"{metadata.get('precision', 0.0)*100:.2f}%")
    m3.metric("Recall", f"{metadata.get('recall', 0.0)*100:.2f}%")
    m4.metric("F1-Score", f"{metadata.get('f1', 0.0)*100:.2f}%")
    m5.metric("ROC-AUC", f"{metadata.get('roc_auc', 0.0):.4f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Top-K Candidate Ranking Evaluation
    st.subheader("🏆 Top-K Geospatial Ranking Evaluation")
    st.markdown("""
    *Top-K evaluation measures whether the actual synthetic cash-withdrawal location appears within the model's highest-ranked candidate locations for a given complaint.*
    """)

    top1 = metadata.get("top1", 0.0) * 100
    top3 = metadata.get("top3", 0.0) * 100
    top5 = metadata.get("top5", 0.0) * 100

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="kpi-card" style="text-align: center;">
            <div class="kpi-label">Top-1 Hit Rate</div>
            <div class="kpi-value" style="color: #38bdf8;">{top1:.1f}%</div>
            <div class="kpi-delta">Actual location was #1 rank</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card" style="text-align: center;">
            <div class="kpi-label">Top-3 Hit Rate</div>
            <div class="kpi-value" style="color: #06b6d4;">{top3:.1f}%</div>
            <div class="kpi-delta">Actual location in Top-3 ranks</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card" style="text-align: center;">
            <div class="kpi-label">Top-5 Hit Rate</div>
            <div class="kpi-value" style="color: #10b981;">{top5:.1f}%</div>
            <div class="kpi-delta">Actual location in Top-5 ranks</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Confusion Matrix & Feature Importances
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        cm = metadata.get("confusion_matrix")
        if cm:
            st.plotly_chart(plot_confusion_matrix(cm), use_container_width=True)
        else:
            st.info("Confusion matrix data unavailable.")

    with c_col2:
        feat_imp = metadata.get("feature_importances", {})
        if feat_imp:
            st.plotly_chart(plot_feature_importances(feat_imp, top_n=8), use_container_width=True)
        else:
            st.info("Feature importance data unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Mandatory Disclaimer
    st.markdown("""
    <div class="disclaimer-box">
        <b>⚠️ ETHICAL DISCLAIMER ON SYNTHETIC PERFORMANCE METRICS:</b><br>
        Model metrics are calculated strictly on synthetic demonstration data generated to emulate urban financial fraud distributions in Hyderabad.
        These statistics demonstrate mathematical and architectural feasibility and should NOT be interpreted as real-world law-enforcement performance.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_model_performance()
