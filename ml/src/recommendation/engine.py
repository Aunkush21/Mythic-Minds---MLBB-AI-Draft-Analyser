"""
Main entry point: recommend_hero_pick(...) -> {best_picks, counter_picks,
synergy_picks, meta}. Orchestrates candidate generation -> scoring ->
ranking -> diversification -> explanation, exactly matching the
designed API response contract.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data_loader import get_context
from candidate_generation import generate_candidates
from scoring import (
    candidate_counter_score, candidate_synergy_score, candidate_meta_score,
    role_gap_bonus, damage_diversity_bonus, lane_fit_bonus,
)
from oracle import is_oracle_eligible, win_prob_uplift
from ranking import compute_composite_scores
from similarity import mmr_rerank
from explain import generate_explanation, top_synergy_partner, top_counter_target

DEFAULT_RANK = "Mythic"


def recommend_hero_pick(
    ally_picks: dict,
    enemy_picks: dict,
    banned_heroes: list[int],
    target_lane: str,
    patch_version: str | None = None,
    rank_tier: str | None = None,
    top_k: int = 5,
) -> dict:
    ctx = get_context()
    patch = ctx.resolve_patch(patch_version)
    rank = rank_tier or DEFAULT_RANK

    ally_ids = [v for v in ally_picks.values() if v is not None]
    enemy_ids = [v for v in enemy_picks.values() if v is not None]

    candidates = generate_candidates(ctx.heroes, ally_picks, enemy_picks, banned_heroes, target_lane)
    oracle_used = ctx.win_model is not None and is_oracle_eligible(ally_picks, enemy_picks)

    rows = []
    for hero_id in candidates:
        meta = candidate_meta_score(hero_id, ctx.hero_stats_lookup, patch)
        row = {
            "hero_id": hero_id,
            "hero_name": ctx.heroes.loc[hero_id, "name"],
            "synergy_score": candidate_synergy_score(hero_id, ally_ids, ctx.synergy_lookup, patch),
            "counter_score": candidate_counter_score(hero_id, enemy_ids, ctx.counter_lookup, patch),
            "win_rate": meta["win_rate"],
            "pick_rate": meta["pick_rate"],
            "ban_rate": meta["ban_rate"],
            "role_gap_bonus": role_gap_bonus(hero_id, ally_ids, ctx.heroes),
            "damage_diversity_bonus": damage_diversity_bonus(hero_id, ally_ids, ctx.heroes),
            "lane_fit_bonus": lane_fit_bonus(hero_id, target_lane, ctx.heroes),
        }
        if oracle_used:
            row["win_prob_uplift"] = win_prob_uplift(
                hero_id, target_lane, ally_picks, enemy_picks, ctx.heroes,
                ctx.hero_stats_lookup, ctx.counter_lookup, ctx.synergy_lookup,
                patch, rank, ctx.win_model, ctx.win_model_feature_columns,
            )
        rows.append(row)

    ranked = compute_composite_scores(rows, oracle_used)

    # Best Picks: top candidates by composite score, then MMR-diversified.
    pre_mmr = ranked.head(max(top_k * 3, 10)).to_dict("records")
    diversified = mmr_rerank(pre_mmr, ctx.similarity_matrix, ctx.similarity_hero_ids, k=top_k)

    best_picks = []
    for c in diversified:
        explanation = generate_explanation(c, ally_ids, enemy_ids, ctx.synergy_lookup,
                                            ctx.counter_lookup, patch, ctx.heroes)
        entry = {
            "hero_id": c["hero_id"],
            "hero_name": c["hero_name"],
            "composite_score": round(float(c["composite_score"]), 4),
            "explanation": explanation,
            # Raw component scores, retained for the unified explainability
            # adapter (explain.to_explanation_best_pick) — without these the
            # adapter would have to re-derive factor contributions from the
            # already-rendered text instead of the real underlying numbers.
            "raw_scores": {
                "synergy_score": float(c["synergy_score"]),
                "counter_score": float(c["counter_score"]),
                "win_rate": float(c["win_rate"]),
                "pick_rate": float(c["pick_rate"]),
                "ban_rate": float(c["ban_rate"]),
                "role_gap_bonus": float(c["role_gap_bonus"]),
                "damage_diversity_bonus": float(c["damage_diversity_bonus"]),
                "lane_fit_bonus": float(c["lane_fit_bonus"]),
                "win_prob_uplift": float(c["win_prob_uplift"]) if oracle_used else None,
            },
        }
        if oracle_used:
            entry["win_prob_uplift"] = round(float(c["win_prob_uplift"]), 4)
        best_picks.append(entry)

    # Counter Picks: pure counter-score ranking, independent list.
    counter_df = ranked[ranked["counter_score"] > 0].sort_values("counter_score", ascending=False).head(top_k)
    counter_picks = []
    for row in counter_df.to_dict("records"):
        target = top_counter_target(row["hero_id"], enemy_ids, ctx.counter_lookup, patch, ctx.heroes)
        counter_picks.append({
            "hero_id": row["hero_id"],
            "hero_name": row["hero_name"],
            "counter_score": round(float(row["counter_score"]), 2),
            "countered_enemy_heroes": [target[0]] if target else [],
        })

    # Synergy Picks: pure synergy-score ranking, independent list.
    synergy_df = ranked[ranked["synergy_score"] > 0].sort_values("synergy_score", ascending=False).head(top_k)
    synergy_picks = []
    for row in synergy_df.to_dict("records"):
        partner = top_synergy_partner(row["hero_id"], ally_ids, ctx.synergy_lookup, patch, ctx.heroes)
        synergy_picks.append({
            "hero_id": row["hero_id"],
            "hero_name": row["hero_name"],
            "synergy_score": round(float(row["synergy_score"]), 2),
            "synergized_ally_heroes": [partner[0]] if partner else [],
        })

    return {
        "best_picks": best_picks,
        "counter_picks": counter_picks,
        "synergy_picks": synergy_picks,
        "meta": {
            "patch_version": patch,
            "candidates_considered": len(candidates),
            "win_prob_uplift_used": oracle_used,
        },
    }
