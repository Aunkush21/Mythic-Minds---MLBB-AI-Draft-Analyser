"""Pairwise intra-team synergy aggregation."""
import itertools

import pandas as pd

from utils import nearest_patch_leq


def build_synergy_lookup(synergies_df: pd.DataFrame) -> dict[str, dict[tuple[int, int], float]]:
    lookup: dict[str, dict[tuple[int, int], float]] = {}
    for patch, group in synergies_df.groupby("patch_version"):
        lookup[patch] = {
            (row.hero_a_id, row.hero_b_id): row.synergy_score
            for row in group.itertuples()
        }
    return lookup


def team_synergy_sum(
    hero_ids: list[int],
    lookup: dict[str, dict[tuple[int, int], float]],
    patch_version: str,
) -> float:
    if not lookup:
        return 0.0
    patch = nearest_patch_leq(patch_version, list(lookup.keys()))
    table = lookup[patch]

    total = 0.0
    for a, b in itertools.combinations(sorted(hero_ids), 2):
        total += table.get((a, b), 0.0)
    return total
