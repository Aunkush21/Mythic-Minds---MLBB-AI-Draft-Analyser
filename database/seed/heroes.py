"""
Hero master data — 40 heroes covering all roles and lanes.
Data reflects MLBB patch 1.9.0 meta.
"""

HEROES = [
    # id, name, role, secondary_role, specialty, damage_type, preferred_lane, difficulty, is_meta, is_op
    # ── TANKS ──────────────────────────────────────────────────────────────────
    (1,  "Tigreal",   "Tank",     None,        "Crowd Control", "Physical", "Roam",   3,  False, False),
    (2,  "Atlas",     "Tank",     None,        "Initiator",     "Physical", "Roam",   7,  True,  False),
    (3,  "Franco",    "Tank",     None,        "Crowd Control", "Physical", "Roam",   5,  True,  False),
    (4,  "Khufra",    "Tank",     "Fighter",   "Crowd Control", "Physical", "Roam",   6,  True,  True),
    (5,  "Gloo",      "Tank",     None,        "Crowd Control", "Physical", "Roam",   7,  True,  False),
    (6,  "Johnson",   "Tank",     "Support",   "Initiator",     "Physical", "Roam",   5,  False, False),
    (7,  "Akai",      "Tank",     None,        "Crowd Control", "Physical", "Roam",   5,  True,  False),
    (8,  "Hylos",     "Tank",     None,        "Guard",         "Magic",    "Roam",   4,  False, False),

    # ── FIGHTERS ───────────────────────────────────────────────────────────────
    (9,  "Fredrinn",  "Fighter",  "Tank",      "Damage",        "Physical", "EXP",    5,  True,  True),
    (10, "Yu Zhong",  "Fighter",  None,        "Damage",        "Physical", "EXP",    6,  True,  False),
    (11, "Paquito",   "Fighter",  None,        "Damage",        "Physical", "EXP",    8,  True,  True),
    (12, "Khaleed",   "Fighter",  None,        "Damage",        "Physical", "EXP",    5,  True,  False),
    (13, "Badang",    "Fighter",  None,        "Crowd Control", "Physical", "EXP",    4,  False, False),
    (14, "Thamuz",    "Fighter",  None,        "Reap",          "Physical", "EXP",    5,  True,  False),
    (15, "Dyrroth",   "Fighter",  None,        "Damage",        "Physical", "EXP",    5,  True,  True),
    (16, "Masha",     "Fighter",  "Tank",      "Damage",        "Physical", "EXP",    5,  False, False),

    # ── ASSASSINS ──────────────────────────────────────────────────────────────
    (17, "Ling",      "Assassin", None,        "Reap",          "Physical", "Jungle", 10, True,  True),
    (18, "Lancelot",  "Assassin", None,        "Reap",          "Physical", "Jungle", 9,  True,  False),
    (19, "Fanny",     "Assassin", None,        "Reap",          "Physical", "Jungle", 10, True,  False),
    (20, "Hayabusa",  "Assassin", None,        "Reap",          "Physical", "Jungle", 8,  False, False),
    (21, "Gusion",    "Assassin", "Mage",      "Reap",          "Magic",    "Jungle", 9,  True,  False),
    (22, "Joy",       "Assassin", None,        "Reap",          "Physical", "Jungle", 7,  True,  True),
    (23, "Karina",    "Assassin", "Mage",      "Reap",          "Magic",    "Jungle", 5,  False, False),

    # ── MAGES ──────────────────────────────────────────────────────────────────
    (24, "Kagura",    "Mage",     None,        "Poke",          "Magic",    "Mid",    9,  True,  False),
    (25, "Lunox",     "Mage",     None,        "Damage",        "Magic",    "Mid",    8,  True,  False),
    (26, "Vale",      "Mage",     None,        "Crowd Control", "Magic",    "Mid",    6,  True,  False),
    (27, "Valentina", "Mage",     None,        "Damage",        "Magic",    "Mid",    8,  True,  True),
    (28, "Xavier",    "Mage",     None,        "Poke",          "Magic",    "Mid",    5,  True,  False),
    (29, "Yve",       "Mage",     None,        "Poke",          "Magic",    "Mid",    6,  False, False),
    (30, "Cecilion",  "Mage",     None,        "Damage",        "Magic",    "Mid",    5,  False, False),

    # ── MARKSMEN ───────────────────────────────────────────────────────────────
    (31, "Beatrix",   "Marksman", None,        "Damage",        "Physical", "Gold",   9,  True,  True),
    (32, "Melissa",   "Marksman", None,        "Damage",        "Physical", "Gold",   6,  True,  False),
    (33, "Karrie",    "Marksman", None,        "Reap",          "Physical", "Gold",   6,  True,  False),
    (34, "Brody",     "Marksman", None,        "Damage",        "Physical", "Gold",   6,  True,  False),
    (35, "Clint",     "Marksman", None,        "Reap",          "Physical", "Gold",   5,  False, False),
    (36, "Granger",   "Marksman", None,        "Reap",          "Physical", "Gold",   7,  True,  False),
    (37, "Hanabi",    "Marksman", None,        "Crowd Control", "Physical", "Gold",   4,  False, False),

    # ── SUPPORTS ───────────────────────────────────────────────────────────────
    (38, "Floryn",    "Support",  None,        "Heal",          "Magic",    "Roam",   5,  True,  False),
    (39, "Estes",     "Support",  None,        "Heal",          "Magic",    "Roam",   5,  False, False),
    (40, "Mathilda",  "Support",  "Assassin",  "Support",       "Magic",    "Roam",   7,  True,  True),
]

HERO_STATS = [
    # hero_id, patch, base_hp, base_mana, armor, magic_res, atk_spd, phys_atk, magic_pwr, move_spd, hp_growth, armor_growth, atk_growth, win_rate, pick_rate, ban_rate
    (1,  "1.9.0", 2971, 480,  27.0, 10.0, 0.830, 114, 0,  240, 289.4, 2.1,  5.0,  50.1, 4.2,  1.0),
    (2,  "1.9.0", 2971, 0,    27.0, 15.0, 0.800, 107, 0,  240, 315.0, 2.5,  4.0,  51.8, 5.1,  8.2),
    (3,  "1.9.0", 2971, 0,    24.0, 10.0, 0.800, 120, 0,  240, 350.0, 1.8,  6.0,  48.9, 6.3,  3.1),
    (4,  "1.9.0", 2971, 0,    28.0, 15.0, 0.800, 117, 0,  240, 330.0, 2.3,  5.5,  53.2, 8.5, 15.6),
    (5,  "1.9.0", 2971, 0,    25.0, 15.0, 0.800, 107, 0,  240, 300.0, 2.4,  4.0,  52.0, 6.8,  9.3),
    (6,  "1.9.0", 2971, 0,    24.0, 10.0, 0.830, 110, 0,  240, 305.0, 1.9,  4.5,  49.5, 3.9,  2.1),
    (7,  "1.9.0", 2971, 0,    27.0, 10.0, 0.800, 107, 0,  240, 320.0, 2.2,  4.0,  51.3, 5.7,  4.8),
    (8,  "1.9.0", 3226, 600,  25.0, 10.0, 0.800, 107, 0,  240, 350.0, 2.0,  3.5,  50.4, 2.1,  0.5),
    (9,  "1.9.0", 2900, 0,    24.0, 15.0, 1.000, 134, 0,  255, 301.0, 2.1,  7.0,  54.8, 9.2, 12.1),
    (10, "1.9.0", 2900, 0,    20.0, 15.0, 1.000, 120, 0,  255, 290.0, 1.8,  6.5,  52.1, 7.3,  8.4),
    (11, "1.9.0", 2725, 0,    24.0, 15.0, 1.000, 130, 0,  260, 280.0, 2.0,  7.5,  55.3,10.1, 18.4),
    (12, "1.9.0", 2725, 0,    22.0, 15.0, 1.000, 125, 0,  255, 275.0, 1.9,  7.0,  53.0, 8.1,  7.2),
    (13, "1.9.0", 2620, 0,    22.0, 10.0, 1.000, 120, 0,  255, 265.0, 1.8,  6.0,  48.5, 4.2,  2.0),
    (14, "1.9.0", 2900, 0,    22.0, 15.0, 1.000, 128, 0,  255, 285.0, 2.0,  6.5,  52.6, 7.9,  6.3),
    (15, "1.9.0", 2725, 0,    22.0, 15.0, 1.000, 130, 0,  255, 278.0, 2.0,  7.2,  54.0, 9.5, 14.2),
    (16, "1.9.0", 3900, 0,    20.0, 15.0, 1.000, 115, 0,  260, 380.0, 1.5,  5.0,  49.0, 3.5,  1.2),
    (17, "1.9.0", 2517, 0,    18.0, 15.0, 1.200, 152, 0,  255, 230.0, 1.8,  8.5,  56.2,11.3, 22.7),
    (18, "1.9.0", 2517, 0,    18.0, 15.0, 1.100, 144, 0,  260, 225.0, 1.7,  8.0,  52.8, 8.6, 11.5),
    (19, "1.9.0", 2447, 600,  16.0, 15.0, 1.100, 140, 0,  255, 215.0, 1.6,  7.5,  54.1, 6.2, 16.8),
    (20, "1.9.0", 2397, 0,    18.0, 10.0, 1.100, 137, 0,  255, 220.0, 1.6,  7.0,  49.8, 5.1,  5.3),
    (21, "1.9.0", 2397, 450,  16.0, 15.0, 1.050, 115, 60, 260, 215.0, 1.5,  5.0,  53.5, 7.4, 10.2),
    (22, "1.9.0", 2517, 0,    18.0, 15.0, 1.200, 148, 0,  265, 230.0, 1.8,  8.2,  55.8,10.5, 20.1),
    (23, "1.9.0", 2397, 450,  16.0, 10.0, 1.050, 110, 50, 255, 210.0, 1.4,  4.5,  50.2, 4.8,  3.2),
    (24, "1.9.0", 2329, 550,  14.0, 10.0, 0.830, 100,150, 250, 195.0, 1.2,  3.0,  54.9, 8.9, 13.6),
    (25, "1.9.0", 2329, 500,  14.0, 10.0, 0.800,  95,130, 250, 192.0, 1.1,  2.8,  53.7, 7.5,  9.1),
    (26, "1.9.0", 2329, 500,  14.0, 10.0, 0.830,  95,120, 250, 190.0, 1.1,  2.5,  52.4, 6.8,  7.8),
    (27, "1.9.0", 2329, 500,  14.0, 10.0, 0.800,  95,125, 250, 192.0, 1.1,  2.8,  55.0, 9.3, 17.3),
    (28, "1.9.0", 2329, 490,  14.0, 10.0, 0.800,  90,110, 250, 188.0, 1.0,  2.4,  52.0, 6.1,  5.9),
    (29, "1.9.0", 2329, 490,  14.0, 10.0, 0.800,  90,105, 250, 185.0, 1.0,  2.3,  50.5, 4.9,  3.4),
    (30, "1.9.0", 2329, 530,  14.0, 10.0, 0.800,  90,115, 250, 188.0, 1.0,  2.5,  49.8, 3.8,  1.8),
    (31, "1.9.0", 2447, 0,    14.0, 10.0, 1.000, 155, 0,  250, 210.0, 1.6, 10.0,  56.8,11.8, 24.3),
    (32, "1.9.0", 2447, 0,    14.0, 10.0, 0.870, 140, 0,  250, 205.0, 1.5,  8.0,  52.3, 7.2,  6.8),
    (33, "1.9.0", 2447, 0,    14.0, 10.0, 1.000, 145, 0,  250, 208.0, 1.5,  8.5,  53.8, 8.0,  9.2),
    (34, "1.9.0", 2447, 0,    14.0, 10.0, 0.850, 150, 0,  250, 207.0, 1.5,  9.0,  52.9, 7.8,  8.5),
    (35, "1.9.0", 2447, 0,    14.0, 10.0, 1.050, 148, 0,  250, 205.0, 1.5,  8.5,  50.1, 4.5,  2.8),
    (36, "1.9.0", 2447, 0,    14.0, 10.0, 0.900, 147, 0,  250, 205.0, 1.5,  8.8,  52.2, 7.0,  8.0),
    (37, "1.9.0", 2447, 0,    14.0, 10.0, 0.830, 130, 0,  250, 200.0, 1.4,  7.0,  49.5, 3.2,  1.5),
    (38, "1.9.0", 2329, 540,  14.0, 10.0, 0.800,  90, 90, 240, 185.0, 1.0,  2.0,  53.5, 6.5,  5.0),
    (39, "1.9.0", 2329, 540,  14.0, 10.0, 0.800,  90, 80, 240, 182.0, 1.0,  2.0,  50.2, 3.0,  1.2),
    (40, "1.9.0", 2397, 480,  16.0, 10.0, 0.900, 115, 80, 255, 220.0, 1.4,  4.5,  55.1, 8.8, 16.5),
]
