from app.core.exceptions import HeroNotFoundError, InvalidDraftError
from app.core.validation import assert_heroes_exist, assert_no_duplicate_picks
from app.schemas.hero import SimilarHeroEntry
from app.schemas.hero_recommendation import (
    BestPickEntry, CounterPickEntry, HeroPickMeta, HeroPickRequest, HeroPickResponse, SynergyPickEntry,
)
from app.services.ml_bridge import (
    explanation_to_schema, get_recommendation_data_context,
    load_recommendation_engine, load_recommendation_explain_module, load_recommendation_similarity_module,
)


def get_similar_heroes(hero_id: int, limit: int) -> list[SimilarHeroEntry]:
    ctx = get_recommendation_data_context()
    if hero_id not in set(ctx.heroes.index):
        raise HeroNotFoundError(f"No hero with id {hero_id}.")

    similarity_module = load_recommendation_similarity_module()
    results = similarity_module.similar_heroes(
        hero_id, ctx.similarity_matrix, ctx.similarity_hero_ids, exclude_ids=set(), limit=limit,
    )
    return [
        SimilarHeroEntry(hero_id=hid, hero_name=ctx.heroes.loc[hid, "name"], similarity=round(float(score), 4))
        for hid, score in results
    ]


def recommend(request: HeroPickRequest) -> HeroPickResponse:
    ctx = get_recommendation_data_context()
    valid_ids = set(ctx.heroes.index)

    ally = request.ally_picks.to_dict()
    enemy = request.enemy_picks.to_dict()

    if ally.get(request.target_lane) is not None:
        raise InvalidDraftError(
            f"target_lane '{request.target_lane}' must be unfilled in ally_picks — "
            f"it currently holds hero id {ally[request.target_lane]}."
        )

    known_ids = [v for v in list(ally.values()) + list(enemy.values()) if v is not None]
    all_ids = known_ids + request.banned_heroes
    assert_heroes_exist(all_ids, valid_ids)
    assert_no_duplicate_picks(known_ids, request.banned_heroes)

    engine = load_recommendation_engine()
    result = engine.recommend_hero_pick(
        ally_picks=ally, enemy_picks=enemy, banned_heroes=request.banned_heroes,
        target_lane=request.target_lane, patch_version=request.patch_version,
        rank_tier=request.rank_tier, top_k=request.top_k,
    )

    explain_module = load_recommendation_explain_module()
    oracle_used = result["meta"]["win_prob_uplift_used"]

    best_picks = [
        BestPickEntry(
            hero_id=p["hero_id"], hero_name=p["hero_name"], composite_score=p["composite_score"],
            explanation=p["explanation"], win_prob_uplift=p.get("win_prob_uplift"),
            unified_explanation=explanation_to_schema(
                explain_module.to_explanation_best_pick(p, oracle_used, ctx.counter_lookup, ctx.synergy_lookup)
            ),
        )
        for p in result["best_picks"]
    ]
    counter_picks = [
        CounterPickEntry(
            hero_id=p["hero_id"], hero_name=p["hero_name"], counter_score=p["counter_score"],
            countered_enemy_heroes=p["countered_enemy_heroes"],
            unified_explanation=explanation_to_schema(
                explain_module.to_explanation_counter_pick(p, ctx.counter_lookup)
            ),
        )
        for p in result["counter_picks"]
    ]
    synergy_picks = [
        SynergyPickEntry(
            hero_id=p["hero_id"], hero_name=p["hero_name"], synergy_score=p["synergy_score"],
            synergized_ally_heroes=p["synergized_ally_heroes"],
            unified_explanation=explanation_to_schema(
                explain_module.to_explanation_synergy_pick(p, ctx.synergy_lookup)
            ),
        )
        for p in result["synergy_picks"]
    ]

    return HeroPickResponse(
        best_picks=best_picks, counter_picks=counter_picks, synergy_picks=synergy_picks,
        meta=HeroPickMeta(**result["meta"]),
    )
