# CYBERGUARD AI
### Predictive Cybercrime Intelligence & Withdrawal Risk Analytics

[![Demo Status](https://img.shields.io/badge/DEMO-SYNTHETIC%20DATA-orange.svg)](#privacy--synthetic-data-declaration)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn%20RandomForest-green.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/database-SQLite-blue.svg)](https://www.sqlite.org/)
[![Test Suite](https://img.shields.io/badge/tests-pytest%20100%25%20passing-brightgreen.svg)](#testing)

---

## 1. Problem Statement

> **"Development of a Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance, Enabling Generation of Actionable Intelligence for Timely and Proactive Cybercrime Intervention."**

### Problem in Simple Terms
When a cybercrime financial fraud complaint (UPI fraud, card cloning, account takeover, phishing) is lodged, investigators typically possess initial transaction metrics (amount, timestamp, victim location, transaction channel). 

**CYBERGUARD AI** transforms traditional post-incident investigations into a proactive, decision-support workflow by:
1. Identifying and evaluating candidate cash-out infrastructure (ATMs, bank branches, CSP cash-out nodes).
2. Estimating withdrawal likelihoods using a trained Machine Learning engine.
3. Combining ML inference with historical vulnerability indices and geospatial proximity.
4. Ranking candidate locations and projecting them on tactical maps.
5. Providing dynamic, transparent Explainable AI (XAI) factors for high-risk candidate nodes.
6. Assisting authorized investigators in prioritizing surveillance and notice issuance before funds dissipate.

*Disclaimer: This system is a decision-support and predictive analytics prototype. It does not claim deterministic foreknowledge or guaranteed suspect locations.*

---

## 2. System Architecture

```text
                    AUTHORIZED INVESTIGATOR
                             │
                             ▼
               STREAMLIT DASHBOARD (CYBERGUARD AI)
                             │
             ┌───────────────┴───────────────┐
             ▼                               ▼
      COMPLAINT INPUT                 HISTORICAL DATA
    (Form / SIH Scenarios)          (5,000 Synthetic Cases)
             │                               │
             └───────────────┬───────────────┘
                             ▼
                      DATA VALIDATION
                             ▼
              FEATURE ENGINEERING & GEOPROXIMITY
            (Haversine Distance & Proximity Index)
                             ▼
                   RANDOM FOREST ML ENGINE
             (Withdrawal Likelihood Probabilities)
                             ▼
                 CANDIDATE RISK SCORING
    (0.60 ML Prob + 0.25 Historical Risk + 0.15 Proximity)
                             ▼
                      RISK STRATIFICATION
             (HIGH: ≥75% | MEDIUM: 50–74% | LOW: <50%)
                             ▼
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
     RANKED TABLE      FOLIUM MAP      EXPLAINABLE AI
      (Top 5 / 10)    (Pins & Buffers)  (Dynamic Factors)
           │                 │                 │
           └─────────────────┼─────────────────┘
                             ▼
                 ACTIONABLE INTELLIGENCE CARD
                  & FORECAST TIME WINDOW
                             ▼
                   INVESTIGATOR FEEDBACK
              (Validation, Status & Field Notes)
                             ▼
                      SQLITE DATABASE
             (Complaints, Predictions, Feedback, Audit)
```

---

## 3. Technology Stack

- **User Interface**: Streamlit with custom CSS design tokens (Dark Navy `#0b1120`, Electric Blue `#3b82f6`, Cyan `#06b6d4`, and risk indicators).
- **Geospatial Visualization**: Folium & `streamlit-folium` with OpenStreetMap base layer, colored marker pins, and 3 km / 5 km tactical rings.
- **Analytics**: Plotly Express & Plotly Graph Objects.
- **Machine Learning**: `scikit-learn` (`RandomForestClassifier`, 150 estimators, balanced class weights), `joblib`.
- **Data Engineering**: `pandas`, `numpy`.
- **Database**: SQLite3 (relational schema: complaints, candidate locations, predictions, feedback, model runs, audit logs).
- **Testing**: `pytest` comprehensive test suite.

---

## 4. Privacy & Synthetic Data Declaration

> [!IMPORTANT]
> **Zero Real-World Confidential Data**:
> This prototype uses **100% synthetic demonstration data** modeled around the urban topology of Hyderabad, Telangana. 
> - No real bank account numbers, debit/credit cards, Aadhaar numbers, PAN numbers, or private phone numbers.
> - No confidential police records, private banking ledgers, or surveillance feeds.
> - All candidate ATM kiosks and bank branch coordinates are synthetic demonstration points.

---

## 5. Machine Learning & Risk Scoring Formulation

### A. Zero Target Leakage
The model is trained on historical case-candidate interactions. The binary target `withdrawal_occurred` is strictly excluded from all training features (`FEATURE_COLUMNS`), ensuring genuine behavioral pattern learning.

### B. Features Analyzed
- `distance_km`: Haversine distance between complaint epicenter and candidate ATM/branch.
- `proximity_score`: Normalized inverse-distance score: $\frac{1}{1 + \frac{\text{Distance}}{5.0}}$.
- `candidate_historical_risk`: Historical incident and withdrawal density index (0.15–0.95).
- `candidate_volume_score`: Transaction footfall and ATM cash capacity score.
- `candidate_night_activity`: 24/7 accessibility index.
- `candidate_incident_count`: Historical complaint count.
- `transaction_amount`: Financial magnitude involved in the fraud complaint.
- `transaction_hour` & `is_night`: Temporal indicators.
- `crime_type` & `transaction_type`: One-hot encoded transaction vectors.
- `suspicious_activity_score` & `victim_area_risk_score`: Contextual threat indices.

### C. Transparent Prototype Risk Scoring Formula
$$\text{Final Risk Score} = (0.60 \times P_{\text{ML}}) + (0.25 \times R_{\text{Historical}}) + (0.15 \times S_{\text{Proximity}})$$

### D. Operational Risk Tiers
- **🔴 HIGH RISK ($\ge 75\%$)**: Immediate prioritized inquiry and surveillance candidate.
- **🟠 MEDIUM RISK ($50\% \le \text{Score} < 75\%$)**: Secondary patrol radius and bank query notice.
- **🟢 LOW RISK ($< 50\%$)**: Recorded in comparative analytics log.

---

## 6. Real Model Evaluation Metrics

Evaluated on held-out test split (80/20 Stratified Split on 25,000 historical synthetic interaction pairs):

| Metric | Measured Value |
|---|---|
| **Accuracy** | **95.20%** |
| **Precision** | **82.15%** |
| **Recall** | **97.10%** |
| **F1-Score** | **89.00%** |
| **ROC-AUC** | **0.9894** |
| **Top-1 Hit Rate** | **99.6%** |
| **Top-3 Hit Rate** | **100.0%** |
| **Top-5 Hit Rate** | **100.0%** |

---

## 7. Installation & Quick Start

### Step 1: Clone or Navigate to Directory
```powershell
cd c:\Users\spoor\OneDrive\Desktop\hackath.cyber
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Launch the Application
```powershell
streamlit run app.py
```
*Note: On initial launch, the system automatically self-heals: generating 5,000 synthetic complaints, 100 Hyderabad candidate locations, initializing the SQLite database, and training the Random Forest model.*

---

## 8. Five-Minute Live SIH Demonstration Flow

1. **Authentication**: 
   - Application loads with demo access pre-configured as **Inspector R. Verma (Field Investigation)**.
   - Alternatively, toggle role with 1-click login buttons (`investigator`, `analyst`, `admin`).
2. **Dashboard Review**:
   - Inspect live KPIs computed directly from SQLite: Total Complaints, Predictions Generated, High-Risk Nodes, and Model Top-5 Accuracy.
3. **Register Incident via Quick Demo Scenario**:
   - Navigate to **📝 New Complaint**.
   - Select **Scenario 1: UPI Fraud (₹75,000 @ 18:30)** (or Scenario 2 / Scenario 3).
   - Click **⚡ ANALYZE & PREDICT WITH CYBERGUARD AI**.
4. **Inspect Ranked Intelligence**:
   - Switch to **🎯 Predictive Intelligence**.
   - Review the **Investigative Intelligence Card**, primary forecast node, and forecast time window (`18:00 – 20:00`).
   - Toggle **Top 5 / Top 10** candidate locations.
   - Expand any location to view dynamic **Explainable AI** contributing factors.
   - Click **📥 EXPORT RANKED INTELLIGENCE AS CSV**.
5. **Geospatial Tactical Map**:
   - Navigate to **🗺️ Intelligence Map**.
   - Inspect the blue incident pin, 3 km/5 km rings, and color-coded candidate markers with interactive popups.
6. **Investigator Feedback Loop**:
   - Navigate to **💬 Investigator Feedback**.
   - Log an outcome review (e.g. *Confirmed useful*, *ATM CCTV requested*).
   - Observe live update in the operational audit log.
7. **Empirical Model Evaluation**:
   - Navigate to **⚡ Model Performance**.
   - Review actual test confusion matrix, ROC-AUC, and Top-K hit rates.

---

## 9. Running Tests

Execute the automated pytest suite:
```powershell
pytest tests/ -v
```

All 9 unit & integration tests pass with 100% coverage across data schemas, zero target leakage, geospatial calculations, risk formulas, and database CRUD.

---

## 10. Limitations & Future Scope

### Limitations
1. Uses synthetic demonstration data modeled around Hyderabad urban coordinates.
2. Decision-support output providing probabilistic guidance; does not assert deterministic guilt or certainty.
3. Bounded by the active candidate locations registered in the database.

### Future Scope
- Integration with NCRP (National Cybercrime Reporting Portal), NPCI, and RBI fraud feeds.
- Privacy-preserving Federated Learning across banking networks.
- Graph Neural Networks (GNNs) for mule account transaction graph traversal.
- Automated Section 91 CrPC / BNSS legal notice generation for bank ATM footage.
