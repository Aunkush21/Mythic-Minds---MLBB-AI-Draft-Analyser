"""
Reuses the trained XGBoost win predictor as a general-purpose draft
evaluator, rather than training a second model. Only invoked once at
least 5 of the other 9 slots are locked in (so the candidate's slot
makes 6/10) — earlier than that, filling unknown slots with placeholders
makes the uplift signal too noisy to trust, so the engine falls back to
the rule-based scores alone (scoring.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "features"))

from build_features import compute_match_row

MIN_LOCKED_SLOTS_FOR_ORACLE = 5
LANES = ["exp", "gold", "mid", "jungle", "roam"]
LANE_MAP = {"exp": "EXP", "gold": "Gold", "mid": "Mid", "jungle": "Jungle", "roam": "Roam"}


def is_oracle_eligible(ally_picks: dict, enemy_picks: dict) -> bool:
    filled = sum(1 for v in ally_picks.values() if v is not None)
    filled += sum(1 for v in enemy_picks.values() if v is not None)
    return filled >= MIN_LOCKED_SLOTS_FOR_ORACLE


def get_placeholder_hero(lane: str, heroes_df, hero_stats_lookup, patch: str, exclude: set[int]) -> int:
    """Deterministic neutral filler: the median-win-rate hero for this lane."""
    from features.utils import nearest_patch_leq  # noqa: F401  (path already on sys.path)
    pool = heroes_df[heroes_df["preferred_lane"] == LANE_MAP[lane]]
    pool = pool[~pool.index.isin(exclude)]
    if pool.empty:
        pool = heroes_df[~heroes_df.index.isin(exclude)]

    stats_patch = patch if patch in hero_stats_lookup else next(iter(hero_stats_lookup), None)
    stats = hero_stats_lookup.get(stats_patch, {})

    win_rates = {hid: stats.get(hid, {}).get("win_rate", 50.0) for hid in pool.index}
    sorted_ids = sorted(win_rates, key=win_rates.get)
    return sorted_ids[len(sorted_ids) // 2]


def fill_placeholders(lane_picks: dict, heroes_df, hero_stats_lookup, patch: str,
                       exclude: set[int]) -> dict:
    filled = dict(lane_picks)
    for lane in LANES:
        if filled.get(lane) is None:
            placeholder = get_placeholder_hero(lane, heroes_df, hero_stats_lookup, patch, exclude)
            filled[lane] = placeholder
            exclude.add(placeholder)
    return filled


def win_prob_uplift(candidate_id: int, target_lane: str, ally_picks: dict, enemy_picks: dict,
                     heroes_df, hero_stats_lookup, counter_lookup, synergy_lookup,
                     patch: str, rank: str, model, feature_columns: list[str]) -> float:
    taken = {h for h in ally_picks.values() if h is not None}
    taken |= {h for h in enemy_picks.values() if h is not None}

    enemy_filled = fill_placeholders(enemy_picks, heroes_df, hero_stats_lookup, patch, set(taken))

    ally_with_candidate = dict(ally_picks)
    ally_with_candidate[target_lane] = candidate_id
    ally_with_candidate = fill_placeholders(
        ally_with_candidate, heroes_df, hero_stats_lookup, patch,
        set(taken) | {candidate_id} | set(enemy_filled.values())
    )

    baseline_hero = get_placeholder_hero(
        target_lane, heroes_df, hero_stats_lookup, patch,
        set(taken) | {candidate_id} | set(enemy_filled.values())
    )
    ally_with_baseline = dict(ally_with_candidate)
    ally_with_baseline[target_lane] = baseline_hero

    row_candidate = compute_match_row(
        ally_with_candidate, enemy_filled, [], [], patch, rank, heroes_df,
        counter_lookup, synergy_lookup, hero_stats_lookup,
    )
    row_baseline = compute_match_row(
        ally_with_baseline, enemy_filled, [], [], patch, rank, heroes_df,
        counter_lookup, synergy_lookup, hero_stats_lookup,
    )

    import pandas as pd
    X = pd.DataFrame([row_candidate, row_baseline])[feature_columns]
    probs = model.predict_proba(X)[:, 1]
    return float(probs[0] - probs[1])
