"""
SHAP-based explainability for the win predictor.

Two outputs:
  - global_importance(): which feature GROUPS drive predictions overall
  - explain_prediction(): per-draft breakdown, grouped into human-readable
    categories (counter pick, synergy, meta strength, etc.) — this is what
    the API will hand to the "Explainable AI Insights" module.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import joblib
import numpy as np
import pandas as pd
import shap
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import DATA_PROCESSED_DIR, MODELS_DIR
from schema import Explanation, ExplanationFactor, Confidence

VERSION = "v1"


def load_model():
    version_dir = MODELS_DIR / VERSION
    model = xgb.XGBClassifier()
    model.load_model(version_dir / "model.json")
    feature_columns = joblib.load(version_dir / "feature_columns.pkl")
    with open(version_dir / "metadata.json") as f:
        metadata = json.load(f)
    return model, feature_columns, metadata


def global_importance(model, X: pd.DataFrame, feature_groups: dict) -> pd.DataFrame:
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    mean_abs = pd.Series(np.abs(shap_values).mean(axis=0), index=X.columns)

    group_importance = {}
    for group, cols in feature_groups.items():
        group_importance[group] = mean_abs[cols].sum()

    return pd.Series(group_importance).sort_values(ascending=False)


def explain_prediction(model, x_row: pd.Series, feature_groups: dict) -> dict:
    explainer = shap.TreeExplainer(model)
    x_df = x_row.to_frame().T
    shap_values = explainer.shap_values(x_df)[0]
    base_value = explainer.expected_value

    win_prob = float(model.predict_proba(x_df)[0, 1])

    per_feature = dict(zip(x_row.index, shap_values))
    per_group = {
        group: float(sum(per_feature[c] for c in cols))
        for group, cols in feature_groups.items()
    }
    sorted_groups = sorted(per_group.items(), key=lambda kv: abs(kv[1]), reverse=True)

    return {
        "win_probability": win_prob,
        "base_probability": float(1 / (1 + np.exp(-base_value))),
        "group_contributions": dict(sorted_groups),
        "top_driver": sorted_groups[0][0],
        "feature_values": x_row.to_dict(),
    }


def to_explanation(explanation: dict, metadata: dict) -> Explanation:
    """
    Confidence is deliberately capped at "medium" regardless of how
    decisive the predicted probability looks — confidence here reflects
    DATA PROVENANCE (this model was trained on a synthetic generator,
    not real matches), not the model's own self-reported certainty. A
    99% prediction is not more trustworthy just because it's extreme.
    """
    factors = [
        ExplanationFactor(
            label=group,
            description=f"{group.replace('_', ' ').title()} contributes {val:+.3f} to win probability.",
            value=round(val, 4),
            direction="positive" if val > 0 else ("negative" if val < 0 else "neutral"),
        )
        for group, val in explanation["group_contributions"].items()
    ]
    confidence = Confidence(
        level="medium",
        source="model_inference",
        basis=metadata.get("data_caveat", "Model provenance not documented."),
    )
    summary = f"{explanation['win_probability'] * 100:.1f}% win probability for the ally side."
    return Explanation(module="win_prediction", summary=summary, factors=factors, confidence=confidence)


def describe(explanation: dict) -> str:
    pct = explanation["win_probability"] * 100
    top, top_val = next(iter(explanation["group_contributions"].items()))
    direction = "favors" if top_val > 0 else "hurts"
    return (
        f"Win probability: {pct:.1f}%. "
        f"Primary driver: '{top}' {direction} this draft "
        f"(SHAP contribution: {top_val:+.3f})."
    )


if __name__ == "__main__":
    model, feature_columns, metadata = load_model()
    feature_groups = metadata["feature_groups"]

    df = pd.read_parquet(DATA_PROCESSED_DIR / "features.parquet")
    X = df[feature_columns]

    print("=" * 50)
    print("  Global Feature Group Importance (mean |SHAP|)")
    print("=" * 50)
    print(global_importance(model, X, feature_groups))

    print("\n" + "=" * 50)
    print("  Example Per-Draft Explanation")
    print("=" * 50)
    sample = X.iloc[0]
    explanation = explain_prediction(model, sample, feature_groups)
    print(describe(explanation))
    print("\nFull group breakdown:")
    for group, val in explanation["group_contributions"].items():
        print(f"  {group:18s}: {val:+.4f}")

    print("\n" + "=" * 50)
    print("  Unified Explanation Schema")
    print("=" * 50)
    unified = to_explanation(explanation, metadata)
    print(f"Module: {unified.module}")
    print(f"Summary: {unified.summary}")
    print(f"Confidence: {unified.confidence.level} ({unified.confidence.source})")
    print(f"Basis: {unified.confidence.basis}")
    print("Factors:")
    for f in unified.factors:
        print(f"  [{f.direction:8s}] {f.description}")
