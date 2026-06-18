"""
Main entry point: recommend_build(hero_id, enemy_picks, patch_version) ->
{ items, emblem, battle_spell, explanation, tier, threat_profile }.

Orchestrates the full confidence cascade: Tier 1 (curated) -> Tier 2
(similarity transfer) -> Tier 3 (role default), then applies threat-based
slot substitution and spell override on top, regardless of which tier
produced the backbone.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_loader import get_build_context
from threat_features import compute_enemy_threat_profile
from template_selection import try_tier1, try_tier2
from role_defaults import build_role_default
from substitution import apply_threat_substitution
from emblem_spell_rules import apply_spell_override
from explain import describe_source, describe_swaps, describe_spell_override


def recommend_build(hero_id: int, enemy_picks: list[int], patch_version: str | None = None) -> dict:
    ctx = get_build_context()
    patch = ctx.resolve_patch(patch_version)
    hero_role = ctx.heroes.loc[hero_id, "role"]

    threat = compute_enemy_threat_profile(enemy_picks, ctx.heroes)

    backbone = try_tier1(hero_id, ctx.hero_builds, threat, patch)
    tier = "tier1_curated"
    if backbone is None:
        backbone = try_tier2(hero_id, ctx.heroes, ctx.hero_builds, threat, patch,
                              ctx.similarity_matrix, ctx.similarity_hero_ids, ctx.items)
        tier = "tier2_similarity_transfer"
    if backbone is None:
        backbone = build_role_default(hero_id, ctx.heroes, ctx.items, ctx.emblems, ctx.spells)
        tier = "tier3_role_default"

    final_items, swap_log = apply_threat_substitution(backbone["items"], threat, ctx.items)
    final_spell_id, spell_reason = apply_spell_override(backbone["spell_id"], threat, hero_role, ctx.spells)

    explanation = [describe_source(backbone)] + describe_swaps(swap_log)
    spell_explanation = describe_spell_override(spell_reason, ctx.spells.loc[final_spell_id, "name"])
    if spell_explanation:
        explanation.append(spell_explanation)

    return {
        "hero_name": ctx.heroes.loc[hero_id, "name"],
        "tier": tier,
        "items": [ctx.items.loc[i, "name"] for i in final_items],
        "emblem": ctx.emblems.loc[backbone["emblem_id"], "name"],
        "battle_spell": ctx.spells.loc[final_spell_id, "name"],
        "explanation": explanation,
        "threat_profile": threat,
        "patch_version": patch,
        # Retained for the unified explainability adapter (explain.to_explanation)
        # — without these, the adapter would have to re-derive confidence
        # detail from the already-rendered explanation strings.
        "provenance_detail": {
            k: v for k, v in backbone.items() if k != "items"
        },
        "swap_log": swap_log,
        "spell_override_reason": spell_reason,
    }
