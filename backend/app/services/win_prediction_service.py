from app.core.exceptions import InvalidDraftError, ModelUnavailableError
from app.core.validation import assert_heroes_exist, assert_no_duplicate_picks
from app.schemas.win_prediction import WinPredictionRequest, WinPredictionResponse
from app.services.ml_bridge import explanation_to_schema, get_recommendation_data_context, load_win_predictor_module


def predict(request: WinPredictionRequest) -> WinPredictionResponse:
    ctx = get_recommendation_data_context()
    valid_ids = set(ctx.heroes.index)

    ally = request.ally_picks.to_dict()
    enemy = request.enemy_picks.to_dict()

    missing_ally = [lane for lane, hid in ally.items() if hid is None]
    missing_enemy = [lane for lane, hid in enemy.items() if hid is None]
    if missing_ally or missing_enemy:
        raise InvalidDraftError(
            f"Win prediction requires a complete 10-hero draft. "
            f"Missing ally lanes: {missing_ally}, missing enemy lanes: {missing_enemy}."
        )

    all_ids = list(ally.values()) + list(enemy.values()) + request.ally_bans + request.enemy_bans
    assert_heroes_exist(all_ids, valid_ids)
    assert_no_duplicate_picks(list(ally.values()), list(enemy.values()), request.ally_bans, request.enemy_bans)

    predict_module = load_win_predictor_module()
    try:
        result = predict_module.predict_win_probability(
            ally_lanes=ally, enemy_lanes=enemy,
            ally_bans=request.ally_bans, enemy_bans=request.enemy_bans,
            patch_version=request.patch_version, rank=request.rank,
        )
    except predict_module.ModelNotLoadedError as e:
        raise ModelUnavailableError(str(e))

    return WinPredictionResponse(
        win_probability=result["win_probability"],
        patch_version=result["patch_version"],
        explanation=explanation_to_schema(result["explanation"]),
    )
