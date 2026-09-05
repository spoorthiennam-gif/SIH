"""
CYBERGUARD AI - Pages Module
Exports page renderers for modular Streamlit routing.
"""

import sys
import os

# Ensure importability of page modules with numeric prefixes
sys.path.insert(0, os.path.dirname(__file__))

# Import render functions
import importlib

dash_mod = importlib.import_module("1_Dashboard")
render_dashboard = dash_mod.render_dashboard

comp_mod = importlib.import_module("2_New_Complaint")
render_new_complaint = comp_mod.render_new_complaint

pred_mod = importlib.import_module("3_Predictive_Intelligence")
render_predictive_intelligence = pred_mod.render_predictive_intelligence

map_mod = importlib.import_module("4_Intelligence_Map")
render_intelligence_map = map_mod.render_intelligence_map

analytics_mod = importlib.import_module("5_Analytics")
render_analytics = analytics_mod.render_analytics

feedback_mod = importlib.import_module("6_Investigator_Feedback")
render_investigator_feedback = feedback_mod.render_investigator_feedback

perf_mod = importlib.import_module("7_Model_Performance")
render_model_performance = perf_mod.render_model_performance

about_mod = importlib.import_module("8_Methodology_About")
render_methodology_about = about_mod.render_methodology_about

__all__ = [
    "render_dashboard",
    "render_new_complaint",
    "render_predictive_intelligence",
    "render_intelligence_map",
    "render_analytics",
    "render_investigator_feedback",
    "render_model_performance",
    "render_methodology_about"
]
