"""
Final model serialization.

The train/test split's job was to produce an honest, unbiased performance
estimate (done in train.py). For the artifact that actually gets shipped,
we refit on the FULL dataset (train+test) using the chosen hyperparameters
— standard practice once evaluation is complete, since more data only
helps the final model and the held-out set has already served its purpose.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import joblib
import pandas as pd
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import DATA_PROCESSED_DIR, MODELS_DIR, RANDOM_SEED
from features.build_features import FEATURE_COLUMNS

FEATURE_GROUPS = {
    "counter_pick":      ["counter_advantage"],
    "team_synergy":       ["synergy_diff"],
    "meta_strength":      ["winrate_diff", "pickrate_diff", "banrate_diff",
                            "op_count_diff", "meta_count_diff"],
    "team_composition":   ["role_diversity_diff", "role_Tank_diff", "role_Fighter_diff",
                            "role_Assassin_diff", "role_Mage_diff", "role_Marksman_diff",
                            "role_Support_diff", "damage_physical_diff", "damage_magic_diff"],
    "lane_fit":           ["lane_fit_diff"],
    "ban_pressure":       ["ban_meta_pressure_diff"],
    "match_context":      ["rank_ordinal"],
}

VERSION = "v1"


def main():
    with open(MODELS_DIR / "best_params.json") as f:
        tuned = json.load(f)

    df = pd.read_parquet(DATA_PROCESSED_DIR / "features.parquet")

    model = xgb.XGBClassifier(
        **tuned["params"],
        n_estimators=tuned["n_estimators"],
        random_state=RANDOM_SEED,
        eval_metric="logloss",
    )
    model.fit(df[FEATURE_COLUMNS], df["ally_win"])

    version_dir = MODELS_DIR / VERSION
    version_dir.mkdir(parents=True, exist_ok=True)

    model.save_model(version_dir / "model.json")
    joblib.dump(FEATURE_COLUMNS, version_dir / "feature_columns.pkl")

    metadata = {
        "version": VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_training_rows": len(df),
        "n_matches": int(df["match_id"].nunique()),
        "feature_columns": FEATURE_COLUMNS,
        "feature_groups": FEATURE_GROUPS,
        "hyperparameters": tuned["params"],
        "n_estimators": tuned["n_estimators"],
        "held_out_test_metrics": tuned["test_metrics"],
        "data_caveat": (
            "Trained on synthetically generated matches (database/seed/matches.py) "
            "whose win labels are a noisy-but-direct function of hero is_meta/is_op "
            "flags. Held-out metrics (AUC ~0.97) reflect recovery of that synthetic "
            "rule, not real-world MLBB draft prediction accuracy. Retrain on real "
            "match data before using these metrics in production claims."
        ),
    }
    with open(version_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Serialized model -> {version_dir}")
    print(f"  model.json, feature_columns.pkl, metadata.json")
    print(f"  Trained on {metadata['n_training_rows']} rows ({metadata['n_matches']} matches)")


if __name__ == "__main__":
    main()
