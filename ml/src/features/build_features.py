"""
Orchestrates full feature engineering pipeline:
  1. Computes counter / synergy / meta / composition / lane-fit / ban-pressure
     features for both team orientations of every match (side-symmetry
     augmentation: Blue-as-ally and Red-as-ally are both emitted).
  2. All features are expressed as (ally - enemy) differentials so the
     model is symmetric under side swap by construction.
  3. Emits a `match_id` group column so CV splitting can keep both
     augmented rows of a match together (prevents leakage across folds).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import DATA_RAW_DIR, DATA_PROCESSED_DIR, LANES, RANK_ORDER
from counter_features import build_counter_lookup, counter_advantage
from synergy_features import build_synergy_lookup, team_synergy_sum
from meta_features import build_hero_stats_lookup, team_meta_aggregate, team_composition, ROLES
from lane_features import lane_fit_count, ban_meta_pressure

FEATURE_COLUMNS = [
    "counter_advantage",
    "synergy_diff",
    "winrate_diff", "pickrate_diff", "banrate_diff",
    "op_count_diff", "meta_count_diff",
    "role_diversity_diff",
    *[f"role_{r}_diff" for r in ROLES],
    "damage_physical_diff", "damage_magic_diff",
    "lane_fit_diff",
    "ban_meta_pressure_diff",
    "rank_ordinal",
]


def _side_aggregate(hero_ids, lane_heroes, bans, patch_version, heroes_df,
                     counter_lookup, synergy_lookup, stats_lookup, opp_ids):
    meta = team_meta_aggregate(hero_ids, stats_lookup, patch_version)
    comp = team_composition(hero_ids, heroes_df)
    return {
        "synergy": team_synergy_sum(hero_ids, synergy_lookup, patch_version),
        "winrate": meta["win_rate"],
        "pickrate": meta["pick_rate"],
        "banrate": meta["ban_rate"],
        "op_count": comp["op_count"],
        "meta_count": comp["meta_count"],
        "role_diversity": comp["role_diversity"],
        **{f"role_{r}": comp[f"role_{r}"] for r in ROLES},
        "damage_physical": comp["damage_physical"],
        "damage_magic": comp["damage_magic"],
        "lane_fit": lane_fit_count(lane_heroes, heroes_df),
        "ban_pressure": ban_meta_pressure(bans, heroes_df),
    }


def compute_match_row(ally_lane_heroes, enemy_lane_heroes, ally_bans, enemy_bans,
                       patch_version, rank, heroes_df,
                       counter_lookup, synergy_lookup, stats_lookup):
    ally_ids = list(ally_lane_heroes.values())
    enemy_ids = list(enemy_lane_heroes.values())

    ally_agg = _side_aggregate(ally_ids, ally_lane_heroes, ally_bans, patch_version,
                                heroes_df, counter_lookup, synergy_lookup, stats_lookup, enemy_ids)
    enemy_agg = _side_aggregate(enemy_ids, enemy_lane_heroes, enemy_bans, patch_version,
                                 heroes_df, counter_lookup, synergy_lookup, stats_lookup, ally_ids)

    row = {
        "counter_advantage": counter_advantage(ally_ids, enemy_ids, counter_lookup, patch_version),
        "synergy_diff": ally_agg["synergy"] - enemy_agg["synergy"],
        "winrate_diff": ally_agg["winrate"] - enemy_agg["winrate"],
        "pickrate_diff": ally_agg["pickrate"] - enemy_agg["pickrate"],
        "banrate_diff": ally_agg["banrate"] - enemy_agg["banrate"],
        "op_count_diff": ally_agg["op_count"] - enemy_agg["op_count"],
        "meta_count_diff": ally_agg["meta_count"] - enemy_agg["meta_count"],
        "role_diversity_diff": ally_agg["role_diversity"] - enemy_agg["role_diversity"],
        "damage_physical_diff": ally_agg["damage_physical"] - enemy_agg["damage_physical"],
        "damage_magic_diff": ally_agg["damage_magic"] - enemy_agg["damage_magic"],
        "lane_fit_diff": ally_agg["lane_fit"] - enemy_agg["lane_fit"],
        "ban_pressure_diff": ally_agg["ban_pressure"] - enemy_agg["ban_pressure"],
        "rank_ordinal": float(RANK_ORDER.index(rank)) if rank in RANK_ORDER else -1.0,
    }
    for r in ROLES:
        row[f"role_{r}_diff"] = ally_agg[f"role_{r}"] - enemy_agg[f"role_{r}"]

    # ban_pressure_diff was computed but renamed in FEATURE_COLUMNS as ban_meta_pressure_diff
    row["ban_meta_pressure_diff"] = row.pop("ban_pressure_diff")
    return row


def build_dataset(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    matches = tables["matches"]
    heroes_df = tables["heroes"].set_index("id")
    counter_lookup = build_counter_lookup(tables["counters"])
    synergy_lookup = build_synergy_lookup(tables["synergies"])
    stats_lookup = build_hero_stats_lookup(tables["hero_stats"])

    rows = []
    for m in matches.itertuples():
        blue_lanes = {lane: getattr(m, f"blue_{lane}") for lane in LANES}
        red_lanes = {lane: getattr(m, f"red_{lane}") for lane in LANES}
        blue_bans = list(m.blue_bans) if m.blue_bans is not None else []
        red_bans = list(m.red_bans) if m.red_bans is not None else []

        # Orientation 1: Blue = ally
        feat = compute_match_row(blue_lanes, red_lanes, blue_bans, red_bans,
                                  m.patch_version, m.rank, heroes_df,
                                  counter_lookup, synergy_lookup, stats_lookup)
        feat["match_id"] = m.match_id
        feat["ally_win"] = 1 if m.winner == "Blue" else 0
        rows.append(feat)

        # Orientation 2: Red = ally (side-symmetry augmentation)
        feat2 = compute_match_row(red_lanes, blue_lanes, red_bans, blue_bans,
                                   m.patch_version, m.rank, heroes_df,
                                   counter_lookup, synergy_lookup, stats_lookup)
        feat2["match_id"] = m.match_id
        feat2["ally_win"] = 1 if m.winner == "Red" else 0
        rows.append(feat2)

    df = pd.DataFrame(rows)
    return df[["match_id", "ally_win"] + FEATURE_COLUMNS]


if __name__ == "__main__":
    tables = {
        "matches": pd.read_parquet(DATA_RAW_DIR / "matches.parquet"),
        "heroes": pd.read_parquet(DATA_RAW_DIR / "heroes.parquet"),
        "hero_stats": pd.read_parquet(DATA_RAW_DIR / "hero_stats.parquet"),
        "counters": pd.read_parquet(DATA_RAW_DIR / "counters.parquet"),
        "synergies": pd.read_parquet(DATA_RAW_DIR / "synergies.parquet"),
    }
    dataset = build_dataset(tables)

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_PROCESSED_DIR / "features.parquet"
    dataset.to_parquet(out_path, index=False)

    print(f"Built feature dataset: {dataset.shape[0]} rows x {dataset.shape[1]} columns")
    print(f"Saved to {out_path}")
    print(f"\nLabel balance:\n{dataset['ally_win'].value_counts(normalize=True)}")
    print(f"\nFeature summary:\n{dataset[FEATURE_COLUMNS].describe().T[['mean', 'std', 'min', 'max']]}")

    # Sanity check: verify symmetry — for each match_id, the two augmented
    # rows' features should be exact negatives of each other.
    sample_id = dataset["match_id"].iloc[0]
    pair = dataset[dataset["match_id"] == sample_id][FEATURE_COLUMNS[:-1]]  # exclude rank (not differential)
    diff_check = (pair.iloc[0] + pair.iloc[1]).abs().max()
    print(f"\nSymmetry check (should be ~0): max|f_ally + f_enemy| = {diff_check:.6f}")
