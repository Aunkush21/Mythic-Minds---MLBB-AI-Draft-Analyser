from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.hero import (
    BattleSpellSummary,
    EmblemSummary,
    HeroCounterEntry,
    ItemSummary,
    PatchSummary,
)
from app.services import reference_data_service

router = APIRouter(tags=["reference-data"])


@router.get("/items", response_model=list[ItemSummary])
async def list_items(db: AsyncSession = Depends(get_db)):
    return await reference_data_service.list_items(db)


@router.get("/counters", response_model=list[HeroCounterEntry])
async def list_counters(db: AsyncSession = Depends(get_db)):
    """Full hero_counters table — used by the frontend to build the
    counter-pick heatmap client-side rather than computing it per-pair on
    the server, since the matrix is small (40 heroes) and static per patch.
    """
    return await reference_data_service.list_counters(db)


@router.get("/emblems", response_model=list[EmblemSummary])
async def list_emblems(db: AsyncSession = Depends(get_db)):
    return await reference_data_service.list_emblems(db)


@router.get("/battle-spells", response_model=list[BattleSpellSummary])
async def list_battle_spells(db: AsyncSession = Depends(get_db)):
    return await reference_data_service.list_battle_spells(db)


@router.get("/patches", response_model=list[PatchSummary])
async def list_patches(db: AsyncSession = Depends(get_db)):
    return await reference_data_service.list_patches(db)


@router.get("/patches/current", response_model=PatchSummary)
async def get_current_patch(db: AsyncSession = Depends(get_db)):
    return await reference_data_service.get_current_patch(db)
