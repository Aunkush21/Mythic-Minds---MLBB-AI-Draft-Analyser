from datetime import date

from pydantic import BaseModel


class HeroSummary(BaseModel):
    id: int
    name: str
    role: str
    secondary_role: str | None
    specialty: str
    damage_type: str
    preferred_lane: str
    difficulty: int
    is_meta: bool
    is_op: bool

    class Config:
        from_attributes = True


class HeroStatsSummary(BaseModel):
    patch_version: str
    win_rate: float | None
    pick_rate: float | None
    ban_rate: float | None

    class Config:
        from_attributes = True


class HeroDetail(HeroSummary):
    stats: list[HeroStatsSummary] = []


class SimilarHeroEntry(BaseModel):
    hero_id: int
    hero_name: str
    similarity: float


class ItemSummary(BaseModel):
    id: int
    name: str
    type: str
    tier: int
    cost: int

    class Config:
        from_attributes = True


class EmblemSummary(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True


class BattleSpellSummary(BaseModel):
    id: int
    name: str
    description: str
    cooldown: int

    class Config:
        from_attributes = True


class HeroCounterEntry(BaseModel):
    hero_id: int
    countered_by_id: int
    counter_score: float
    reason: str | None
    patch_version: str

    class Config:
        from_attributes = True


class PatchSummary(BaseModel):
    patch_version: str
    release_date: date
    codename: str | None
    is_current: bool

    class Config:
        from_attributes = True
