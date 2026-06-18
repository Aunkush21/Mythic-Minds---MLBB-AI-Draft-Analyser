"""
XGBoost win-probability model: grouped CV + Optuna hyperparameter search,
with early stopping per fold to pick a stable number of boosting rounds.
Must beat the logistic regression baseline (baseline.py) on held-out
log-loss to justify its complexity.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import optuna
import xgboost as xgb
from sklearn.metrics import log_loss

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import DATA_PROCESSED_DIR, RANDOM_SEED
from features.build_features import FEATURE_COLUMNS
from splits import train_test_split_grouped, cv_splitter
from evaluate import compute_metrics, calibration_table, print_report

optuna.logging.set_verbosity(optuna.logging.WARNING)

N_TRIALS = 40
N_FOLDS = 5
EARLY_STOPPING_ROUNDS = 30
MAX_ESTIMATORS = 500


def _fit_fold(params, X_train, y_train, X_val, y_val):
    model = xgb.XGBClassifier(
        **params,
        n_estimators=MAX_ESTIMATORS,
        random_state=RANDOM_SEED,
        eval_metric="logloss",
        early_stopping_rounds=EARLY_STOPPING_ROUNDS,
    )
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    return model


def cv_objective(trial, X, y, groups):
    params = {
        "max_depth": trial.suggest_int("max_depth", 2, 5),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 5.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 5.0, log=True),
    }

    fold_losses, fold_iters = [], []
    for train_idx, val_idx in cv_splitter(N_FOLDS).split(X, y, groups):
        model = _fit_fold(params, X.iloc[train_idx], y.iloc[train_idx],
                           X.iloc[val_idx], y.iloc[val_idx])
        y_prob = model.predict_proba(X.iloc[val_idx])[:, 1]
        fold_losses.append(log_loss(y.iloc[val_idx], y_prob))
        fold_iters.append(model.best_iteration or MAX_ESTIMATORS)

    trial.set_user_attr("mean_best_iteration", float(np.mean(fold_iters)))
    return float(np.mean(fold_losses))


def run_search(train_df: pd.DataFrame) -> optuna.Study:
    X, y, groups = train_df[FEATURE_COLUMNS], train_df["ally_win"], train_df["match_id"]
    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
    study.optimize(lambda t: cv_objective(t, X, y, groups), n_trials=N_TRIALS, show_progress_bar=False)
    return study


if __name__ == "__main__":
    df = pd.read_parquet(DATA_PROCESSED_DIR / "features.parquet")
    train_df, test_df = train_test_split_grouped(df)

    print(f"Train: {len(train_df)} rows ({train_df['match_id'].nunique()} matches)")
    print(f"Test:  {len(test_df)} rows ({test_df['match_id'].nunique()} matches)")
    print(f"\nRunning Optuna search ({N_TRIALS} trials, {N_FOLDS}-fold grouped CV)...")

    study = run_search(train_df)
    best_params = study.best_params
    best_n_estimators = int(round(study.best_trial.user_attrs["mean_best_iteration"]))

    print(f"\nBest CV log-loss: {study.best_value:.4f}")
    print(f"Best params: {best_params}")
    print(f"Chosen n_estimators (avg best_iteration across folds): {best_n_estimators}")

    final_model = xgb.XGBClassifier(
        **best_params,
        n_estimators=best_n_estimators,
        random_state=RANDOM_SEED,
        eval_metric="logloss",
    )
    final_model.fit(train_df[FEATURE_COLUMNS], train_df["ally_win"])

    y_prob_test = final_model.predict_proba(test_df[FEATURE_COLUMNS])[:, 1]
    test_metrics = compute_metrics(test_df["ally_win"], y_prob_test)
    calib = calibration_table(test_df["ally_win"], y_prob_test)
    print_report("XGBoost — Held-out Test Set", test_metrics, calib)

    importances = pd.Series(
        final_model.feature_importances_, index=FEATURE_COLUMNS
    ).sort_values(ascending=False)
    print("\nFeature importances (gain-based):")
    print(importances.head(10))

    # Persist study + params for the serialization step
    import json
    from config import MODELS_DIR
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODELS_DIR / "best_params.json", "w") as f:
        json.dump({
            "params": best_params,
            "n_estimators": best_n_estimators,
            "cv_log_loss": study.best_value,
            "test_metrics": test_metrics,
        }, f, indent=2)
    print(f"\nSaved best params -> {MODELS_DIR / 'best_params.json'}")
