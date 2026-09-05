"""
CYBERGUARD AI - Model Training Pipeline
Trains RandomForestClassifier on synthetic historical cases, calculates genuine metrics
including Top-1, Top-3, Top-5 ranking evaluation, and serializes artifacts.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

from src.feature_engineering import prepare_training_matrices, FEATURE_COLUMNS
from src.database import save_model_run

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def evaluate_top_k(model: RandomForestClassifier, df_test: pd.DataFrame) -> Tuple[float, float, float]:
    """
    Compute Top-1, Top-3, and Top-5 ranking accuracy across historical test cases.
    Verifies whether the actual withdrawal candidate ranks in top K model predictions.
    """
    case_groups = df_test.groupby("case_id")
    top1_hits, top3_hits, top5_hits = 0, 0, 0
    valid_cases = 0

    for case_id, group in case_groups:
        if 1 not in group["withdrawal_occurred"].values:
            continue
        valid_cases += 1
        X_group, _ = prepare_training_matrices(group)
        probs = model.predict_proba(X_group)[:, 1]
        
        # Rank by probability descending
        ranked_indices = np.argsort(probs)[::-1]
        actual_labels = group["withdrawal_occurred"].values[ranked_indices]
        
        if 1 in actual_labels[:1]:
            top1_hits += 1
        if 1 in actual_labels[:3]:
            top3_hits += 1
        if 1 in actual_labels[:5]:
            top5_hits += 1

    if valid_cases == 0:
        return 0.0, 0.0, 0.0

    return (
        round(top1_hits / valid_cases, 4),
        round(top3_hits / valid_cases, 4),
        round(top5_hits / valid_cases, 4)
    )


def train_prediction_model(training_csv_path: str = None) -> Dict[str, Any]:
    """
    Execute end-to-end model training, evaluation, and artifact persistence.
    """
    if training_csv_path is None:
        training_csv_path = os.path.join(DATA_DIR, "synthetic_training_pairs.csv")

    if not os.path.exists(training_csv_path):
        raise FileNotFoundError(f"Training dataset not found at {training_csv_path}")

    df = pd.read_csv(training_csv_path)

    # Prepare features and target
    X, y = prepare_training_matrices(df)

    # Stratified Train/Test split (80/20)
    X_train, X_test, y_train, y_test, df_train, df_test = train_test_split(
        X, y, df, test_size=0.20, random_state=42, stratify=y
    )

    # Train Random Forest Classifier
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Evaluate classification metrics on held-out test set
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Evaluate Top-K Ranking performance
    top1, top3, top5 = evaluate_top_k(clf, df_test)

    # Feature importances
    importances = {
        col: round(float(imp), 4)
        for col, imp in zip(FEATURE_COLUMNS, clf.feature_importances_)
    }
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))

    timestamp_str = datetime.now().isoformat()
    metrics = {
        "model_name": "RandomForestClassifier",
        "training_timestamp": timestamp_str,
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "top1": top1,
        "top3": top3,
        "top5": top5,
        "confusion_matrix": cm,
        "feature_importances": sorted_importances,
        "parameters": {
            "n_estimators": 150,
            "max_depth": 10,
            "class_weight": "balanced",
            "random_state": 42
        }
    }

    # Save artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "prediction_model.pkl")
    joblib.dump(clf, model_path)

    with open(os.path.join(MODEL_DIR, "feature_columns.json"), "w") as f:
        json.dump(FEATURE_COLUMNS, f, indent=2)

    with open(os.path.join(MODEL_DIR, "model_metadata.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # Save to SQLite database for audit and dashboard KPI tracking
    save_model_run(metrics)

    return metrics


def load_trained_model():
    """Load the trained model and feature definitions."""
    model_path = os.path.join(MODEL_DIR, "prediction_model.pkl")
    meta_path = os.path.join(MODEL_DIR, "model_metadata.json")

    if not os.path.exists(model_path):
        return None, None

    model = joblib.load(model_path)
    metadata = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            metadata = json.load(f)

    return model, metadata
