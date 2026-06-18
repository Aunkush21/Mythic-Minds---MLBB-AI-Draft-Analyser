from app.core.validation import assert_heroes_exist, assert_no_duplicate_picks
from app.schemas.build_recommendation import BuildRequest, BuildResponse, ThreatProfile
from app.services.ml_bridge import (
    explanation_to_schema, load_build_recommendation_engine, load_build_recommendation_explain_module,
)


def recommend(request: BuildRequest) -> BuildResponse:
    engine = load_build_recommendation_engine()
    ctx = engine.get_build_context()
    valid_ids = set(ctx.heroes.index)

    assert_heroes_exist([request.hero_id] + request.enemy_picks, valid_ids)
    assert_no_duplicate_picks([request.hero_id], request.enemy_picks)

    result = engine.recommend_build(
        hero_id=request.hero_id, enemy_picks=request.enemy_picks, patch_version=request.patch_version,
    )

    explain_module = load_build_recommendation_explain_module()
    unified = explain_module.to_explanation(result)

    return BuildResponse(
        hero_name=result["hero_name"],
        tier=result["tier"],
        items=result["items"],
        emblem=result["emblem"],
        battle_spell=result["battle_spell"],
        explanation=result["explanation"],
        threat_profile=ThreatProfile(**result["threat_profile"]),
        patch_version=result["patch_version"],
        unified_explanation=explanation_to_schema(unified),
    )
