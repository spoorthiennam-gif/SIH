"""
CYBERGUARD AI - Prototype Authentication & Session Management
Provides lightweight role-based access control for Smart India Hackathon demonstrations.
Clearly marked as a local prototype authentication layer.
"""

from typing import Dict, Any, Optional

DEMO_USERS = {
    "investigator": {
        "password": "demo_password",
        "name": "Inspector R. Verma",
        "badge": "TS-CYBER-8842",
        "role": "INVESTIGATOR",
        "department": "Cyber Crime Police Station, Hyderabad"
    },
    "analyst": {
        "password": "demo_password",
        "name": "P. Swaminathan (Analyst)",
        "badge": "ANALYST-042",
        "role": "ANALYST",
        "department": "Financial Fraud Intelligence Unit"
    },
    "admin": {
        "password": "demo_password",
        "name": "Superintendent K. Rao",
        "badge": "ADMIN-001",
        "role": "ADMIN",
        "department": "State Cyber Security Command Center"
    }
}


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate demo user credentials against demo configuration.
    Non-production prototype demonstration only.
    """
    u = username.strip().lower()
    if u in DEMO_USERS and DEMO_USERS[u]["password"] == password:
        user_info = DEMO_USERS[u].copy()
        user_info["username"] = u
        return user_info
    return None
