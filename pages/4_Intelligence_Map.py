"""
CYBERGUARD AI - Geospatial Intelligence Map Page
Visualizes incident epicenter, candidate cash-withdrawal nodes, risk buffers, and details.
"""

import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

from src.map_utils import create_intelligence_map
from src.database import get_recent_complaints
from src.prediction import predict_candidate_locations


def render_intelligence_map():
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">Geospatial Intelligence Map</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Spatial distribution of reported incident epicenter, candidate cashout nodes, and operational proximity buffers.</p>', unsafe_allow_html=True)

    curr_pred = st.session_state.get("current_prediction")
    curr_complaint = st.session_state.get("current_complaint")

    if not curr_pred or not curr_complaint:
        st.info("No active complaint analysis selected.")
        recent_complaints = get_recent_complaints(limit=10)
        if recent_complaints:
            cid_options = [f"{c['complaint_id']} — {c['crime_type']} (₹{c['amount']:,.0f})" for c in recent_complaints]
            selected_option = st.selectbox("Select a complaint to project onto tactical map:", cid_options)
            sel_cid = selected_option.split(" — ")[0]
            sel_comp = next(c for c in recent_complaints if c["complaint_id"] == sel_cid)
            if st.button("Load Map for Selected Complaint"):
                with st.spinner("Calculating geospatial intelligence..."):
                    pred_res = predict_candidate_locations(sel_comp, top_n=10)
                    st.session_state["current_complaint"] = sel_comp
                    st.session_state["current_prediction"] = pred_res
                    st.rerun()
            return
        else:
            st.warning("Please register a complaint first.")
            return

    # Filter controls in columns
    m_col1, m_col2, m_col3 = st.columns([2, 1, 1])
    with m_col1:
        st.markdown(f"**Incident:** `{curr_complaint['complaint_id']}` | **Coords:** `{curr_complaint['latitude']:.4f}°N, {curr_complaint['longitude']:.4f}°E`")
    with m_col2:
        risk_filter = st.selectbox("Filter Risk Tier:", ["All Tiers", "High Risk Only", "High & Medium Risk"])
    with m_col3:
        display_count = st.selectbox("Candidate Pool:", [5, 10, 25, 100], index=1)

    all_candidates = curr_pred["all_ranked_candidates"][:display_count]

    # Filter by risk tier if selected
    if risk_filter == "High Risk Only":
        filtered_candidates = [c for c in all_candidates if c["risk_level"] == "HIGH"]
    elif risk_filter == "High & Medium Risk":
        filtered_candidates = [c for c in all_candidates if c["risk_level"] in ["HIGH", "MEDIUM"]]
    else:
        filtered_candidates = all_candidates

    # Generate Folium map
    folium_map = create_intelligence_map(
        incident_lat=float(curr_complaint["latitude"]),
        incident_lon=float(curr_complaint["longitude"]),
        ranked_candidates=filtered_candidates,
        incident_info=curr_complaint,
        zoom_start=13
    )

    # Render interactive Folium map in Streamlit
    st_folium(folium_map, width="100%", height=550)

    st.markdown("<br>", unsafe_allow_html=True)

    # Candidate details expander
    st.subheader(f"📍 Mapped Candidate Nodes ({len(filtered_candidates)} Displayed)")
    summary_data = []
    for c in filtered_candidates[:10]:
        summary_data.append({
            "Rank": f"#{c['rank']}",
            "Location": c["location_name"],
            "Type": c.get("location_type", "ATM"),
            "Risk Score": f"{c['risk_percentage']:.1f}%",
            "Level": c["risk_level"],
            "Distance": f"{c['distance_km']:.2f} km",
            "Historical Risk": f"{c['historical_risk']:.2f}"
        })
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    render_intelligence_map()
