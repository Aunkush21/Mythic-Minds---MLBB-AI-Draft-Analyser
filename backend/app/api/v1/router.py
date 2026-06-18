from fastapi import APIRouter

from app.api.v1 import admin, build_recommendation, hero_recommendation, heroes, reference_data, win_prediction

api_router = APIRouter()
api_router.include_router(heroes.router)
api_router.include_router(reference_data.router)
api_router.include_router(win_prediction.router)
api_router.include_router(hero_recommendation.router)
api_router.include_router(build_recommendation.router)
api_router.include_router(admin.router)
