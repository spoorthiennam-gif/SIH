"""
CYBERGUARD AI - Geospatial Mapping Utility
Generates interactive Folium maps with styled markers, risk color coding, and incident radii.
"""

import folium
from folium.plugins import MarkerCluster
from typing import List, Dict, Any, Optional


def create_intelligence_map(
    incident_lat: float,
    incident_lon: float,
    ranked_candidates: List[Dict[str, Any]],
    incident_info: Optional[Dict[str, Any]] = None,
    zoom_start: int = 13
) -> folium.Map:
    """
    Generate an interactive Folium map visualization:
    - Blue marker for reported incident epicenter
    - Color-coded pins for candidate withdrawal locations (Red=High, Orange=Medium, Green=Low)
    - Interactive popups with ranking details, distance, and historical risk
    - Proximity buffer circles and legend
    """
    # Create base map with clean OpenStreetMap tiles
    folium_map = folium.Map(
        location=[incident_lat, incident_lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # 1. Incident epicenter marker (Blue pulsing icon)
    inc_desc = "<b>Reported Incident Location</b><br>"
    if incident_info:
        inc_desc += f"<b>ID:</b> {incident_info.get('complaint_id', 'N/A')}<br>"
        inc_desc += f"<b>Type:</b> {incident_info.get('crime_type', 'N/A')}<br>"
        inc_desc += f"<b>Amount:</b> ₹{float(incident_info.get('amount', 0)):,.2f}<br>"
        inc_desc += f"<b>Coords:</b> {incident_lat:.4f}, {incident_lon:.4f}"

    folium.Marker(
        location=[incident_lat, incident_lon],
        popup=folium.Popup(inc_desc, max_width=300),
        tooltip="Incident Epicenter (Victim Coordinates)",
        icon=folium.Icon(color="blue", icon="shield", prefix="fa")
    ).add_to(folium_map)

    # 3 km and 5 km Proximity perimeter rings
    folium.Circle(
        location=[incident_lat, incident_lon],
        radius=3000,
        color="#3b82f6",
        weight=1.5,
        dash_array="4, 6",
        fill=True,
        fill_opacity=0.04,
        tooltip="3 km Primary Rapid-Response Zone"
    ).add_to(folium_map)

    folium.Circle(
        location=[incident_lat, incident_lon],
        radius=5000,
        color="#64748b",
        weight=1,
        dash_array="3, 5",
        fill=False,
        tooltip="5 km Extended Perimeter Zone"
    ).add_to(folium_map)

    # 2. Add candidate location markers
    for cand in ranked_candidates:
        c_lat = float(cand["latitude"])
        c_lon = float(cand["longitude"])
        rank = cand.get("rank", 999)
        risk_level = cand.get("risk_level", "LOW")
        risk_pct = cand.get("risk_percentage", cand.get("final_risk_score", 0) * 100)
        dist_km = cand.get("distance_km", 0.0)
        hist_risk = cand.get("historical_risk", 0.5)
        name = cand.get("location_name", f"Location {cand.get('location_id')}")
        loc_type = cand.get("location_type", "ATM")

        # Color mapping
        if risk_level == "HIGH":
            icon_color = "red"
            circle_color = "#ef4444"
            icon_name = "exclamation-triangle"
        elif risk_level == "MEDIUM":
            icon_color = "orange"
            circle_color = "#f59e0b"
            icon_name = "credit-card"
        else:
            icon_color = "green"
            circle_color = "#10b981"
            icon_name = "map-marker"

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 6px 0; color: #0f172a;">#{rank} {name}</h4>
            <span style="background: {circle_color}; color: white; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">
                {risk_level} RISK ({risk_pct:.1f}%)
            </span>
            <hr style="margin: 8px 0; border: 0; border-top: 1px solid #e2e8f0;">
            <p style="margin: 4px 0; font-size: 12px;"><b>Type:</b> {loc_type}</p>
            <p style="margin: 4px 0; font-size: 12px;"><b>Distance:</b> {dist_km:.2f} km</p>
            <p style="margin: 4px 0; font-size: 12px;"><b>Historical Risk:</b> {hist_risk:.2f}</p>
            <p style="margin: 4px 0; font-size: 12px;"><b>ML Probability:</b> {cand.get('ml_probability', 0)*100:.1f}%</p>
            <p style="margin: 6px 0 0 0; font-size: 11px; color: #64748b;"><i>Decision-support candidate</i></p>
        </div>
        """

        # For Top 5, use larger custom pins
        if rank <= 5:
            folium.Marker(
                location=[c_lat, c_lon],
                popup=folium.Popup(popup_html, max_width=320),
                tooltip=f"Rank #{rank} — {name} ({risk_pct:.1f}% {risk_level})",
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa")
            ).add_to(folium_map)
        else:
            # Circle markers for lower ranked locations to prevent map clutter
            folium.CircleMarker(
                location=[c_lat, c_lon],
                radius=6,
                color=circle_color,
                fill=True,
                fill_color=circle_color,
                fill_opacity=0.8,
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=f"Rank #{rank} — {name}"
            ).add_to(folium_map)

    # 3. Add Custom Legend HTML
    legend_html = """
    <div style="
        position: fixed; 
        bottom: 25px; right: 25px; width: 230px; 
        background-color: rgba(255, 255, 255, 0.95);
        border: 2px solid #cbd5e1;
        border-radius: 8px;
        padding: 12px;
        font-family: Arial, sans-serif;
        font-size: 12px;
        z-index: 9999;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <b style="font-size: 13px; color: #0f172a;">Risk Score Classification</b><br>
        <span style="color: #3b82f6; font-size: 14px;">●</span> Incident Epicenter<br>
        <span style="color: #ef4444; font-size: 14px;">●</span> High Risk (Score &ge; 75%)<br>
        <span style="color: #f59e0b; font-size: 14px;">●</span> Medium Risk (50% &le; Score &lt; 75%)<br>
        <span style="color: #10b981; font-size: 14px;">●</span> Low Risk (Score &lt; 50%)<br>
        <hr style="margin: 6px 0; border-top: 1px solid #e2e8f0;">
        <span style="font-size: 10px; color: #64748b;">Synthetic Data &bull; Decision Support</span>
    </div>
    """
    folium_map.get_root().html.add_child(folium.Element(legend_html))

    return folium_map
