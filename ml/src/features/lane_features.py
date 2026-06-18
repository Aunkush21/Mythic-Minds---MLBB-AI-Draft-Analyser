"""Lane-fit quality: how many picks are in a hero's preferred lane."""
import pandas as pd

LANE_MAP = {"exp": "EXP", "gold": "Gold", "mid": "Mid", "jungle": "Jungle", "roam": "Roam"}


def lane_fit_count(lane_heroes: dict[str, int], heroes_df: pd.DataFrame) -> float:
    fit = 0
    for lane, hero_id in lane_heroes.items():
        preferred = heroes_df.loc[hero_id, "preferred_lane"]
        if preferred == LANE_MAP[lane]:
            fit += 1
    return float(fit)


def ban_meta_pressure(ban_ids: list[int] | None, heroes_df: pd.DataFrame) -> float:
    if not ban_ids:
        return 0.0
    valid = [b for b in ban_ids if b in heroes_df.index]
    if not valid:
        return 0.0
    banned = heroes_df.loc[valid]
    return float(banned["is_op"].sum() + banned["is_meta"].sum())
