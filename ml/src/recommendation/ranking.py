"""
Combines per-candidate scores into a single ranked "Best Picks" list.

Critical detail: raw scores have wildly different scales (counter_score
spans roughly ±10, win_rate spans ~45-58) — summing them directly would
let whichever has the larger raw magnitude silently dominate. Every
score is z-scored across the candidate pool *for this request* before
blending.
"""
import pandas as pd

BASE_WEIGHTS = {
    "synergy_score": 0.22,
    "counter_score": 0.22,
    "win_rate": 0.11,
    "pick_rate": 0.04,
    "ban_rate": 0.03,
    "role_gap_bonus": 0.08,        # already in [0,1], not z-scored
    "damage_diversity_bonus": 0.04,  # already in [0,1], not z-scored
    "lane_fit_bonus": 0.11,        # already in [0,1], not z-scored
    "win_prob_uplift": 0.15,
}
Z_SCORED_KEYS = {"synergy_score", "counter_score", "win_rate", "pick_rate", "ban_rate", "win_prob_uplift"}


def _zscore(series: pd.Series) -> pd.Series:
    std = series.std()
    if std == 0 or pd.isna(std):
        return series * 0.0
    return (series - series.mean()) / std


def compute_composite_scores(candidates: list[dict], oracle_used: bool) -> pd.DataFrame:
    df = pd.DataFrame(candidates)

    active_keys = list(BASE_WEIGHTS.keys())
    if not oracle_used:
        active_keys.remove("win_prob_uplift")
        df["win_prob_uplift"] = 0.0

    weight_sum = sum(BASE_WEIGHTS[k] for k in active_keys)
    weights = {k: BASE_WEIGHTS[k] / weight_sum for k in active_keys}

    df["composite_score"] = 0.0
    for key in active_keys:
        col = _zscore(df[key]) if key in Z_SCORED_KEYS else df[key]
        df["composite_score"] += weights[key] * col

    return df.sort_values("composite_score", ascending=False).reset_index(drop=True)
