from fastapi import APIRouter

from app.schemas.build_recommendation import BuildRequest, BuildResponse
from app.services import build_recommendation_service

router = APIRouter(prefix="/recommendations", tags=["build-recommendation"])


@router.post("/build", response_model=BuildResponse)
def recommend_build(request: BuildRequest):
    """Sync `def` — see win_prediction.py for why (CPU-bound, not I/O-bound)."""
    return build_recommendation_service.recommend(request)
