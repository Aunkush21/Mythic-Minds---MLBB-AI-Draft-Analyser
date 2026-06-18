"""
Master database seeder — runs all seed scripts in order.
Usage: python seed_all.py

Requires:
    pip install psycopg2-binary python-dotenv
    DATABASE_URL in .env or environment
"""

import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

# Allow importing sibling seed modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "seed"))

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from patches import PATCHES
from heroes import HEROES, HERO_STATS
from items import ITEMS
from emblems_spells import EMBLEMS, BATTLE_SPELLS
from relationships import COUNTERS, SYNERGIES, HERO_BUILDS
from matches import generate_matches

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in environment or .env file")
    sys.exit(1)


def get_conn():
    return psycopg2.connect(DATABASE_URL)


# ──────────────────────────────────────────────────────────────────────────────
def seed_patches(cur):
    print("  Seeding patch_history...")
    execute_values(cur, """
        INSERT INTO patch_history
            (id, patch_version, release_date, codename, summary,
             heroes_added, heroes_reworked, is_current)
        VALUES %s
        ON CONFLICT (patch_version) DO NOTHING
    """, [(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]) for p in PATCHES],
        template="(%s,%s,%s,%s,%s,%s::text[],%s::text[],%s)")
    print(f"    -> {len(PATCHES)} patches inserted.")


def seed_heroes(cur):
    print("  Seeding heroes...")
    execute_values(cur, """
        INSERT INTO heroes
            (id, name, role, secondary_role, specialty, damage_type,
             preferred_lane, difficulty, is_meta, is_op)
        VALUES %s
        ON CONFLICT (name) DO NOTHING
    """, [(h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7], h[8], h[9])
          for h in HEROES],
        template="(%s,%s,%s::hero_role,%s::hero_role,%s::hero_specialty,%s::damage_type,%s::lane_type,%s,%s,%s)")
    print(f"    -> {len(HEROES)} heroes inserted.")


def seed_hero_stats(cur):
    print("  Seeding hero_stats...")
    execute_values(cur, """
        INSERT INTO hero_stats
            (hero_id, patch_version, base_hp, base_mana, base_armor,
             base_magic_res, base_atk_spd, base_phys_atk, base_magic_pwr,
             movement_spd, hp_growth, armor_growth, atk_growth,
             win_rate, pick_rate, ban_rate)
        VALUES %s
        ON CONFLICT (hero_id, patch_version) DO NOTHING
    """, [(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8],
           s[9], s[10], s[11], s[12], s[13], s[14], s[15])
          for s in HERO_STATS])
    print(f"    -> {len(HERO_STATS)} stat rows inserted.")


def seed_items(cur):
    print("  Seeding items...")
    execute_values(cur, """
        INSERT INTO items
            (id, name, type, tier, cost, phys_atk, magic_pwr, phys_def,
             magic_def, max_hp, hp_regen, mana, mana_regen, crit_chance,
             atk_speed, lifesteal, movement_spd, phys_pen, magic_pen,
             cooldown_red, passive_name, passive_desc, is_active, patch_version)
        VALUES %s
        ON CONFLICT (name) DO NOTHING
    """, [(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9],
           i[10], i[11], i[12], i[13], i[14], i[15], i[16], i[17], i[18],
           i[19], i[20], i[21], i[22], i[23])
          for i in ITEMS])
    print(f"    -> {len(ITEMS)} items inserted.")


def seed_emblems(cur):
    print("  Seeding emblems...")
    execute_values(cur, """
        INSERT INTO emblems
            (id, name, type, phys_atk_bonus, magic_pwr_bonus, hp_bonus,
             armor_bonus, magic_res_bonus, cdr_bonus, movement_bonus,
             talent_1, talent_2, talent_3, recommended_roles)
        VALUES %s
        ON CONFLICT (name) DO NOTHING
    """, [(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9],
           e[10], e[11], e[12], e[13])
          for e in EMBLEMS],
        template="(%s,%s,%s::emblem_type,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::hero_role[])")
    print(f"    -> {len(EMBLEMS)} emblems inserted.")


def seed_spells(cur):
    print("  Seeding battle_spells...")
    execute_values(cur, """
        INSERT INTO battle_spells
            (id, name, description, cooldown, unlock_level,
             recommended_roles, recommended_lanes, use_case, patch_version)
        VALUES %s
        ON CONFLICT (name) DO NOTHING
    """, [(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8])
          for s in BATTLE_SPELLS],
        template="(%s,%s,%s,%s,%s,%s::hero_role[],%s::lane_type[],%s,%s)")
    print(f"    -> {len(BATTLE_SPELLS)} battle spells inserted.")


def seed_counters(cur):
    print("  Seeding hero_counters...")
    execute_values(cur, """
        INSERT INTO hero_counters
            (hero_id, countered_by_id, counter_score, reason, patch_version)
        VALUES %s
        ON CONFLICT (hero_id, countered_by_id, patch_version) DO NOTHING
    """, [(c[0], c[1], c[2], c[3], "1.9.0") for c in COUNTERS])
    print(f"    -> {len(COUNTERS)} counter relationships inserted.")


def seed_synergies(cur):
    print("  Seeding hero_synergies...")
    execute_values(cur, """
        INSERT INTO hero_synergies
            (hero_a_id, hero_b_id, synergy_score, combo_name, reason, patch_version)
        VALUES %s
        ON CONFLICT (hero_a_id, hero_b_id, patch_version) DO NOTHING
    """, [(s[0], s[1], s[2], s[3], s[4], "1.9.0") for s in SYNERGIES])
    print(f"    -> {len(SYNERGIES)} synergy pairs inserted.")


def seed_builds(cur):
    print("  Seeding hero_builds...")
    execute_values(cur, """
        INSERT INTO hero_builds
            (hero_id, build_name, item_1, item_2, item_3, item_4, item_5, item_6,
             emblem_id, spell_id, situation, patch_version, win_rate, games_played)
        VALUES %s
        ON CONFLICT (hero_id, build_name, patch_version) DO NOTHING
    """, [(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7],
           b[8], b[9], b[10], b[11], b[12], b[13])
          for b in HERO_BUILDS])
    print(f"    -> {len(HERO_BUILDS)} builds inserted.")


def seed_matches(cur, n: int = 500):
    print(f"  Generating {n} synthetic matches...")
    drafts, results = generate_matches(n)

    execute_values(cur, """
        INSERT INTO match_drafts
            (match_id, patch_version, rank,
             blue_exp, blue_gold, blue_mid, blue_jungle, blue_roam,
             red_exp,  red_gold,  red_mid,  red_jungle,  red_roam,
             blue_bans, red_bans)
        VALUES %s
        ON CONFLICT (match_id) DO NOTHING
    """, [(d["match_id"], d["patch_version"], d["rank"],
           d["blue_exp"], d["blue_gold"], d["blue_mid"],
           d["blue_jungle"], d["blue_roam"],
           d["red_exp"],  d["red_gold"],  d["red_mid"],
           d["red_jungle"], d["red_roam"],
           d["blue_bans"], d["red_bans"])
          for d in drafts])

    execute_values(cur, """
        INSERT INTO match_results
            (match_id, winner, match_duration,
             blue_kills, blue_deaths, blue_assists, blue_turrets,
             blue_lords, blue_turtles, blue_gold_total,
             red_kills,  red_deaths,  red_assists,  red_turrets,
             red_lords,  red_turtles,  red_gold_total,
             first_blood_side, first_turret_side,
             first_lord_side, first_turtle_side)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, [(r["match_id"], r["winner"], r["match_duration"],
           r["blue_kills"], r["blue_deaths"], r["blue_assists"],
           r["blue_turrets"], r["blue_lords"], r["blue_turtles"], r["blue_gold_total"],
           r["red_kills"],  r["red_deaths"],  r["red_assists"],
           r["red_turrets"],  r["red_lords"],  r["red_turtles"],  r["red_gold_total"],
           r["first_blood_side"], r["first_turret_side"],
           r["first_lord_side"],  r["first_turtle_side"])
          for r in results])

    print(f"    -> {len(drafts)} match drafts inserted.")
    print(f"    -> {len(results)} match results inserted.")


# ──────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("MLBB AI Platform — Database Seeder")
    print("=" * 60)

    conn = get_conn()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            seed_patches(cur)
            seed_heroes(cur)
            seed_hero_stats(cur)
            seed_items(cur)
            seed_emblems(cur)
            seed_spells(cur)
            seed_counters(cur)
            seed_synergies(cur)
            seed_builds(cur)
            seed_matches(cur, n=500)

        conn.commit()
        print("\n✓ All data seeded successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error during seeding: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
