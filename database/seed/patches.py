"""
Patch history dataset — the 5 patches preceding and including 1.9.0.
Source of truth that every other table's patch_version FK's into.
"""

PATCHES = [
    # id, patch_version, release_date, codename, summary, heroes_added, heroes_reworked, is_current
    (1, "1.7.0", "2023-08-15", "Mecha Era",
     "Introduced jungle pathing rework and item economy rebalance.",
     ["Joy"], [], False),

    (2, "1.7.2", "2023-09-12", "Storm Surge",
     "Tank emblem rework; nerfs to early-game roam burst combos.",
     [], ["Khufra", "Atlas"], False),

    (3, "1.8.0", "2023-10-20", "Land of Dawn Anniversary",
     "Major mage itemization changes; Holy Crystal passive scaling adjusted.",
     [], ["Kagura"], False),

    (4, "1.8.4", "2023-12-05", "Winter Truncheon Update",
     "Defense item overhaul; Immortality and Athena's Shield cost reduced.",
     [], ["Fredrinn"], False),

    (5, "1.9.0", "2024-01-18", "Reap & Sow",
     "Assassin jungle clear speed buffed across the board; new roam duo "
     "meta emerges around Khufra + Mathilda lockdown combos.",
     [], ["Paquito", "Khufra"], True),
]
