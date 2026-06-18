"""
Counter-pick advantage feature.

hero_counters schema: (hero_id, countered_by_id, counter_score) means
`countered_by_id` counters `hero_id`. For a 5v5 matchup, the net counter
advantage is: (sum of ally heroes countering enemy heroes) minus
(sum of enemy heroes countering ally heroes).
"""
import pandas as pd

from utils import nearest_patch_leq


def build_counter_lookup(counters_df: pd.DataFrame) -> dict[str, dict[tuple[int, int], float]]:
    lookup: dict[str, dict[tuple[int, int], float]] = {}
    for patch, group in counters_df.groupby("patch_version"):
        lookup[patch] = {
            (row.hero_id, row.countered_by_id): row.counter_score
            for row in group.itertuples()
        }
    return lookup


def counter_advantage(
    ally_ids: list[int],
    enemy_ids: list[int],
    lookup: dict[str, dict[tuple[int, int], float]],
    patch_version: str,
) -> float:
    if not lookup:
        return 0.0
    patch = nearest_patch_leq(patch_version, list(lookup.keys()))
    table = lookup[patch]

    ally_counters_enemy = sum(
        table.get((enemy, ally), 0.0) for ally in ally_ids for enemy in enemy_ids
    )
    enemy_counters_ally = sum(
        table.get((ally, enemy), 0.0) for ally in ally_ids for enemy in enemy_ids
    )
    return ally_counters_enemy - enemy_counters_ally
