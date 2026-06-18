"""
Synthetic match generator — produces 500 realistic MLBB drafts + results.
Uses hero role/lane constraints and meta win rates to bias outcomes.
"""
import random
import uuid
from heroes import HEROES

random.seed(42)

# Hero lookup: id -> (name, role, lane, is_meta, is_op)
HERO_LOOKUP = {h[0]: h for h in HEROES}

# Lane -> list of hero_ids that prefer that lane
LANE_HEROES = {lane: [] for lane in ["EXP", "Gold", "Mid", "Jungle", "Roam"]}
for h in HEROES:
    LANE_HEROES[h[6]].append(h[0])

# Meta/OP heroes get higher win probability when picked
META_HEROES = {h[0] for h in HEROES if h[8]}
OP_HEROES   = {h[0] for h in HEROES if h[9]}

RANKS = [
    "Warrior", "Elite", "Master", "Grandmaster",
    "Epic", "Legend", "Mythic", "Mythical Glory"
]
# Weighted distribution — more Mythic-range games in a competitive dataset
RANK_WEIGHTS = [2, 4, 8, 12, 20, 25, 20, 9]

SIDES = ["Blue", "Red"]


def team_score(picks: list[int]) -> float:
    """Simple meta score for a 5-hero team."""
    score = 0.0
    for hid in picks:
        if hid in OP_HEROES:
            score += 2.0
        elif hid in META_HEROES:
            score += 1.0
    return score


def draft_team(used_ids: set[int]) -> tuple[int, int, int, int, int]:
    """Pick one hero per lane, no repeats."""
    picks = []
    for lane in ["EXP", "Gold", "Mid", "Jungle", "Roam"]:
        pool = [h for h in LANE_HEROES[lane] if h not in used_ids]
        if not pool:
            pool = [h for h in HERO_LOOKUP if h not in used_ids]
        hero = random.choice(pool)
        picks.append(hero)
        used_ids.add(hero)
    return tuple(picks)


def draft_bans(used_ids: set[int], n: int = 5) -> list[int]:
    available = [h[0] for h in HEROES if h[0] not in used_ids]
    bans = random.sample(available, min(n, len(available)))
    used_ids.update(bans)
    return bans


def generate_matches(n: int = 500) -> tuple[list[dict], list[dict]]:
    drafts = []
    results = []

    for _ in range(n):
        used_ids: set[int] = set()

        blue_bans = draft_bans(used_ids)
        red_bans  = draft_bans(used_ids)
        blue_picks = draft_team(used_ids)
        red_picks  = draft_team(used_ids)

        blue_score = team_score(list(blue_picks))
        red_score  = team_score(list(red_picks))

        # Win probability biased by meta score difference
        score_diff = blue_score - red_score
        blue_win_prob = 0.5 + (score_diff * 0.06)
        blue_win_prob = max(0.30, min(0.70, blue_win_prob))

        winner = "Blue" if random.random() < blue_win_prob else "Red"

        rank   = random.choices(RANKS, weights=RANK_WEIGHTS)[0]
        match_id = str(uuid.uuid4())

        # Performance stats — loosely correlated with winner
        def gen_team_stats(is_winner: bool):
            base_kills = random.randint(8, 20) if is_winner else random.randint(4, 14)
            return {
                "kills":   base_kills,
                "deaths":  random.randint(4, 14) if is_winner else random.randint(8, 20),
                "assists": base_kills + random.randint(0, 10),
                "turrets": random.randint(4, 11) if is_winner else random.randint(0, 5),
                "lords":   random.randint(1, 3) if is_winner else random.randint(0, 2),
                "turtles": random.randint(2, 4) if is_winner else random.randint(0, 3),
                "gold":    random.randint(55000, 80000) if is_winner else random.randint(40000, 65000),
            }

        blue_stats = gen_team_stats(winner == "Blue")
        red_stats  = gen_team_stats(winner == "Red")
        duration   = random.randint(600, 1800)

        # First objectives
        def first_side(win_side: str, bias: float = 0.6) -> str:
            return win_side if random.random() < bias else ("Red" if win_side == "Blue" else "Blue")

        drafts.append({
            "match_id":      match_id,
            "patch_version": "1.9.0",
            "rank":          rank,
            "blue_exp":    blue_picks[0], "blue_gold":   blue_picks[1],
            "blue_mid":    blue_picks[2], "blue_jungle": blue_picks[3], "blue_roam":   blue_picks[4],
            "red_exp":     red_picks[0],  "red_gold":    red_picks[1],
            "red_mid":     red_picks[2],  "red_jungle":  red_picks[3],  "red_roam":    red_picks[4],
            "blue_bans":   blue_bans,
            "red_bans":    red_bans,
        })

        results.append({
            "match_id":         match_id,
            "winner":           winner,
            "match_duration":   duration,
            "blue_kills":       blue_stats["kills"],
            "blue_deaths":      blue_stats["deaths"],
            "blue_assists":     blue_stats["assists"],
            "blue_turrets":     blue_stats["turrets"],
            "blue_lords":       blue_stats["lords"],
            "blue_turtles":     blue_stats["turtles"],
            "blue_gold_total":  blue_stats["gold"],
            "red_kills":        red_stats["kills"],
            "red_deaths":       red_stats["deaths"],
            "red_assists":      red_stats["assists"],
            "red_turrets":      red_stats["turrets"],
            "red_lords":        red_stats["lords"],
            "red_turtles":      red_stats["turtles"],
            "red_gold_total":   red_stats["gold"],
            "first_blood_side":  first_side(winner, 0.65),
            "first_turret_side": first_side(winner, 0.70),
            "first_lord_side":   first_side(winner, 0.75),
            "first_turtle_side": first_side(winner, 0.60),
        })

    return drafts, results


if __name__ == "__main__":
    drafts, results = generate_matches(500)
    print(f"Generated {len(drafts)} drafts and {len(results)} results.")
    print("\nSample draft:")
    d = drafts[0]
    print(f"  Match:  {d['match_id']}")
    print(f"  Rank:   {d['rank']}")
    print(f"  Blue:   EXP={d['blue_exp']} Gold={d['blue_gold']} Mid={d['blue_mid']} "
          f"JG={d['blue_jungle']} Roam={d['blue_roam']}")
    print(f"  Red:    EXP={d['red_exp']} Gold={d['red_gold']} Mid={d['red_mid']} "
          f"JG={d['red_jungle']} Roam={d['red_roam']}")
    print(f"\nSample result:")
    r = results[0]
    print(f"  Winner: {r['winner']}  Duration: {r['match_duration']}s")
    print(f"  Blue K/D/A: {r['blue_kills']}/{r['blue_deaths']}/{r['blue_assists']}")
    print(f"  Red  K/D/A: {r['red_kills']}/{r['red_deaths']}/{r['red_assists']}")
