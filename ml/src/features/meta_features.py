"""Team-level meta strength, role composition, and damage-type balance."""
import pandas as pd

from utils import nearest_patch_leq

ROLES = ["Tank", "Fighter", "Assassin", "Mage", "Marksman", "Support"]


def build_hero_stats_lookup(hero_stats_df: pd.DataFrame) -> dict[str, dict[int, dict]]:
    lookup: dict[str, dict[int, dict]] = {}
    for patch, group in hero_stats_df.groupby("patch_version"):
        lookup[patch] = {
            row.hero_id: {
                "win_rate": row.win_rate,
                "pick_rate": row.pick_rate,
                "ban_rate": row.ban_rate,
            }
            for row in group.itertuples()
        }
    return lookup


def team_meta_aggregate(
    hero_ids: list[int],
    lookup: dict[str, dict[int, dict]],
    patch_version: str,
) -> dict[str, float]:
    if not lookup:
        return {"win_rate": 0.0, "pick_rate": 0.0, "ban_rate": 0.0}
    patch = nearest_patch_leq(patch_version, list(lookup.keys()))
    table = lookup[patch]

    rows = [table[h] for h in hero_ids if h in table]
    if not rows:
        return {"win_rate": 0.0, "pick_rate": 0.0, "ban_rate": 0.0}

    n = len(rows)
    return {
        "win_rate": sum(r["win_rate"] for r in rows) / n,
        "pick_rate": sum(r["pick_rate"] for r in rows) / n,
        "ban_rate": sum(r["ban_rate"] for r in rows) / n,
    }


def team_composition(hero_ids: list[int], heroes_df: pd.DataFrame) -> dict[str, float]:
    """Role counts, damage-type balance, OP/meta density, role diversity."""
    team = heroes_df.loc[hero_ids]

    role_counts = {f"role_{r}": float((team["role"] == r).sum()) for r in ROLES}
    damage_counts = {
        "damage_physical": float((team["damage_type"] == "Physical").sum()),
        "damage_magic": float((team["damage_type"] == "Magic").sum()),
    }
    op_count = float(team["is_op"].sum())
    meta_count = float(team["is_meta"].sum())
    role_diversity = float(team["role"].nunique())

    return {
        **role_counts,
        **damage_counts,
        "op_count": op_count,
        "meta_count": meta_count,
        "role_diversity": role_diversity,
    }
