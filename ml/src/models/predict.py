"""
Clean win-prediction entrypoint for external callers (the FastAPI backend).

Composes three pieces that already exist independently:
  - features/build_features.compute_match_row  (feature engineering)
  - the serialized XGBoost model (loaded once via recommendation's
    DataContext, which already loads it for the Hero Recommendation
    Engine's oracle — reused here rather than loading it a second time)
  - explainability/shap_explainer                (SHAP explanation + the
    unified Explanation schema adapter)

This file is purely additive — it does not modify any existing ml/ module.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "features"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "recommendation"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "explainability"))

from config import MODELS_DIR
from build_features import compute_match_row
from data_loader import get_context as get_recommendation_context
import shap_explainer

MODEL_VERSION = "v1"


class ModelNotLoadedError(RuntimeError):
    """Raised when the win predictor artifact hasn't been trained/serialized yet."""


def _load_metadata() -> dict:
    path = MODELS_DIR / MODEL_VERSION / "metadata.json"
    if not path.exists():
        raise ModelNotLoadedError(f"No model metadata found at {path}. Run ml/src/models/serialize.py first.")
    with open(path) as f:
        return json.load(f)


def predict_win_probability(
    ally_lanes: dict[str, int],
    enemy_lanes: dict[str, int],
    ally_bans: list[int],
    enemy_bans: list[int],
    patch_version: str | None,
    rank: str,
) -> dict:
    """
    ally_lanes/enemy_lanes: {"exp": hero_id, "gold": hero_id, ...} — all 5
    lanes must be filled (this predicts a complete draft, unlike the Hero
    Recommendation Engine which handles partial drafts).
    """
    ctx = get_recommendation_context()
    if ctx.win_model is None:
        raise ModelNotLoadedError(
            "Win predictor model artifact not found. Run ml/src/models/train.py "
            "then ml/src/models/serialize.py to produce ml/models/v1/."
        )

    patch = ctx.resolve_patch(patch_version)

    row = compute_match_row(
        ally_lanes, enemy_lanes, ally_bans, enemy_bans, patch, rank,
        ctx.heroes, ctx.counter_lookup, ctx.synergy_lookup, ctx.hero_stats_lookup,
    )
    X = pd.DataFrame([row])[ctx.win_model_feature_columns]

    win_prob = float(ctx.win_model.predict_proba(X)[0, 1])
    raw_explanation = shap_explainer.explain_prediction(ctx.win_model, X.iloc[0], ctx.win_model_feature_groups)

    metadata = _load_metadata()
    unified_explanation = shap_explainer.to_explanation(raw_explanation, metadata)

    return {
        "win_probability": win_prob,
        "patch_version": patch,
        "explanation": unified_explanation,
    }
