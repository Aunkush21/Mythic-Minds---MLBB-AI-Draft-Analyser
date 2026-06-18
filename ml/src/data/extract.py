"""
Pulls match drafts + results from Postgres into a flat dataframe.
Only draft-time columns are selected from match_results (winner) —
performance stats (kills/gold/turrets/etc.) are intentionally excluded
to prevent outcome leakage into a draft-time predictor.
"""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import DATABASE_URL, DATA_RAW_DIR

MATCH_QUERY = """
    SELECT
        d.match_id,
        d.patch_version,
        d.rank,
        d.blue_exp, d.blue_gold, d.blue_mid, d.blue_jungle, d.blue_roam,
        d.red_exp,  d.red_gold,  d.red_mid,  d.red_jungle,  d.red_roam,
        d.blue_bans, d.red_bans,
        r.winner
    FROM match_drafts d
    JOIN match_results r ON d.match_id = r.match_id
"""

HEROES_QUERY = """
    SELECT id, name, role, secondary_role, specialty, damage_type,
           preferred_lane, difficulty, is_meta, is_op
    FROM heroes
"""

HERO_STATS_QUERY = """
    SELECT hero_id, patch_version, win_rate, pick_rate, ban_rate
    FROM hero_stats
"""

COUNTERS_QUERY = """
    SELECT hero_id, countered_by_id, counter_score, patch_version
    FROM hero_counters
"""

SYNERGIES_QUERY = """
    SELECT hero_a_id, hero_b_id, synergy_score, patch_version
    FROM hero_synergies
"""

PATCHES_QUERY = """
    SELECT patch_version, release_date, is_current
    FROM patch_history
"""

ITEMS_QUERY = """
    SELECT id, name, type, tier, cost, phys_atk, magic_pwr, phys_def, magic_def,
           max_hp, hp_regen, mana, mana_regen, crit_chance, atk_speed, lifesteal,
           movement_spd, phys_pen, magic_pen, cooldown_red, passive_name,
           passive_desc, is_active, active_desc, patch_version
    FROM items
"""

EMBLEMS_QUERY = """
    SELECT id, name, type, phys_atk_bonus, magic_pwr_bonus, hp_bonus,
           armor_bonus, magic_res_bonus, cdr_bonus, movement_bonus,
           talent_1, talent_2, talent_3, recommended_roles
    FROM emblems
"""

BATTLE_SPELLS_QUERY = """
    SELECT id, name, description, cooldown, unlock_level,
           recommended_roles, recommended_lanes, use_case, patch_version
    FROM battle_spells
"""

HERO_BUILDS_QUERY = """
    SELECT id, hero_id, build_name, item_1, item_2, item_3, item_4, item_5, item_6,
           emblem_id, spell_id, is_core, situation, patch_version, win_rate, games_played
    FROM hero_builds
"""


def fetch_all() -> dict[str, pd.DataFrame]:
    engine = create_engine(DATABASE_URL)
    try:
        matches    = pd.read_sql(MATCH_QUERY, engine)
        heroes     = pd.read_sql(HEROES_QUERY, engine)
        hero_stats = pd.read_sql(HERO_STATS_QUERY, engine)
        counters   = pd.read_sql(COUNTERS_QUERY, engine)
        synergies  = pd.read_sql(SYNERGIES_QUERY, engine)
        patches    = pd.read_sql(PATCHES_QUERY, engine)
        items      = pd.read_sql(ITEMS_QUERY, engine)
        emblems    = pd.read_sql(EMBLEMS_QUERY, engine)
        spells     = pd.read_sql(BATTLE_SPELLS_QUERY, engine)
        hero_builds = pd.read_sql(HERO_BUILDS_QUERY, engine)
    finally:
        engine.dispose()
    return {
        "matches": matches,
        "heroes": heroes,
        "hero_stats": hero_stats,
        "counters": counters,
        "synergies": synergies,
        "patches": patches,
        "items": items,
        "emblems": emblems,
        "spells": spells,
        "hero_builds": hero_builds,
    }


def save_raw(tables: dict[str, pd.DataFrame]) -> None:
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        path = DATA_RAW_DIR / f"{name}.parquet"
        df.to_parquet(path, index=False)
        print(f"  {name}: {len(df)} rows -> {path.relative_to(DATA_RAW_DIR.parents[2])}")


if __name__ == "__main__":
    print("Extracting tables from Postgres...")
    tables = fetch_all()
    save_raw(tables)

    matches = tables["matches"]
    print(f"\nTotal matches: {len(matches)}")
    print(f"Winner distribution:\n{matches['winner'].value_counts()}")
    print(f"\nMissing values per column:\n{matches.isnull().sum()[matches.isnull().sum() > 0]}")
