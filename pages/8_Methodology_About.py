"""
CYBERGUARD AI - Methodology & Technical Documentation Page
Provides architectural flowchart, mathematical formulas, operational limitations, and future scope.
"""

import streamlit as st


def render_methodology_about():
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">System Methodology & Architectural Framework</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">End-to-end predictive analytics framework for cybercrime financial complaints to forecast candidate cash withdrawal locations.</p>', unsafe_allow_html=True)

    # 1. Pipeline Flowchart
    st.subheader("🔄 End-to-End Predictive Analytics Pipeline")
    st.markdown("""
    ```text
    COMPLAINT RECEIVED (FIR / Portal / Victim Report)
           │
           ▼
    INPUT VALIDATION & DATA SANITIZATION (Strict range, type, and geographic boundary checks)
           │
           ▼
    SPATIOTEMPORAL FEATURE ENGINEERING (Haversine distance, normalized proximity, diurnal flags)
           │
           ▼
    CANDIDATE CASH-OUT POOL EVALUATION (100 ATM kiosks, bank branches, CSP cashout points)
           │
           ▼
    MACHINE LEARNING INFERENCE ENGINE (RandomForestClassifier estimating withdrawal likelihood)
           │
           ▼
    MULTI-FACTOR PROTOTYPE RISK SCORING (0.60 ML Prob + 0.25 Hist Risk + 0.15 Proximity Score)
           │
           ▼
    RANKING & STRATIFICATION (Top 5 & Top 10 candidate nodes ordered by risk percentage)
           │
           ▼
    GEOSPATIAL MAPPING & TACTICAL BUFFERING (Interactive Folium visualization with 3km/5km rings)
           │
           ▼
    ACTIONABLE INTELLIGENCE GENERATION (Forecast time-risk windows & dynamic explainability)
           │
           ▼
    INVESTIGATOR FEEDBACK & SQLite PERSISTENCE (Human-in-the-loop efficacy validation and audit logging)
    ```
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Transparent Scoring Formula
    st.subheader("📐 Risk Scoring Formulation")
    st.markdown("""
    The prototype employs a transparent, multi-criteria risk scoring formulation:

    $$\\text{Final Risk Score} = (0.60 \\times P_{\\text{ML}}) + (0.25 \\times R_{\\text{Historical}}) + (0.15 \\times S_{\\text{Proximity}})$$

    Where:
    - **$P_{\\text{ML}}$**: Machine Learning probability derived from a Random Forest Classifier trained on complaint attributes, transaction amounts, temporal patterns, and location features.
    - **$R_{\\text{Historical}}$**: Location historical vulnerability score (0.15–0.95), reflecting past incident density, night activity, and transaction volume.
    - **$S_{\\text{Proximity}}$**: Normalized geographic proximity score computed via Haversine distance:
      $$S_{\\text{Proximity}} = \\frac{1}{1 + \\frac{\\text{Distance (km)}}{5.0}}$$
    
    **Risk Categorization Thresholds:**
    - **HIGH RISK (Red):** Score $\\ge 75\\%$ &rarr; Immediate surveillance and tactical inquiry recommended.
    - **MEDIUM RISK (Orange):** $50\\% \\le$ Score $< 75\\%$ &rarr; Secondary sweep and bank inquiry notice.
    - **LOW RISK (Green):** Score $< 50\\%$ &rarr; Standard operational log recording.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Limitations & Constraints
    st.subheader("⚠️ System Constraints & Ethical Boundaries")
    st.markdown("""
    1. **Synthetic Data**: All complaints, amounts, coordinates, and candidate locations are 100% synthetic demonstration data inspired by Hyderabad, Telangana. Zero real PII, Aadhaar, PAN, or confidential bank logs are processed.
    2. **Probabilistic Decision Support**: Output rankings reflect probabilistic likelihoods, not deterministic guarantees. The system does NOT state "the suspect will be here".
    3. **Operational Discretion**: Field deployment remains subject to statutory legal mandates, judicial warrants, and senior investigative oversight.
    4. **Geographic Coverage**: Location rankings are bounded by the candidate locations present in the active demonstration database.
    5. **No Autonomous Action**: The system does not execute automated enforcement, dispatch, or accusations.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Future Scope & Roadmap
    st.subheader("🚀 Roadmap for Production Law Enforcement Deployment")
    st.markdown("""
    - **Authorized Institutional Feeds**: Integration with National Cybercrime Reporting Portal (NCRP), I4C, NPCI UPI logs, and RBI fraud registries via encrypted government APIs.
    - **Privacy-Preserving Computation**: Implementation of Federated Learning and Differential Privacy to train on multi-bank ledger patterns without exposing customer records.
    - **Advanced Spatiotemporal Modeling**: Graph Neural Networks (GNNs) to model mule account financial transaction graphs and temporal cashout corridors.
    - **Automated Bank Notice Generation**: Direct generation of Section 91 CrPC / BNSS inquiries for ATM CCTV footage within predicted high-risk windows.
    - **Continuous Active Learning**: Automated model weight calibration based on validated investigator feedback.
    """)


if __name__ == "__main__":
    render_methodology_about()
