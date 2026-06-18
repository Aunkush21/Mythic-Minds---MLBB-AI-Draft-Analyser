"""
Tier 3 fallback: pure role/damage-type domain heuristics, used only when
no curated build exists for the hero AND no sufficiently similar hero
has one either. No historical win-rate signal backs this tier — it's
the safety net that guarantees the engine never returns nothing.
"""
import pandas as pd

LANE_TO_EMBLEM_TYPE = {
    "EXP": "Fighter", "Jungle": "Assassin", "Mid": "Mage",
    "Gold": "Marksman", "Roam": "Tank",
}


def _best_item(items_df: pd.DataFrame, item_type: str, sort_col: str, exclude: set[int]) -> int:
    pool = items_df[(items_df["type"] == item_type) & (~items_df.index.isin(exclude))]
    if pool.empty:
        pool = items_df[~items_df.index.isin(exclude)]
    return pool.sort_values(sort_col, ascending=False).index[0]


def build_role_default(hero_id: int, heroes_df: pd.DataFrame, items_df: pd.DataFrame,
                        emblems_df: pd.DataFrame, spells_df: pd.DataFrame) -> dict:
    hero = heroes_df.loc[hero_id]
    is_physical = hero["damage_type"] != "Magic"
    used: set[int] = set()

    core_type = "Attack" if is_physical else "Magic"
    core_sort = "phys_atk" if is_physical else "magic_pwr"
    core_item = _best_item(items_df, core_type, core_sort, used)
    used.add(core_item)

    pen_sort = "phys_pen" if is_physical else "magic_pen"
    pen_item = _best_item(items_df, core_type, pen_sort, used)
    used.add(pen_item)

    sustain_item = _best_item(items_df, "Attack", "lifesteal", used) if is_physical else \
        _best_item(items_df, "Magic", "max_hp", used)
    used.add(sustain_item)

    boots = _best_item(items_df, "Movement", "movement_spd", used)
    used.add(boots)

    defense_item = _best_item(items_df, "Defense", "magic_def" if not is_physical else "phys_def", used)
    used.add(defense_item)

    filler = _best_item(items_df, core_type, core_sort, used)
    used.add(filler)

    items = [core_item, pen_item, sustain_item, boots, defense_item, filler]

    emblem_type = LANE_TO_EMBLEM_TYPE.get(hero["preferred_lane"], "Common")
    emblem_match = emblems_df[emblems_df["type"] == emblem_type]
    emblem_id = emblem_match.index[0] if not emblem_match.empty else emblems_df.index[0]

    spell_id = spells_df[spells_df["name"] == "Retribution"].index[0] \
        if hero["preferred_lane"] == "Jungle" else \
        spells_df[spells_df["name"] == "Flicker"].index[0]

    return {
        "items": items,
        "emblem_id": int(emblem_id),
        "spell_id": int(spell_id),
        "source": "role_default",
    }