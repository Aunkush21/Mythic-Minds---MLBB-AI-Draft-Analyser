"""
Per-candidate rule-based scores: synergy, counter, meta strength,
role-gap bonus, damage-type diversity bonus. These are well-defined at
any draft stage (even with zero allies/enemies picked), which is why
they're the primary signal — the win-prediction oracle (oracle.py) only
supplements them once enough of the draft is locked in.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "features"))

from counter_features import counter_advantage
from synergy_features import team_synergy_sum
from meta_features import team_meta_aggregate

LANE_MAP = {"exp": "EXP", "gold": "Gold", "mid": "Mid", "jungle": "Jungle", "roam": "Roam"}


def candidate_counter_score(candidate_id: int, enemy_ids: list[int], counter_lookup, patch: str) -> float:
    if not enemy_ids:
        return 0.0
    return counter_advantage([candidate_id], enemy_ids, counter_lookup, patch)


def candidate_synergy_score(candidate_id: int, ally_ids: list[int], synergy_lookup, patch: str) -> float:
    if not ally_ids:
        return 0.0
    with_candidate = team_synergy_sum(ally_ids + [candidate_id], synergy_lookup, patch)
    without_candidate = team_synergy_sum(ally_ids, synergy_lookup, patch)
    return with_candidate - without_candidate


def candidate_meta_score(candidate_id: int, hero_stats_lookup, patch: str) -> dict:
    return team_meta_aggregate([candidate_id], hero_stats_lookup, patch)


def role_gap_bonus(candidate_id: int, ally_ids: list[int], heroes_df) -> float:
    if not ally_ids:
        return 0.0
    ally_roles = set(heroes_df.loc[ally_ids, "role"])
    candidate_role = heroes_df.loc[candidate_id, "role"]
    return 1.0 if candidate_role not in ally_roles else 0.0


def lane_fit_bonus(candidate_id: int, target_lane: str, heroes_df) -> float:
    return 1.0 if heroes_df.loc[candidate_id, "preferred_lane"] == LANE_MAP[target_lane] else 0.0


def damage_diversity_bonus(candidate_id: int, ally_ids: list[int], heroes_df) -> float:
    candidate_type = heroes_df.loc[candidate_id, "damage_type"]
    if candidate_type == "Hybrid":
        return 0.25
    if not ally_ids:
        return 0.5

    ally_types = heroes_df.loc[ally_ids, "damage_type"]
    physical_count = (ally_types == "Physical").sum()
    magic_count = (ally_types == "Magic").sum()

    if physical_count == magic_count:
        return 0.5
    if physical_count > magic_count and candidate_type == "Magic":
        return 1.0
    if magic_count > physical_count and candidate_type == "Physical":
        return 1.0
    return 0.0
