from pydantic import BaseModel, Field

from app.schemas.common import ExplanationSchema, LanePicks


class WinPredictionRequest(BaseModel):
    ally_picks: LanePicks = Field(..., description="All 5 lanes must be filled — this predicts a complete draft.")
    enemy_picks: LanePicks
    ally_bans: list[int] = Field(default_factory=list)
    enemy_bans: list[int] = Field(default_factory=list)
    patch_version: str | None = Field(None, description="Defaults to the current patch if omitted.")
    rank: str = "Mythic"


class WinPredictionResponse(BaseModel):
    win_probability: float
    patch_version: str
    explanation: ExplanationSchema
