"""
SQLAlchemy ORM models mirroring database/schema.sql's reference/catalog
tables — used only by the read-heavy reference-data endpoints (heroes,
items, emblems, battle spells, patches). The ML inference endpoints do
NOT go through these models; they use the existing ml/ engines, which
read from pre-extracted parquet snapshots (see ml/src/data/extract.py)
rather than live Postgres. See backend/README.md for why that split is
deliberate.

`create_type=False` on every PGEnum/ARRAY-of-enum below because these
Postgres ENUM types already exist (created by database/schema.sql) —
SQLAlchemy must not try to CREATE TYPE again.
"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


HeroRoleEnum = PGEnum(
    "Tank", "Fighter", "Assassin", "Mage", "Marksman", "Support",
    name="hero_role", create_type=False,
)
HeroSpecialtyEnum = PGEnum(
    "Crowd Control", "Damage", "Initiator", "Pusher", "Reap", "Poke", "Guard", "Heal", "Support",
    name="hero_specialty", create_type=False,
)
DamageTypeEnum = PGEnum("Physical", "Magic", "Hybrid", name="damage_type", create_type=False)
LaneTypeEnum = PGEnum("EXP", "Gold", "Mid", "Jungle", "Roam", name="lane_type", create_type=False)
ItemTypeEnum = PGEnum(
    "Attack", "Magic", "Defense", "Movement", "Jungle", "Roam",
    name="item_type", create_type=False,
)
EmblemTypeEnum = PGEnum(
    "Assassin", "Fighter", "Mage", "Marksman", "Support", "Tank", "Common",
    name="emblem_type", create_type=False,
)


class Hero(Base):
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(HeroRoleEnum, nullable=False)
    secondary_role: Mapped[str | None] = mapped_column(HeroRoleEnum, nullable=True)
    specialty: Mapped[str] = mapped_column(HeroSpecialtyEnum, nullable=False)
    damage_type: Mapped[str] = mapped_column(DamageTypeEnum, nullable=False)
    preferred_lane: Mapped[str] = mapped_column(LaneTypeEnum, nullable=False)
    difficulty: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    release_patch: Mapped[str | None] = mapped_column(
        String(10), ForeignKey("patch_history.patch_version"), nullable=True
    )
    is_meta: Mapped[bool] = mapped_column(Boolean, default=False)
    is_op: Mapped[bool] = mapped_column(Boolean, default=False)
    portrait_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)

    stats: Mapped[list["HeroStats"]] = relationship(back_populates="hero")


class HeroStats(Base):
    __tablename__ = "hero_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hero_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"), nullable=False)
    patch_version: Mapped[str] = mapped_column(
        String(10), ForeignKey("patch_history.patch_version"), nullable=False
    )
    base_hp: Mapped[int] = mapped_column(Integer, nullable=False)
    base_mana: Mapped[int | None] = mapped_column(Integer, nullable=True)
    base_armor: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    base_magic_res: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    base_atk_spd: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    base_phys_atk: Mapped[int] = mapped_column(Integer, nullable=False)
    base_magic_pwr: Mapped[int] = mapped_column(Integer, default=0)
    movement_spd: Mapped[int] = mapped_column(Integer, nullable=False)
    hp_growth: Mapped[float | None] = mapped_column(Numeric(6, 1), nullable=True)
    armor_growth: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    atk_growth: Mapped[float | None] = mapped_column(Numeric(4, 1), nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    pick_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    ban_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    hero: Mapped["Hero"] = relationship(back_populates="stats")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(ItemTypeEnum, nullable=False)
    tier: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    phys_atk: Mapped[int] = mapped_column(Integer, default=0)
    magic_pwr: Mapped[int] = mapped_column(Integer, default=0)
    phys_def: Mapped[int] = mapped_column(Integer, default=0)
    magic_def: Mapped[int] = mapped_column(Integer, default=0)
    max_hp: Mapped[int] = mapped_column(Integer, default=0)
    hp_regen: Mapped[int] = mapped_column(Integer, default=0)
    mana: Mapped[int] = mapped_column(Integer, default=0)
    mana_regen: Mapped[int] = mapped_column(Integer, default=0)
    crit_chance: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    atk_speed: Mapped[float] = mapped_column(Numeric(4, 2), default=0)
    lifesteal: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    movement_spd: Mapped[int] = mapped_column(Integer, default=0)
    phys_pen: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    magic_pen: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    cooldown_red: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    passive_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    passive_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    active_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    patch_version: Mapped[str] = mapped_column(
        String(10), ForeignKey("patch_history.patch_version"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Emblem(Base):
    __tablename__ = "emblems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(EmblemTypeEnum, nullable=False)
    phys_atk_bonus: Mapped[float] = mapped_column(Numeric(5, 1), default=0)
    magic_pwr_bonus: Mapped[float] = mapped_column(Numeric(5, 1), default=0)
    hp_bonus: Mapped[int] = mapped_column(Integer, default=0)
    armor_bonus: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    magic_res_bonus: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    cdr_bonus: Mapped[float] = mapped_column(Numeric(4, 1), default=0)
    movement_bonus: Mapped[int] = mapped_column(Integer, default=0)
    talent_1: Mapped[str | None] = mapped_column(String(60), nullable=True)
    talent_2: Mapped[str | None] = mapped_column(String(60), nullable=True)
    talent_3: Mapped[str | None] = mapped_column(String(60), nullable=True)
    recommended_roles: Mapped[list[str] | None] = mapped_column(ARRAY(HeroRoleEnum), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)


class BattleSpell(Base):
    __tablename__ = "battle_spells"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cooldown: Mapped[int] = mapped_column(Integer, nullable=False)
    unlock_level: Mapped[int] = mapped_column(Integer, default=1)
    recommended_roles: Mapped[list[str] | None] = mapped_column(ARRAY(HeroRoleEnum), nullable=True)
    recommended_lanes: Mapped[list[str] | None] = mapped_column(ARRAY(LaneTypeEnum), nullable=True)
    use_case: Mapped[str | None] = mapped_column(Text, nullable=True)
    patch_version: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)


class HeroBuild(Base):
    __tablename__ = "hero_builds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hero_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"), nullable=False)
    build_name: Mapped[str] = mapped_column(String(80), nullable=False)
    item_1: Mapped[int | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    item_2: Mapped[int | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    item_3: Mapped[int | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    item_4: Mapped[int | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    item_5: Mapped[int | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    item_6: Mapped[int | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    emblem_id: Mapped[int | None] = mapped_column(ForeignKey("emblems.id"), nullable=True)
    spell_id: Mapped[int | None] = mapped_column(ForeignKey("battle_spells.id"), nullable=True)
    is_core: Mapped[bool] = mapped_column(Boolean, default=True)
    situation: Mapped[str | None] = mapped_column(String(40), nullable=True)
    patch_version: Mapped[str] = mapped_column(
        String(10), ForeignKey("patch_history.patch_version"), nullable=False
    )
    win_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)


class HeroCounter(Base):
    __tablename__ = "hero_counters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hero_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"), nullable=False)
    countered_by_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"), nullable=False)
    counter_score: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    patch_version: Mapped[str] = mapped_column(
        String(10), ForeignKey("patch_history.patch_version"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)


class HeroSynergy(Base):
    __tablename__ = "hero_synergies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hero_a_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"), nullable=False)
    hero_b_id: Mapped[int] = mapped_column(ForeignKey("heroes.id"), nullable=False)
    synergy_score: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    combo_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    patch_version: Mapped[str] = mapped_column(
        String(10), ForeignKey("patch_history.patch_version"), nullable=False
    )
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)


class PatchHistory(Base):
    __tablename__ = "patch_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patch_version: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    codename: Mapped[str | None] = mapped_column(String(80), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    heroes_added: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    heroes_reworked: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(nullable=True)
