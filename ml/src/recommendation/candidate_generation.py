"""
Candidate pool generation: exclude already-picked (either team, since MLBB
disallows mirror picks) and banned heroes, soft-filter to the target lane's
typical hero pool, widening to the full remaining pool if too few qualify.
"""
import pandas as pd

LANE_MAP = {"exp": "EXP", "gold": "Gold", "mid": "Mid", "jungle": "Jungle", "roam": "Roam"}


def generate_candidates(
    heroes_df: pd.DataFrame,
    ally_picks: dict[str, int | None],
    enemy_picks: dict[str, int | None],
    banned_heroes: list[int],
    target_lane: str,
    min_pool_size: int = 8,
) -> list[int]:
    taken = {h for h in ally_picks.values() if h is not None}
    taken |= {h for h in enemy_picks.values() if h is not None}
    taken |= set(banned_heroes)

    remaining = [hid for hid in heroes_df.index if hid not in taken]

    preferred = LANE_MAP.get(target_lane)
    lane_filtered = [
        hid for hid in remaining
        if preferred is not None and heroes_df.loc[hid, "preferred_lane"] == preferred
    ]

    if len(lane_filtered) >= min_pool_size:
        return lane_filtered
    return remaining
