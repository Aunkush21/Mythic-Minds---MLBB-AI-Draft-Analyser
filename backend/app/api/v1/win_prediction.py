from fastapi import APIRouter

from app.schemas.win_prediction import WinPredictionRequest, WinPredictionResponse
from app.services import win_prediction_service

router = APIRouter(prefix="/predict", tags=["win-prediction"])


@router.post("/win-probability", response_model=WinPredictionResponse)
def predict_win_probability(request: WinPredictionRequest):
    """
    Regular `def`, not `async def`: this endpoint is CPU-bound (pandas
    feature engineering + XGBoost inference + SHAP), not I/O-bound.
    FastAPI automatically runs sync route handlers in a thread pool, which
    is the correct behavior here — making this `async def` without an
    actual await inside would block the event loop instead of helping it.
    """
    return win_prediction_service.predict(request)
