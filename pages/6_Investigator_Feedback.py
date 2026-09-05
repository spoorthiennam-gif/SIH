"""
CYBERGUARD AI - Investigator Feedback Loop Page
Enables authorized investigators to log outcome validation, field efficacy assessments,
and qualitative notes, persisting continuous human-in-the-loop audit data to SQLite.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from src.database import (
    save_feedback, get_all_feedback, get_recent_complaints,
    get_predictions_by_complaint, get_db_connection
)


def render_investigator_feedback():
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">Investigator Feedback & Validation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Human-in-the-loop evaluation: record field outcomes, CCTV verification, or patrol feedback to assess model decision support utility.</p>', unsafe_allow_html=True)

    # 1. Feedback Submission Form
    st.subheader("📝 Record Investigative Outcome Assessment")
    
    recent_complaints = get_recent_complaints(limit=20)
    if not recent_complaints:
        st.info("No complaints found in system database. Run predictions to log feedback.")
        return

    comp_options = [f"{c['complaint_id']} — {c['crime_type']} (₹{c['amount']:,.0f})" for c in recent_complaints]
    selected_comp_str = st.selectbox("Select Target Complaint Reference:", comp_options)
    selected_cid = selected_comp_str.split(" — ")[0]

    # Fetch predictions for this complaint
    preds = get_predictions_by_complaint(selected_cid)
    
    with st.form("feedback_entry_form"):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            if preds:
                loc_options = [f"Rank #{p['rank_order']} - {p['location_name']} ({p['risk_level']} - {p['final_risk_score']*100:.1f}%)" for p in preds[:10]]
                selected_loc_str = st.selectbox("Select Candidate Location Assessed:", loc_options)
                # find matching prediction record
                loc_idx = int(selected_loc_str.split("Rank #")[1].split(" - ")[0]) - 1
                pred_record = preds[loc_idx] if loc_idx < len(preds) else preds[0]
                loc_id = pred_record["location_id"]
                pred_id = pred_record.get("id")
            else:
                st.warning("No predictions currently persisted for this complaint. Run prediction first.")
                loc_id = "LOC_UNKNOWN"
                pred_id = None

        with f_col2:
            status_options = [
                "Confirmed useful",
                "Partially useful",
                "Not confirmed",
                "Insufficient information"
            ]
            feedback_status = st.selectbox("Operational Utility Status:", status_options)

        feedback_notes = st.text_area(
            "Investigative Field Notes / Observations (Optional):",
            placeholder="e.g., CCTV requisition sent to bank branch. Footage confirmed subject attempting withdrawal at ATM kiosk within predicted time window."
        )

        sub_btn = st.form_submit_button("💾 SUBMIT & PERSIST INVESTIGATOR FEEDBACK", use_container_width=True)

    if sub_btn:
        save_feedback(
            complaint_id=selected_cid,
            location_id=loc_id,
            status=feedback_status,
            notes=feedback_notes.strip(),
            prediction_id=pred_id,
            role=st.session_state.get("user", {}).get("role", "INVESTIGATOR")
        )
        st.success(f"Feedback successfully recorded for Complaint {selected_cid} and Location {loc_id}!")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Feedback Statistics & Metrics
    st.subheader("📊 Operational Efficacy & Validation Summary")
    feedback_list = get_all_feedback()
    
    if feedback_list:
        df_fb = pd.DataFrame(feedback_list)
        total_fb = len(df_fb)
        useful_count = len(df_fb[df_fb["status"].isin(["Confirmed useful", "Partially useful"])])
        useful_rate = (useful_count / total_fb) * 100 if total_fb > 0 else 0.0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Validation Reviews", f"{total_fb}")
        col2.metric("Positive Efficacy Rate", f"{useful_rate:.1f}%")
        col3.metric("Latest Submission", df_fb["created_at"].iloc[0][:19] if not df_fb.empty else "N/A")

        st.markdown("#### Historical Investigator Feedback Audit Log")
        disp_fb = df_fb[["complaint_id", "location_name", "status", "investigator_role", "notes", "created_at"]].copy()
        disp_fb.columns = ["Case Ref", "Assessed Location", "Outcome", "Reviewer Role", "Field Notes", "Recorded At"]
        st.dataframe(disp_fb, use_container_width=True, hide_index=True)
    else:
        st.info("No investigator feedback recorded yet. Submit feedback above to populate operational metrics.")

    st.markdown("""
    <div class="disclaimer-box">
        <b>DISCLAIMER ON FEEDBACK ANALYTICS:</b><br>
        Operational feedback statistics reflect internal experimental assessment on synthetic evaluation cases.
        They do not constitute verified real-world police efficacy metrics or official audit performance statistics.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_investigator_feedback()
