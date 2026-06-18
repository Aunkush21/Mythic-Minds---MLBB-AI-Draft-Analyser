"""Shared evaluation metrics — used by both the baseline and XGBoost models
so their numbers are directly comparable."""
import numpy as np
from sklearn.metrics import (
    roc_auc_score, log_loss, brier_score_loss,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix,
)


def compute_metrics(y_true, y_prob, threshold: float = 0.5) -> dict:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "roc_auc": roc_auc_score(y_true, y_prob),
        "log_loss": log_loss(y_true, y_prob),
        "brier_score": brier_score_loss(y_true, y_prob),
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }


def calibration_table(y_true, y_prob, n_bins: int = 10) -> list[dict]:
    """Bucket predictions into deciles; compare mean predicted prob to actual win rate."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bins = np.linspace(0, 1, n_bins + 1)
    bin_idx = np.digitize(y_prob, bins[1:-1])

    rows = []
    for b in range(n_bins):
        mask = bin_idx == b
        if mask.sum() == 0:
            continue
        rows.append({
            "bin": f"{bins[b]:.1f}-{bins[b+1]:.1f}",
            "n": int(mask.sum()),
            "mean_predicted": float(y_prob[mask].mean()),
            "actual_win_rate": float(y_true[mask].mean()),
        })
    return rows


def print_report(name: str, metrics: dict, calib: list[dict] | None = None) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {name}")
    print(f"{'=' * 50}")
    for k, v in metrics.items():
        print(f"  {k:14s}: {v:.4f}")
    if calib:
        print(f"\n  Calibration (predicted vs actual win rate):")
        for row in calib:
            print(f"    [{row['bin']}] n={row['n']:4d}  "
                  f"predicted={row['mean_predicted']:.3f}  actual={row['actual_win_rate']:.3f}")
