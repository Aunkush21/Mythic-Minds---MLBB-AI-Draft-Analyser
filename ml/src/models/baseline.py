"""
Logistic Regression baseline. XGBoost must beat this by a meaningful
margin on held-out log-loss/AUC to justify the added complexity.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import DATA_PROCESSED_DIR, RANDOM_SEED
from features.build_features import FEATURE_COLUMNS
from splits import train_test_split_grouped, cv_splitter
from evaluate import compute_metrics, calibration_table, print_report


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)),
    ])


def run_cv(df: pd.DataFrame) -> list[dict]:
    X, y, groups = df[FEATURE_COLUMNS], df["ally_win"], df["match_id"]
    fold_metrics = []
    for fold, (train_idx, val_idx) in enumerate(cv_splitter().split(X, y, groups)):
        pipe = build_pipeline()
        pipe.fit(X.iloc[train_idx], y.iloc[train_idx])
        y_prob = pipe.predict_proba(X.iloc[val_idx])[:, 1]
        m = compute_metrics(y.iloc[val_idx], y_prob)
        m["fold"] = fold
        fold_metrics.append(m)
    return fold_metrics


if __name__ == "__main__":
    df = pd.read_parquet(DATA_PROCESSED_DIR / "features.parquet")
    train_df, test_df = train_test_split_grouped(df)

    print(f"Train: {len(train_df)} rows ({train_df['match_id'].nunique()} matches)")
    print(f"Test:  {len(test_df)} rows ({test_df['match_id'].nunique()} matches)")

    cv_results = run_cv(train_df)
    cv_df = pd.DataFrame(cv_results)
    print("\nCross-validation (5-fold, grouped by match_id):")
    for metric in ["roc_auc", "log_loss", "brier_score", "accuracy"]:
        print(f"  {metric:12s}: {cv_df[metric].mean():.4f} ± {cv_df[metric].std():.4f}")

    final_pipe = build_pipeline()
    final_pipe.fit(train_df[FEATURE_COLUMNS], train_df["ally_win"])
    y_prob_test = final_pipe.predict_proba(test_df[FEATURE_COLUMNS])[:, 1]

    test_metrics = compute_metrics(test_df["ally_win"], y_prob_test)
    calib = calibration_table(test_df["ally_win"], y_prob_test)
    print_report("Logistic Regression — Held-out Test Set", test_metrics, calib)

    coefs = pd.Series(
        final_pipe.named_steps["clf"].coef_[0], index=FEATURE_COLUMNS
    ).sort_values(key=abs, ascending=False)
    print("\nTop coefficients (standardized features):")
    print(coefs.head(10))
