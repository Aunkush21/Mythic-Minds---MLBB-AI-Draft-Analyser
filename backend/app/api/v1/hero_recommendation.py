from fastapi import APIRouter

from app.schemas.hero_recommendation import HeroPickRequest, HeroPickResponse
from app.services import hero_recommendation_service

router = APIRouter(prefix="/recommendations", tags=["hero-recommendation"])


@router.post("/hero-pick", response_model=HeroPickResponse)
def recommend_hero_pick(request: HeroPickRequest):
    """Sync `def` — see win_prediction.py for why (CPU-bound, not I/O-bound)."""
    return hero_recommendation_service.recommend(request)
