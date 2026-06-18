"""
Hero counter and synergy relationships.
Based on MLBB patch 1.9.0 meta knowledge.
"""

# (hero_id, countered_by_id, counter_score, reason)
COUNTERS = [
    # Tigreal countered by
    (1, 15, 9.2, "Dyrroth's Spectre Step denies Tigreal ult with dash displacement."),
    (1, 22, 8.8, "Joy's mobility kit dodges Sacred Hammer setup windows."),
    (1, 17, 8.5, "Ling's aerial mobility avoids Sacred Hammer ult zone."),
    # Atlas countered by
    (2, 8,  8.7, "Hylos' massive HP pool dilutes Atlas Annihilate damage."),
    (2, 15, 8.5, "Dyrroth shreds Atlas shield with Spectre Step."),
    (2, 22, 9.0, "Joy dashes out of Final Dive pull range easily."),
    # Franco countered by
    (3, 40, 9.3, "Mathilda's shield blocks Iron Hook for an ally."),
    (3, 8,  8.0, "Hylos' body size makes hooking carries difficult."),
    # Khufra countered by
    (4, 22, 9.1, "Joy's dash is not classified as blink, bypasses Bouncing Ball."),
    (4, 21, 8.7, "Gusion dash speed makes Tyrant's Rage whiff consistently."),
    # Fredrinn countered by
    (9, 13, 8.5, "Badang wall traps Fredrinn and negates his dive pattern."),
    (9, 7,  8.2, "Akai's spin pushes Fredrinn away from backline targets."),
    # Yu Zhong countered by
    (10, 13, 8.8, "Badang's wall breaks Yu Zhong dragon form repositioning."),
    (10, 33, 9.0, "Karrie's true damage shreds Yu Zhong's physical sustain regardless of stacking."),
    # Paquito countered by
    (11, 9,  8.9, "Fredrinn's counter absorbs Paquito combo cleanly."),
    (11, 3,  8.5, "Franco hook interrupts Paquito's champion chain."),
    # Ling countered by
    (17, 3,  9.5, "Franco iron hook pulls Ling mid-air off walls."),
    (17, 4,  9.2, "Khufra Bouncing Ball knocks Ling off walls."),
    (17, 40, 9.0, "Mathilda's burst and mobility matches Ling's aggression."),
    # Lancelot countered by
    (18, 4,  9.0, "Khufra's Tyrant's Rage catches Lancelot mid-dash."),
    (18, 2,  8.8, "Atlas Final Dive cancels Lancelot's dash-pattern timing."),
    # Fanny countered by
    (19, 3,  9.8, "Franco hook removes Fanny from her cable trajectory."),
    (19, 4,  9.5, "Khufra Bouncing Ball cancels cable movement completely."),
    (19, 6,  8.7, "Johnson charge stops Fanny cable path in teamfight."),
    # Gusion countered by
    (21, 4,  9.2, "Khufra displaces Gusion mid-dagger-combo."),
    (21, 7,  8.8, "Akai spin pushes Gusion out of dagger range."),
    # Joy countered by
    (22, 4,  8.6, "Khufra Bouncing Ball catches Joy dash sequences."),
    (22, 7,  8.5, "Akai's spin slows attack windows, denying Joy's dash chain timing."),
    # Kagura countered by
    (24, 4,  9.0, "Khufra pushes Kagura umbrella out of position."),
    (24, 3,  8.7, "Franco hook picks Kagura before she can reset umbrella."),
    # Valentina countered by
    (27, 4,  8.9, "Khufra interrupts Valentina's ultimate copy sequence."),
    (27, 22, 8.5, "Joy's high burst kills Valentina before she can ult."),
    # Beatrix countered by
    (31, 4,  8.7, "Khufra Bouncing Ball stops Beatrix repositioning."),
    (31, 40, 9.1, "Mathilda closes gap rapidly, nullifying Beatrix range advantage."),
    (31, 38, 8.9, "Floryn healing sustains teammates through Beatrix poke."),
    # Melissa countered by
    (32, 22, 8.8, "Joy burst kills Melissa before bubble can protect her."),
    (32, 21, 8.5, "Gusion combo bursts through Me Too! shield timing."),
    # Karrie countered by
    (33, 22, 8.7, "Joy closes fast enough to shut down Karrie's kite loop."),
    (33, 4,  9.3, "Khufra's CC chain shuts Karrie down before her true-damage stacks build."),
    # Mathilda countered by
    (40, 4,  9.0, "Khufra Bouncing Ball stops Mathilda flight mid-air."),
    (40, 3,  8.7, "Franco hook cancels Mathilda's soul guide dash."),
]

# (hero_a_id, hero_b_id, synergy_score, combo_name, reason)
# hero_a_id must always be < hero_b_id
SYNERGIES = [
    (2,  3,  9.5, "Hook & Bomb",         "Franco hooks target into Atlas Final Dive for guaranteed multi-man CC."),
    (2,  38, 9.0, "Tank Healer",         "Atlas engages; Floryn heals teammates through the CC window."),
    (3,  40, 9.3, "Hook & Fly",          "Franco hooks; Mathilda flies in to execute the isolated target."),
    (4,  9,  8.8, "Stun Dive",           "Khufra sets up; Fredrinn dives in for massive AoE damage."),
    (4,  11, 9.2, "Lock & Burst",        "Khufra locks target with CC; Paquito chains combo for instant kill."),
    (4,  17, 9.5, "Cage & Assassin",     "Khufra Bouncing Ball traps enemies; Ling drops in for clean kills."),
    (4,  21, 9.4, "Stun Burst",          "Khufra CC chains into Gusion dagger burst for zero-counterplay kill."),
    (4,  31, 9.1, "Control Carry",       "Khufra's lockdown gives Beatrix safe positioning to deal damage."),
    (5,  9,  8.5, "Sticky Tank",         "Gloo slows; Fredrinn follows up. Hard to kite."),
    (7,  17, 9.0, "Wall Spin Aerial",    "Akai spin + Ling aerial makes for unescapable initiation."),
    (9,  38, 8.7, "Tank Sustain",        "Fredrinn dives; Floryn heals him back through the fight."),
    (10, 24, 8.5, "Dragon Scroll",       "Yu Zhong dragon form holds enemies; Kagura shreds with umbrellas."),
    (11, 36, 9.0, "Punch Snipe",         "Paquito CC combo; Granger snipers the low-HP target."),
    (17, 24, 9.2, "Roof Drop",           "Ling drops on priority target; Kagura isolates with passive."),
    (17, 40, 9.6, "Fly & Drop",          "Mathilda flies ally Ling into backline for devastating surprise."),
    (18, 36, 8.8, "Dash Snipe",          "Lancelot dive distracts; Granger snipes the displaced carry."),
    (20, 26, 8.6, "Shadow Tornado",      "Hayabusa cuts escape routes; Vale tornado traps for kills."),
    (21, 40, 9.3, "Speed Burst",         "Mathilda closes gap; Gusion unloads full dagger combo before enemy reacts."),
    (24, 38, 8.9, "Poke Heal",           "Kagura pokes enemies down; Floryn heals teammates sustaining the poke."),
    (25, 40, 9.0, "Chaos Fly",           "Mathilda flies Lunox in; Lunox unloads Order burst on arrival."),
    (27, 31, 9.1, "Copy Carry",          "Valentina copies enemy ultimate; Beatrix provides the damage backbone."),
    (31, 38, 9.2, "Safe Carry",          "Floryn keeps Beatrix alive; Beatrix punishes with multi-weapon poke."),
    (33, 36, 8.7, "True Damage Snipe",   "Karrie shreds tank HP; Granger finishes squishies. Balanced damage profile."),
    (34, 40, 9.0, "Hook Fly",            "Mathilda flies Brody in; Brody stacks marks for massive burst."),
    (38, 40, 9.4, "Heal Roam",           "Floryn and Mathilda double support — ultimate healing + engage. High ELO roam duo."),
    (2,  40, 9.1, "Roam Duo",            "Atlas + Mathilda create two independent engage threats that confuse enemy backline."),
    (4,  40, 9.8, "Meta Roam",           "Khufra + Mathilda. Most feared roam duo in patch 1.9.0 pro play."),
    (9,  15, 8.9, "EXP Brawl",           "Fredrinn + Dyrroth create an oppressive EXP lane double fighter."),
    (11, 22, 9.1, "High Skill Burst",    "Paquito + Joy — two skill-intensive assassin/fighters creating solo-kill threats everywhere."),
    (17, 22, 9.3, "Aerial Dash",         "Ling + Joy — both mobile, fast-killing. Enemy tanks get ignored."),
]

# Hero builds: (hero_id, build_name, item1..6, emblem_id, spell_id, situation, patch, win_rate, games)
HERO_BUILDS = [
    # Fredrinn — Tank Fighter EXP
    (9,  "Fredrinn Standard",      36, 29, 4,  6, 20, 25, 2, 2, "Standard",   "1.9.0", 54.2, 4821),
    (9,  "Fredrinn Anti-Magic",    36, 29, 27, 28,20, 25, 2, 2, "Anti-Magic", "1.9.0", 52.8, 1203),
    # Paquito — Fighter EXP
    (11, "Paquito Burst",          29, 3,  4,  2, 24, 25, 2, 2, "Standard",   "1.9.0", 55.1, 3241),
    # Ling — Assassin Jungle
    (17, "Ling Standard",          29, 1,  2,  3, 44, 25, 1, 3, "Standard",   "1.9.0", 56.0, 8102),
    (17, "Ling Anti-Tank",         29, 1,  10, 3, 44, 25, 1, 3, "Anti-Tank",  "1.9.0", 53.5, 2201),
    # Lancelot — Assassin Jungle
    (18, "Lancelot Standard",      29, 1,  3,  2, 44, 25, 1, 3, "Standard",   "1.9.0", 52.4, 5601),
    # Fanny — Assassin Jungle
    (19, "Fanny Standard",         29, 1,  3,  2, 44, 25, 1, 3, "Standard",   "1.9.0", 53.8, 4320),
    # Kagura — Mage Mid
    (24, "Kagura Standard",        31, 16, 18, 11, 14, 42, 3, 1, "Standard",  "1.9.0", 54.6, 6201),
    # Valentina — Mage Mid
    (27, "Valentina Standard",     31, 11, 14, 18, 17, 42, 3, 1, "Standard",  "1.9.0", 54.8, 5102),
    # Beatrix — Marksman Gold
    (31, "Beatrix Standard",       33, 5,  1,  2, 45,  9, 4, 4, "Standard",   "1.9.0", 56.5, 9801),
    (31, "Beatrix Anti-Burst",     33, 5,  1, 44, 45,  9, 4, 4, "Anti-Burst", "1.9.0", 54.0, 1802),
    # Karrie — Marksman Gold
    (33, "Karrie Standard",        33, 10, 7,  5, 45,  9, 4, 4, "Standard",   "1.9.0", 53.6, 4210),
    # Mathilda — Support Roam
    (40, "Mathilda Standard",      30, 37, 28, 23, 36, 17, 5, 7, "Standard",  "1.9.0", 54.9, 7302),
    # Floryn — Support Roam
    (38, "Floryn Standard",        30, 37, 28, 13, 17, 39, 5, 7, "Standard",  "1.9.0", 53.2, 3201),
    # Atlas — Tank Roam
    (2,  "Atlas Standard",         30, 36, 20, 27, 47, 25, 6, 6, "Standard",  "1.9.0", 51.6, 4801),
    # Franco — Tank Roam
    (3,  "Franco Standard",        30, 36, 20, 22, 47, 25, 6, 6, "Standard",  "1.9.0", 48.7, 3902),
    # Khufra — Tank Roam
    (4,  "Khufra Standard",        30, 36, 20, 46, 47, 25, 6, 6, "Standard",  "1.9.0", 52.9, 6103),
    # Dyrroth — Fighter EXP
    (15, "Dyrroth Standard",       29, 3,  4,  2, 24, 44, 2, 2, "Standard",   "1.9.0", 53.8, 5421),
    # Yu Zhong — Fighter EXP
    (10, "Yu Zhong Standard",      29, 4,  6,  24, 20, 25, 2, 2, "Standard",  "1.9.0", 51.9, 3810),
    # Joy — Assassin Jungle
    (22, "Joy Standard",           29, 1,  3,  2, 44, 25, 1, 3, "Standard",   "1.9.0", 55.6, 7201),
    # Gusion — Assassin Jungle
    (21, "Gusion Standard",        31, 40, 18, 11, 14, 42, 3, 1, "Standard",  "1.9.0", 53.2, 4901),
    # Vale — Mage Mid
    (26, "Vale Standard",          31, 16, 17, 11, 14, 42, 3, 1, "Standard",  "1.9.0", 52.1, 3801),
    # Lunox — Mage Mid
    (25, "Lunox Standard",         31, 11, 14, 18, 15, 42, 3, 1, "Standard",  "1.9.0", 53.5, 4201),
    # Khufra EXP lane
    (4,  "Khufra EXP",             29, 36, 20, 46, 26, 25, 6, 2, "Off-Lane",  "1.9.0", 50.2, 1102),
]
