from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.hero import HeroDetail, HeroSummary, SimilarHeroEntry
from app.services import reference_data_service
from app.services.hero_recommendation_service import get_similar_heroes

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.get("", response_model=list[HeroSummary])
async def list_heroes(db: AsyncSession = Depends(get_db)):
    return await reference_data_service.list_heroes(db)


@router.get("/{hero_id}", response_model=HeroDetail)
async def get_hero(hero_id: int, db: AsyncSession = Depends(get_db)):
    return await reference_data_service.get_hero(db, hero_id)


@router.get("/{hero_id}/similar", response_model=list[SimilarHeroEntry])
def similar_heroes(hero_id: int, limit: int = Query(5, ge=1, le=20)):
    return get_similar_heroes(hero_id, limit)
