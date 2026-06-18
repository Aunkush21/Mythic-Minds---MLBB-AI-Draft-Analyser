"""
Explanation generation with mandatory provenance disclosure — the
recommendation must always state whether it's backed by real curated
data, transferred from a similar hero, or a pure heuristic fallback.
Never blur that distinction.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "explainability"))
from schema import Explanation, ExplanationFactor, Confidence

HIGH_CONFIDENCE_GAMES_PLAYED = 2000
MEDIUM_CONFIDENCE_SIMILARITY = 0.93

ESTIMATED_BUILD_STATS_DISCLOSURE = (
    "Win rate and games-played figures in the curated build table are "
    "hand-authored estimates illustrating plausible patch 1.9.0 outcomes, "
    "not measured from real match telemetry."
)


def describe_source(build: dict) -> str:
    source = build["source"]
    if source == "curated":
        wr = build.get("win_rate")
        gp = build.get("games_played", 0)
        wr_text = f"{wr:.1f}% win rate" if wr is not None else "no recorded win rate"
        return f"Based on {gp:,} games at {wr_text} ('{build['build_name']}')."
    if source == "similarity_transfer":
        return (f"Adapted from {build['borrowed_from']}'s build "
                f"(similarity {build['similarity']:.2f}) — no direct historical "
                f"data for this hero in this matchup.")
    return "Role-based default — no curated or transferable historical data available."


def describe_swaps(swap_log: list[dict]) -> list[str]:
    return [f"Swapped {s['removed_item']} -> {s['added_item']} because {s['reason']}." for s in swap_log]


def describe_spell_override(reason: str | None, new_spell_name: str) -> str | None:
    if reason is None:
        return None
    return f"Switched battle spell to {new_spell_name} because {reason}."


def to_explanation(result: dict) -> Explanation:
    provenance = result["provenance_detail"]
    source_kind = provenance["source"]

    factors = []
    if source_kind == "curated":
        wr, gp = provenance.get("win_rate"), provenance.get("games_played", 0)
        factors.append(ExplanationFactor(
            label="historical_track_record", value=wr, direction="positive",
            description=f"{gp:,} games at {wr:.1f}% win rate" if wr is not None else f"{gp:,} games recorded",
        ))
        confidence = Confidence(
            level="high" if gp >= HIGH_CONFIDENCE_GAMES_PLAYED else "medium",
            source="curated_data",
            basis=ESTIMATED_BUILD_STATS_DISCLOSURE,
        )
    elif source_kind == "similarity_transfer":
        sim = provenance["similarity"]
        factors.append(ExplanationFactor(
            label="similarity_transfer", value=round(sim, 2), direction="neutral",
            description=f"Adapted from {provenance['borrowed_from']}'s build (similarity {sim:.2f})",
        ))
        confidence = Confidence(
            level="medium" if sim >= MEDIUM_CONFIDENCE_SIMILARITY else "low",
            source="transferred_data",
            basis=f"No direct historical data for this hero in this matchup. {ESTIMATED_BUILD_STATS_DISCLOSURE}",
        )
    else:
        factors.append(ExplanationFactor(
            label="role_default", value=None, direction="neutral",
            description="Pure role/damage-type heuristic, no historical backing",
        ))
        confidence = Confidence(
            level="low", source="heuristic_default",
            basis="No curated or transferable historical data available for this hero and situation.",
        )

    for swap in result["swap_log"]:
        factors.append(ExplanationFactor(
            label="threat_substitution", value=None, direction="neutral",
            description=f"Swapped {swap['removed_item']} -> {swap['added_item']} because {swap['reason']}",
        ))

    if result["spell_override_reason"]:
        factors.append(ExplanationFactor(
            label="spell_override", value=None, direction="neutral",
            description=f"Switched battle spell because {result['spell_override_reason']}",
        ))

    return Explanation(
        module="build_recommendation",
        summary=result["explanation"][0],
        factors=factors,
        confidence=confidence,
    )
