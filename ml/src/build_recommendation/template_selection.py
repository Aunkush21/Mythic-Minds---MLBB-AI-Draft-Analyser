"""
Tier 1 (curated lookup) and Tier 2 (similarity transfer) of the
confidence cascade. Tier 1 ranks a hero's own curated builds by how well
their `situation` tag matches the computed enemy threat profile. Tier 2
borrows the best-matching build from the most similar hero who has one,
then adapts item types to the requesting hero's damage type/role.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "features"))
from utils import nearest_patch_leq

SIMILARITY_TRANSFER_THRESHOLD = 0.85
ITEM_SLOT_COLS = ["item_1", "item_2", "item_3", "item_4", "item_5", "item_6"]


def situation_match_score(situation: str, threat: dict) -> float:
    if situation == "Standard":
        return 1.0
    if situation == "Anti-Magic":
        return float(threat["magic_count"])
    if situation == "Anti-Tank":
        return float(threat["tank_count"])
    if situation == "Anti-Burst":
        return float(threat["burst_threat_score"])
    return 0.3  # unmapped situation tags (e.g. "Off-Lane") — low default priority


def _resolve_hero_builds(hero_id: int, hero_builds_df: pd.DataFrame, patch: str) -> pd.DataFrame:
    rows = hero_builds_df[hero_builds_df["hero_id"] == hero_id]
    if rows.empty:
        return rows
    available_patches = rows["patch_version"].unique().tolist()
    resolved = nearest_patch_leq(patch, available_patches)
    return rows[rows["patch_version"] == resolved]


def select_best_row(rows: pd.DataFrame, threat: dict) -> pd.Series | None:
    if rows.empty:
        return None
    scored = rows.copy()
    scored["_match"] = scored["situation"].apply(lambda s: situation_match_score(s, threat))
    scored = scored.sort_values(["_match", "win_rate", "games_played"], ascending=False)
    return scored.iloc[0]


def try_tier1(hero_id: int, hero_builds_df: pd.DataFrame, threat: dict, patch: str) -> dict | None:
    rows = _resolve_hero_builds(hero_id, hero_builds_df, patch)
    best = select_best_row(rows, threat)
    if best is None:
        return None
    return {
        "items": [int(best[c]) for c in ITEM_SLOT_COLS],
        "emblem_id": int(best["emblem_id"]),
        "spell_id": int(best["spell_id"]),
        "source": "curated",
        "build_name": best["build_name"],
        "win_rate": float(best["win_rate"]) if pd.notna(best["win_rate"]) else None,
        "games_played": int(best["games_played"]),
    }


def adapt_item_for_hero(item_id: int, target_hero_id: int, heroes_df, items_df, used: set[int]) -> int:
    item = items_df.loc[item_id]
    target = heroes_df.loc[target_hero_id]
    target_physical = target["damage_type"] != "Magic"

    needs_swap = (
        (item["type"] == "Attack" and not target_physical) or
        (item["type"] == "Magic" and target_physical) or
        (item["type"] == "Jungle" and target["preferred_lane"] != "Jungle") or
        (item["type"] == "Roam" and target["preferred_lane"] != "Roam")
    )
    if not needs_swap:
        return item_id

    if item["type"] in ("Jungle", "Roam"):
        replacement_type, sort_col = "Movement", "movement_spd"
    else:
        replacement_type = "Attack" if target_physical else "Magic"
        sort_col = "phys_atk" if target_physical else "magic_pwr"

    pool = items_df[(items_df["type"] == replacement_type) & (~items_df.index.isin(used))]
    if pool.empty:
        return item_id
    return pool.sort_values(sort_col, ascending=False).index[0]


def try_tier2(hero_id: int, heroes_df, hero_builds_df: pd.DataFrame, threat: dict, patch: str,
              similarity_matrix, similarity_hero_ids, items_df) -> dict | None:
    if hero_id not in similarity_hero_ids:
        return None
    idx = similarity_hero_ids.index(hero_id)
    ranked = sorted(
        ((hid, similarity_matrix[idx][j]) for j, hid in enumerate(similarity_hero_ids) if hid != hero_id),
        key=lambda x: x[1], reverse=True,
    )

    for similar_hero_id, sim_score in ranked:
        if sim_score < SIMILARITY_TRANSFER_THRESHOLD:
            break
        rows = _resolve_hero_builds(similar_hero_id, hero_builds_df, patch)
        best = select_best_row(rows, threat)
        if best is None:
            continue

        used: set[int] = set()
        adapted_items = []
        for c in ITEM_SLOT_COLS:
            adapted = adapt_item_for_hero(int(best[c]), hero_id, heroes_df, items_df, used)
            used.add(adapted)
            adapted_items.append(adapted)

        return {
            "items": adapted_items,
            "emblem_id": int(best["emblem_id"]),
            "spell_id": int(best["spell_id"]),
            "source": "similarity_transfer",
            "borrowed_from": heroes_df.loc[similar_hero_id, "name"],
            "similarity": float(sim_score),
            "build_name": best["build_name"],
        }
    return None
