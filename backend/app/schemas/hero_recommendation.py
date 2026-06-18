from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ExplanationSchema, LanePicks

LaneName = Literal["exp", "gold", "mid", "jungle", "roam"]


class HeroPickRequest(BaseModel):
    ally_picks: LanePicks
    enemy_picks: LanePicks
    banned_heroes: list[int] = Field(default_factory=list)
    target_lane: LaneName
    patch_version: str | None = None
    rank_tier: str | None = None
    top_k: int = Field(5, ge=1, le=10)


class BestPickEntry(BaseModel):
    hero_id: int
    hero_name: str
    composite_score: float
    explanation: str
    win_prob_uplift: float | None = None
    unified_explanation: ExplanationSchema


class CounterPickEntry(BaseModel):
    hero_id: int
    hero_name: str
    counter_score: float
    countered_enemy_heroes: list[str]
    unified_explanation: ExplanationSchema


class SynergyPickEntry(BaseModel):
    hero_id: int
    hero_name: str
    synergy_score: float
    synergized_ally_heroes: list[str]
    unified_explanation: ExplanationSchema


class HeroPickMeta(BaseModel):
    patch_version: str
    candidates_considered: int
    win_prob_uplift_used: bool


class HeroPickResponse(BaseModel):
    best_picks: list[BestPickEntry]
    counter_picks: list[CounterPickEntry]
    synergy_picks: list[SynergyPickEntry]
    meta: HeroPickMeta
