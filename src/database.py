"""
CYBERGUARD AI - Database Management Module
Handles SQLite schema creation, complaints, candidate locations, predictions, feedback, and audit trails.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "cyberguard.db")


def get_db_connection():
    """Create and return a database connection."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize SQLite database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            crime_type TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            previous_transaction_count INTEGER DEFAULT 0,
            previous_transaction_amount REAL DEFAULT 0.0,
            time_since_previous_transaction REAL DEFAULT 0.0,
            suspicious_activity_score REAL DEFAULT 0.0,
            victim_area_risk_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'PENDING_PREDICTION',
            created_at TEXT NOT NULL
        )
    """)

    # 2. Candidate Locations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            historical_risk REAL NOT NULL,
            location_type TEXT NOT NULL,
            transaction_volume_score REAL DEFAULT 0.5,
            night_activity_score REAL DEFAULT 0.5,
            previous_incident_count INTEGER DEFAULT 0,
            area_risk_score REAL DEFAULT 0.5,
            created_at TEXT NOT NULL
        )
    """)

    # 3. Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            location_name TEXT,
            ml_probability REAL NOT NULL,
            historical_risk REAL NOT NULL,
            proximity_score REAL NOT NULL,
            final_risk_score REAL NOT NULL,
            risk_level TEXT NOT NULL,
            distance_km REAL NOT NULL,
            rank_order INTEGER NOT NULL,
            explanation TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id)
        )
    """)

    # 4. Investigator Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investigator_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER,
            complaint_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            investigator_role TEXT DEFAULT 'INVESTIGATOR',
            created_at TEXT NOT NULL
        )
    """)

    # 5. Model Runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            training_timestamp TEXT NOT NULL,
            accuracy REAL NOT NULL,
            precision REAL NOT NULL,
            recall REAL NOT NULL,
            f1 REAL NOT NULL,
            roc_auc REAL NOT NULL,
            top1 REAL NOT NULL,
            top3 REAL NOT NULL,
            top5 REAL NOT NULL,
            dataset_size INTEGER NOT NULL,
            test_size INTEGER NOT NULL,
            metadata_json TEXT
        )
    """)

    # 6. Audit Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            user_role TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_complaint(complaint_dict: Dict[str, Any]) -> str:
    """Insert or replace a complaint record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO complaints (
            complaint_id, crime_type, transaction_type, amount,
            timestamp, latitude, longitude,
            previous_transaction_count, previous_transaction_amount,
            time_since_previous_transaction, suspicious_activity_score,
            victim_area_risk_score, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(complaint_id) DO UPDATE SET
            crime_type=excluded.crime_type,
            transaction_type=excluded.transaction_type,
            amount=excluded.amount,
            timestamp=excluded.timestamp,
            latitude=excluded.latitude,
            longitude=excluded.longitude,
            previous_transaction_count=excluded.previous_transaction_count,
            previous_transaction_amount=excluded.previous_transaction_amount,
            time_since_previous_transaction=excluded.time_since_previous_transaction,
            suspicious_activity_score=excluded.suspicious_activity_score,
            victim_area_risk_score=excluded.victim_area_risk_score,
            status=excluded.status
    """, (
        complaint_dict["complaint_id"],
        complaint_dict["crime_type"],
        complaint_dict["transaction_type"],
        float(complaint_dict["amount"]),
        complaint_dict["timestamp"],
        float(complaint_dict["latitude"]),
        float(complaint_dict["longitude"]),
        int(complaint_dict.get("previous_transaction_count", 0)),
        float(complaint_dict.get("previous_transaction_amount", 0.0)),
        float(complaint_dict.get("time_since_previous_transaction", 0.0)),
        float(complaint_dict.get("suspicious_activity_score", 0.5)),
        float(complaint_dict.get("victim_area_risk_score", 0.5)),
        complaint_dict.get("status", "ANALYZED"),
        now_str
    ))
    conn.commit()
    conn.close()
    return complaint_dict["complaint_id"]


def save_candidate_locations(locations_df: pd.DataFrame):
    """Seed or update candidate locations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    for _, row in locations_df.iterrows():
        cursor.execute("""
            INSERT INTO candidate_locations (
                location_id, name, latitude, longitude, historical_risk,
                location_type, transaction_volume_score, night_activity_score,
                previous_incident_count, area_risk_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(location_id) DO UPDATE SET
                name=excluded.name,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                historical_risk=excluded.historical_risk,
                location_type=excluded.location_type,
                transaction_volume_score=excluded.transaction_volume_score,
                night_activity_score=excluded.night_activity_score,
                previous_incident_count=excluded.previous_incident_count,
                area_risk_score=excluded.area_risk_score
        """, (
            str(row["location_id"]),
            str(row["location_name"]),
            float(row["latitude"]),
            float(row["longitude"]),
            float(row["historical_risk_score"]),
            str(row["location_type"]),
            float(row.get("transaction_volume_score", 0.5)),
            float(row.get("night_activity_score", 0.5)),
            int(row.get("previous_incident_count", 0)),
            float(row.get("area_risk_score", 0.5)),
            now_str
        ))
    conn.commit()
    conn.close()


def get_candidate_locations() -> pd.DataFrame:
    """Retrieve all candidate locations as a DataFrame."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM candidate_locations", conn)
    conn.close()
    return df


def save_predictions(complaint_id: str, predictions_list: List[Dict[str, Any]]):
    """Save ranked prediction results for a complaint."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    # Clear previous predictions for this complaint if re-run
    cursor.execute("DELETE FROM predictions WHERE complaint_id = ?", (complaint_id,))

    for pred in predictions_list:
        cursor.execute("""
            INSERT INTO predictions (
                complaint_id, location_id, location_name, ml_probability,
                historical_risk, proximity_score, final_risk_score,
                risk_level, distance_km, rank_order, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint_id,
            pred["location_id"],
            pred.get("location_name", ""),
            float(pred["ml_probability"]),
            float(pred["historical_risk"]),
            float(pred["proximity_score"]),
            float(pred["final_risk_score"]),
            pred["risk_level"],
            float(pred["distance_km"]),
            int(pred["rank"]),
            pred.get("explanation", ""),
            now_str
        ))

    # Update complaint status
    cursor.execute("UPDATE complaints SET status = 'PREDICTION_GENERATED' WHERE complaint_id = ?", (complaint_id,))
    conn.commit()
    conn.close()


def get_predictions_by_complaint(complaint_id: str) -> List[Dict[str, Any]]:
    """Retrieve predictions for a given complaint ordered by rank."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM predictions
        WHERE complaint_id = ?
        ORDER BY rank_order ASC
    """, (complaint_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_predictions(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent predictions across all complaints."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM predictions
        ORDER BY created_at DESC, final_risk_score DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_recent_complaints(limit: int = 10) -> List[Dict[str, Any]]:
    """Get the latest complaints."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM complaints
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_complaint_by_id(complaint_id: str) -> Optional[Dict[str, Any]]:
    """Get a complaint by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_feedback(complaint_id: str, location_id: str, status: str, notes: str = "", prediction_id: Optional[int] = None, role: str = "INVESTIGATOR"):
    """Record investigator feedback for a prediction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO investigator_feedback (
            prediction_id, complaint_id, location_id, status, notes, investigator_role, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (prediction_id, complaint_id, location_id, status, notes, role, now_str))
    conn.commit()
    conn.close()


def get_all_feedback() -> List[Dict[str, Any]]:
    """Retrieve all investigator feedback records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, p.location_name, p.final_risk_score, p.risk_level
        FROM investigator_feedback f
        LEFT JOIN predictions p ON f.complaint_id = p.complaint_id AND f.location_id = p.location_id
        ORDER BY f.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_model_run(run_metrics: Dict[str, Any]):
    """Record an ML training run with metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO model_runs (
            model_name, training_timestamp, accuracy, precision, recall,
            f1, roc_auc, top1, top3, top5, dataset_size, test_size, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_metrics.get("model_name", "RandomForestClassifier"),
        run_metrics.get("training_timestamp", datetime.now().isoformat()),
        float(run_metrics.get("accuracy", 0.0)),
        float(run_metrics.get("precision", 0.0)),
        float(run_metrics.get("recall", 0.0)),
        float(run_metrics.get("f1", 0.0)),
        float(run_metrics.get("roc_auc", 0.0)),
        float(run_metrics.get("top1", 0.0)),
        float(run_metrics.get("top3", 0.0)),
        float(run_metrics.get("top5", 0.0)),
        int(run_metrics.get("dataset_size", 0)),
        int(run_metrics.get("test_size", 0)),
        json.dumps(run_metrics.get("metadata", {}))
    ))
    conn.commit()
    conn.close()


def get_latest_model_run() -> Optional[Dict[str, Any]]:
    """Fetch metrics from the most recent model training."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM model_runs ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def log_audit(action: str, user_role: str, details: str = ""):
    """Log user actions for auditability."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (action, user_role, details, timestamp)
        VALUES (?, ?, ?, ?)
    """, (action, user_role, details, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_dashboard_kpis() -> Dict[str, Any]:
    """Calculate live dashboard KPIs directly from SQLite data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT complaint_id) FROM predictions")
    predictions_generated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM candidate_locations WHERE historical_risk >= 0.70")
    high_risk_locations = cursor.fetchone()[0]

    cursor.execute("SELECT top5 FROM model_runs ORDER BY id DESC LIMIT 1")
    model_row = cursor.fetchone()
    top5_accuracy = model_row[0] if model_row else 0.0

    conn.close()
    return {
        "total_complaints": total_complaints,
        "predictions_generated": predictions_generated,
        "high_risk_locations": high_risk_locations,
        "model_top5_accuracy": top5_accuracy
    }
