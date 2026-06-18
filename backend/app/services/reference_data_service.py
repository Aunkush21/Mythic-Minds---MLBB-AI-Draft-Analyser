"""
Live Postgres reads for catalog/reference data — heroes, items, emblems,
battle spells, patches. Unlike the ML services, these go straight to the
database via SQLAlchemy async session rather than the ml/ parquet
snapshots, since reference data should reflect the current DB state
immediately, not a snapshot that's stale until the next extraction run.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import HeroNotFoundError, PatchNotFoundError
from app.db.models import BattleSpell, Emblem, Hero, HeroCounter, HeroStats, Item, PatchHistory


async def list_heroes(db: AsyncSession) -> list[Hero]:
    result = await db.execute(select(Hero).order_by(Hero.name))
    return list(result.scalars().all())


async def get_hero(db: AsyncSession, hero_id: int) -> Hero:
    result = await db.execute(
        select(Hero).where(Hero.id == hero_id).options(selectinload(Hero.stats))
    )
    hero = result.scalar_one_or_none()
    if hero is None:
        raise HeroNotFoundError(f"No hero with id {hero_id}.")
    return hero


async def list_items(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item).order_by(Item.name))
    return list(result.scalars().all())


async def list_emblems(db: AsyncSession) -> list[Emblem]:
    result = await db.execute(select(Emblem).order_by(Emblem.name))
    return list(result.scalars().all())


async def list_battle_spells(db: AsyncSession) -> list[BattleSpell]:
    result = await db.execute(select(BattleSpell).order_by(BattleSpell.name))
    return list(result.scalars().all())


async def list_patches(db: AsyncSession) -> list[PatchHistory]:
    result = await db.execute(select(PatchHistory).order_by(PatchHistory.release_date.desc()))
    return list(result.scalars().all())


async def list_counters(db: AsyncSession) -> list[HeroCounter]:
    result = await db.execute(select(HeroCounter).order_by(HeroCounter.hero_id))
    return list(result.scalars().all())


async def get_current_patch(db: AsyncSession) -> PatchHistory:
    result = await db.execute(select(PatchHistory).where(PatchHistory.is_current.is_(True)))
    patch = result.scalar_one_or_none()
    if patch is None:
        raise PatchNotFoundError("No patch is currently marked as is_current.")
    return patch
