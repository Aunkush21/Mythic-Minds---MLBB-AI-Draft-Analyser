"""
Generates human-readable explanations naming the specific allied/enemy
heroes responsible for a recommendation's synergy/counter score — this
is what feeds the platform's Explainable AI Insights module.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "features"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "explainability"))

from utils import nearest_patch_leq
from schema import Explanation, ExplanationFactor, Confidence

def _curated_disclosure(n_counters: int | None = None, n_synergies: int | None = None) -> str:
    parts = []
    if n_counters is not None:
        parts.append(f"{n_counters} counter relationships")
    if n_synergies is not None:
        parts.append(f"{n_synergies} synergy relationships")
    coverage = " and ".join(parts) + " across 40 heroes"
    return (
        f"Backed by a hand-curated hero_counters/hero_synergies relationship table "
        f"({coverage}) reflecting authored domain knowledge for the current patch "
        f"meta — not measured win-rate deltas from real matches."
    )
META_STATS_DISCLOSURE = (
    "Win/pick/ban rate figures are hand-authored estimates reflecting plausible "
    "patch 1.9.0 meta, not measured from real match telemetry."
)


def _win_predictor_caveat() -> str:
    try:
        from config import MODELS_DIR
        with open(MODELS_DIR / "v1" / "metadata.json") as f:
            return json.load(f).get("data_caveat", "")
    except FileNotFoundError:
        return "Win predictor model artifact not found."


def _patch_table(lookup: dict, patch: str) -> dict:
    if not lookup:
        return {}
    resolved = nearest_patch_leq(patch, list(lookup.keys()))
    return lookup[resolved]


def top_synergy_partner(candidate_id: int, ally_ids: list[int], synergy_lookup, patch: str, heroes_df):
    table = _patch_table(synergy_lookup, patch)
    best = None
    for ally in ally_ids:
        key = (min(candidate_id, ally), max(candidate_id, ally))
        score = table.get(key)
        if score is not None and (best is None or score > best[1]):
            best = (ally, score)
    if best is None:
        return None
    return heroes_df.loc[best[0], "name"], best[1]


def top_counter_target(candidate_id: int, enemy_ids: list[int], counter_lookup, patch: str, heroes_df):
    table = _patch_table(counter_lookup, patch)
    best = None
    for enemy in enemy_ids:
        score = table.get((enemy, candidate_id))
        if score is not None and (best is None or score > best[1]):
            best = (enemy, score)
    if best is None:
        return None
    return heroes_df.loc[best[0], "name"], best[1]


def generate_explanation(candidate_row: dict, ally_ids: list[int], enemy_ids: list[int],
                          synergy_lookup, counter_lookup, patch: str, heroes_df) -> str:
    synergy_partner = top_synergy_partner(candidate_row["hero_id"], ally_ids, synergy_lookup, patch, heroes_df)
    counter_target = top_counter_target(candidate_row["hero_id"], enemy_ids, counter_lookup, patch, heroes_df)

    clauses = []
    if counter_target and counter_target[1] >= 7.0:
        clauses.append(f"counters {counter_target[0]} (+{counter_target[1]:.1f})")
    if synergy_partner and synergy_partner[1] >= 7.0:
        clauses.append(f"synergizes with {synergy_partner[0]} (+{synergy_partner[1]:.1f})")

    if clauses:
        return "Strong pick: " + " and ".join(clauses) + "."

    if candidate_row.get("win_rate", 50.0) >= 53.0:
        return f"Solid current-patch pick (win rate {candidate_row['win_rate']:.1f}%)."

    return "Viable pick based on overall draft balance."


def _data_count(lookup: dict) -> int:
    return sum(len(v) for v in lookup.values())


def to_explanation_best_pick(entry: dict, oracle_used: bool, counter_lookup, synergy_lookup) -> Explanation:
    raw = entry["raw_scores"]
    factors = [
        ExplanationFactor(
            label="synergy_score", value=round(raw["synergy_score"], 2),
            direction="positive" if raw["synergy_score"] > 0 else "neutral",
            description=f"Synergy with current allies: {raw['synergy_score']:+.1f}",
        ),
        ExplanationFactor(
            label="counter_score", value=round(raw["counter_score"], 2),
            direction="positive" if raw["counter_score"] > 0 else (
                "negative" if raw["counter_score"] < 0 else "neutral"),
            description=f"Counter advantage vs current enemies: {raw['counter_score']:+.1f}",
        ),
        ExplanationFactor(
            label="meta_win_rate", value=round(raw["win_rate"] - 50.0, 2),
            direction="positive" if raw["win_rate"] > 50.0 else (
                "negative" if raw["win_rate"] < 50.0 else "neutral"),
            description=f"Current-patch win rate: {raw['win_rate']:.1f}% "
                        f"({raw['win_rate'] - 50.0:+.1f} vs. 50% baseline)",
        ),
        ExplanationFactor(
            label="lane_fit", value=raw["lane_fit_bonus"],
            direction="positive" if raw["lane_fit_bonus"] == 1.0 else "negative",
            description="Matches this hero's preferred lane" if raw["lane_fit_bonus"] == 1.0
            else "Off-meta lane pick — not this hero's preferred lane",
        ),
    ]
    if raw["role_gap_bonus"] == 1.0:
        factors.append(ExplanationFactor(
            label="role_gap", value=1.0, direction="positive",
            description="Fills a role currently missing from the draft",
        ))

    basis = _curated_disclosure(_data_count(counter_lookup), _data_count(synergy_lookup)) + " " + META_STATS_DISCLOSURE

    source = "curated_data"
    level = "medium"
    cold_start = raw["synergy_score"] == 0 and raw["counter_score"] == 0

    if oracle_used and raw["win_prob_uplift"] is not None:
        factors.append(ExplanationFactor(
            label="win_prob_uplift", value=round(raw["win_prob_uplift"], 4),
            direction="positive" if raw["win_prob_uplift"] > 0 else (
                "negative" if raw["win_prob_uplift"] < 0 else "neutral"),
            description=f"Model-predicted marginal change in win probability: {raw['win_prob_uplift']:+.3f}",
        ))
        source = "model_inference"
        basis += " Additionally, the win-probability-uplift component reuses the win predictor " \
                 "model, which carries its own caveat: " + _win_predictor_caveat()
    elif cold_start:
        level = "low"
        basis = "No draft context yet (first pick) — ranked on current-patch meta alone. " + META_STATS_DISCLOSURE

    return Explanation(
        module="hero_recommendation",
        summary=entry["explanation"],
        factors=factors,
        confidence=Confidence(level=level, source=source, basis=basis),
    )


def to_explanation_counter_pick(entry: dict, counter_lookup) -> Explanation:
    factors = [ExplanationFactor(
        label="counter_score", value=entry["counter_score"], direction="positive",
        description=f"Counters {', '.join(entry['countered_enemy_heroes'])} (+{entry['counter_score']:.1f})",
    )]
    basis = _curated_disclosure(n_counters=_data_count(counter_lookup))
    return Explanation(
        module="hero_recommendation",
        summary=f"Strong counter pick: +{entry['counter_score']:.1f} counter score.",
        factors=factors,
        confidence=Confidence(level="medium", source="curated_data", basis=basis),
    )


def to_explanation_synergy_pick(entry: dict, synergy_lookup) -> Explanation:
    factors = [ExplanationFactor(
        label="synergy_score", value=entry["synergy_score"], direction="positive",
        description=f"Synergizes with {', '.join(entry['synergized_ally_heroes'])} (+{entry['synergy_score']:.1f})",
    )]
    basis = _curated_disclosure(n_synergies=_data_count(synergy_lookup))
    return Explanation(
        module="hero_recommendation",
        summary=f"Strong synergy pick: +{entry['synergy_score']:.1f} synergy score.",
        factors=factors,
        confidence=Confidence(level="medium", source="curated_data", basis=basis),
    )
