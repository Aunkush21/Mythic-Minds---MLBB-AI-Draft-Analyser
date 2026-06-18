from pydantic import BaseModel, Field

from app.schemas.common import ExplanationSchema


class BuildRequest(BaseModel):
    hero_id: int
    enemy_picks: list[int] = Field(default_factory=list, description="Hero IDs already drafted by the enemy team.")
    patch_version: str | None = None


class ThreatProfile(BaseModel):
    physical_count: int
    magic_count: int
    tank_count: int
    burst_threat_score: int
    cc_density: int
    sustain_threat: int


class BuildResponse(BaseModel):
    hero_name: str
    tier: str
    items: list[str]
    emblem: str
    battle_spell: str
    explanation: list[str]
    threat_profile: ThreatProfile
    patch_version: str
    unified_explanation: ExplanationSchema
