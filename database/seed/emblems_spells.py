"""
Emblems and Battle Spells seed data.
"""

EMBLEMS = [
    # id, name, type, phys_atk, magic_pwr, hp, armor, magic_res, cdr, move_spd, t1, t2, t3, recommended_roles
    (1, "Assassin Emblem",  "Assassin", 16.0,  0.0, 0,   0.0,  0.0, 0.0, 0,
     "Agility", "Mastery", "Killing Spree",  ["Assassin"]),
    (2, "Fighter Emblem",   "Fighter",  14.0,  0.0, 0,   3.0,  0.0, 0.0, 0,
     "Bravery", "Invasion", "Festival of Blood", ["Fighter"]),
    (3, "Mage Emblem",      "Mage",     0.0,  17.0, 0,   0.0,  0.0, 5.0, 0,
     "Mastery", "Observation", "Mystery Shop",  ["Mage"]),
    (4, "Marksman Emblem",  "Marksman", 12.0,  0.0, 0,   0.0,  0.0, 0.0, 0,
     "Agility", "Weapon Master", "Electro Flash", ["Marksman"]),
    (5, "Support Emblem",   "Support",  0.0,   0.0, 500, 0.0,  0.0, 10.0, 10,
     "Avarice", "Healing Spell", "Pull Yourself Together", ["Support", "Tank"]),
    (6, "Tank Emblem",      "Tank",     0.0,   0.0, 0,   6.0,  6.0, 0.0, 0,
     "Vitality", "Fortress", "Brave Smite", ["Tank"]),
    (7, "Common Emblem",    "Common",   8.0,   8.0, 0,   0.0,  0.0, 0.0, 0,
     "Vitality", "Persistence", "Concussive Blast", ["Tank", "Fighter", "Support"]),
]

BATTLE_SPELLS = [
    # id, name, description, cooldown, unlock_level, recommended_roles, recommended_lanes, use_case, patch
    (1,  "Flicker",
     "Teleport to designated location instantly, immune to CC during blink.",
     120, 1, ["Assassin", "Mage", "Marksman"], ["Gold", "Mid", "Jungle"],
     "Escape/engage. Most picked spell in high elo.", "1.9.0"),

    (2,  "Execute",
     "Deal 200+80% Phys Attack as True Damage to one enemy with HP below 50%.",
     90, 1, ["Fighter", "Assassin"], ["EXP", "Jungle"],
     "Finish off low-HP targets. Great on fighters with gap-close.", "1.9.0"),

    (3,  "Retribution",
     "Deal 600 True Damage to a jungle monster. Upgrading unlocks jungle item.",
     50, 1, ["Assassin", "Fighter"], ["Jungle"],
     "Mandatory for jungler role. Secures objectives.", "1.9.0"),

    (4,  "Sprint",
     "Increase movement speed by 40-60% for 8s.",
     90, 1, ["Marksman", "Mage"], ["Gold", "Mid"],
     "Escape for immobile carries. Alternative to Flicker.", "1.9.0"),

    (5,  "Aegis",
     "Gain a 750HP shield for yourself and the lowest HP nearby ally for 3s.",
     90, 1, ["Support", "Tank"], ["Roam"],
     "Defensive option for supports and tanks.", "1.9.0"),

    (6,  "Vengeance",
     "Reflect 50% of damage taken back to attackers for 3s. Reduce damage taken by 35%.",
     90, 1, ["Tank", "Fighter"], ["Roam", "EXP"],
     "Anti-burst tankiness. Great in teamfight.", "1.9.0"),

    (7,  "Revitalize",
     "Summon a Healing Spring for 5s, restoring HP to allies within range.",
     75, 1, ["Support"], ["Roam"],
     "Sustain in teamfight. Pairs well with Angela, Estes, Floryn.", "1.9.0"),

    (8,  "Purify",
     "Remove CC effects immediately; grants CC immunity for 1.2s.",
     100, 1, ["Marksman", "Mage"], ["Gold", "Mid"],
     "Counter to hook/CC-heavy comps. Essential vs Franco/Atlas.", "1.9.0"),

    (9,  "Inspire",
     "+55% attack speed and ignore 8 physical defense for 5 basic attacks.",
     75, 1, ["Marksman", "Fighter"], ["Gold", "EXP"],
     "Burst basic attack window. Great on Clint/Masha.", "1.9.0"),

    (10, "Flameshot",
     "Fire a flaming shot dealing 160+45% Magic Power magic damage and knocking back.",
     75, 1, ["Mage", "Marksman"], ["Mid", "Gold"],
     "Poke + interrupt. Anti-dive tool.", "1.9.0"),
]
