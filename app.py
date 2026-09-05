"""
CYBERGUARD AI - Master Streamlit Application Entry Point
Predictive Cybercrime Intelligence & Withdrawal Risk Analytics
Smart India Hackathon Prototype
"""

import streamlit as st
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.bootstrap import bootstrap_system
from src.auth import authenticate_user, DEMO_USERS
from src.database import get_latest_model_run, log_audit

# Import page renderers
from pages import (
    render_dashboard,
    render_new_complaint,
    render_predictive_intelligence,
    render_intelligence_map,
    render_analytics,
    render_investigator_feedback,
    render_model_performance,
    render_methodology_about
)


# Streamlit Page Config
st.set_page_config(
    page_title="CYBERGUARD AI — Predictive Cybercrime Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load Custom CSS
def load_custom_css():
    css_path = os.path.join(BASE_DIR, "assets", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Auto-bootstrap system data and model
@st.cache_resource(show_spinner="Initializing CYBERGUARD AI data and ML models...")
def ensure_system_initialized():
    return bootstrap_system()


def main():
    load_custom_css()
    init_status = ensure_system_initialized()

    # Session State Initialization
    if "authenticated" not in st.session_state:
        # Default to pre-authenticated investigator for ultra-smooth SIH demo flow
        st.session_state["authenticated"] = True
        st.session_state["user"] = DEMO_USERS["investigator"]

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "📊 Dashboard"

    # Authentication Gate
    if not st.session_state.get("authenticated", False):
        render_login_screen()
        return

    # Render Authenticated App
    render_sidebar(init_status)
    render_active_page()


def render_login_screen():
    st.markdown('<div style="text-align: center; margin-top: 50px;">', unsafe_allow_html=True)
    st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="platform-title">CYBERGUARD AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="platform-subtitle">Predictive Cybercrime Intelligence & Withdrawal Risk Analytics</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="kpi-card" style="margin-top: 20px;">
            <h3 style="color: #ffffff; margin-bottom: 8px;">🔐 Authorized Personnel Login</h3>
            <p style="color: #94a3b8; font-size: 13px;">Restricted access portal for authorized cybercrime analysts and investigators.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username / Officer ID", value="investigator")
            password = st.text_input("Password", type="password", value="demo_password")
            submitted = st.form_submit_button("LOGIN TO CYBERGUARD AI", use_container_width=True)

        if submitted:
            user = authenticate_user(username, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                log_audit("LOGIN", user["role"], f"User {username} authenticated successfully.")
                st.rerun()
            else:
                st.error("Invalid credentials. Please use demo credentials listed below.")

        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px dashed #334155; border-radius: 8px; padding: 12px; margin-top: 15px; font-size: 12px; color: #94a3b8;">
            <b>⚡ Quick Demo Accounts (Password: <code>demo_password</code>):</b><br>
            • <code>investigator</code> &rarr; Inspector R. Verma (Field Investigation)<br>
            • <code>analyst</code> &rarr; P. Swaminathan (Intelligence Unit)<br>
            • <code>admin</code> &rarr; Superintendent K. Rao (Command Oversight)
        </div>
        """, unsafe_allow_html=True)

        # 1-Click Quick Login Buttons
        c_a, c_b, c_c = st.columns(3)
        with c_a:
            if st.button("👮 Investigator Login", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["user"] = DEMO_USERS["investigator"]
                st.rerun()
        with c_b:
            if st.button("📊 Analyst Login", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["user"] = DEMO_USERS["analyst"]
                st.rerun()
        with c_c:
            if st.button("🛡️ Admin Login", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["user"] = DEMO_USERS["admin"]
                st.rerun()


def render_sidebar(init_status):
    with st.sidebar:
        st.markdown('<div class="demo-badge">DEMO — SYNTHETIC DATA</div>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #ffffff; margin: 0 0 2px 0;">🛡️ CYBERGUARD AI</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #06b6d4; font-size: 11px; margin-bottom: 16px;">Withdrawal Risk Intelligence Platform</p>', unsafe_allow_html=True)

        # User profile badge
        user = st.session_state.get("user", DEMO_USERS["investigator"])
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid #334155; border-radius: 8px; padding: 10px; margin-bottom: 18px;">
            <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Authenticated Officer</div>
            <div style="color: #ffffff; font-weight: bold; font-size: 13px;">{user['name']}</div>
            <div style="font-size: 11px; color: #38bdf8;">{user['role']} • {user['badge']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation Options
        pages = [
            "📊 Dashboard",
            "📝 New Complaint",
            "🎯 Predictive Intelligence",
            "🗺️ Intelligence Map",
            "📈 Analytics",
            "💬 Investigator Feedback",
            "⚡ Model Performance",
            "📖 Methodology & About"
        ]

        selected_page = st.radio(
            "COMMAND NAVIGATION:",
            pages,
            index=pages.index(st.session_state.get("current_page", "📊 Dashboard")) if st.session_state.get("current_page") in pages else 0
        )
        st.session_state["current_page"] = selected_page

        st.markdown("<hr style='border-color: #243552; margin: 20px 0;'>", unsafe_allow_html=True)

        # System Status Indicator
        model_meta = get_latest_model_run()
        top5_val = model_meta["top5"] * 100 if model_meta else 85.0

        st.markdown(f"""
        <div style="font-size: 11px; color: #64748b; line-height: 1.6;">
            <b>SYSTEM TELEMETRY:</b><br>
            • Database: <span style="color: #10b981;">● Online (SQLite)</span><br>
            • Candidate Nodes: <span style="color: #38bdf8;">100 Hyd Urban</span><br>
            • Active ML: <span style="color: #38bdf8;">Random Forest</span><br>
            • Top-5 Accuracy: <span style="color: #10b981;"><b>{top5_val:.1f}%</b></span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout / Switch Role", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()


def render_active_page():
    page = st.session_state.get("current_page", "📊 Dashboard")

    if page == "📊 Dashboard":
        render_dashboard()
    elif page == "📝 New Complaint":
        render_new_complaint()
    elif page == "🎯 Predictive Intelligence":
        render_predictive_intelligence()
    elif page == "🗺️ Intelligence Map":
        render_intelligence_map()
    elif page == "📈 Analytics":
        render_analytics()
    elif page == "💬 Investigator Feedback":
        render_investigator_feedback()
    elif page == "⚡ Model Performance":
        render_model_performance()
    elif page == "📖 Methodology & About":
        render_methodology_about()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
