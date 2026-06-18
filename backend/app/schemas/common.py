"""
Pydantic mirror of ml/src/explainability/schema.py's dataclasses.

Kept as a separate, parallel definition rather than importing the ml/
dataclasses directly — the ML layer is deliberately framework-agnostic
(no FastAPI/Pydantic dependency), and the API layer is where HTTP
concerns (validation, OpenAPI schema generation) belong. The service
layer (see services/) converts ml/ dataclass instances into these
Pydantic models at the boundary.
"""
from enum import Enum

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ConfidenceSource(str, Enum):
    curated_data = "curated_data"
    transferred_data = "transferred_data"
    heuristic_default = "heuristic_default"
    model_inference = "model_inference"


class Direction(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class ExplanationFactorSchema(BaseModel):
    label: str
    description: str
    value: float | None = None
    direction: Direction = Direction.neutral


class ConfidenceSchema(BaseModel):
    level: ConfidenceLevel
    source: ConfidenceSource
    basis: str = Field(..., description="Human-readable justification — always discloses data provenance caveats.")


class ExplanationSchema(BaseModel):
    module: str
    summary: str
    factors: list[ExplanationFactorSchema] = Field(default_factory=list)
    confidence: ConfidenceSchema


class LanePicks(BaseModel):
    """Hero IDs by lane. Use null for an unfilled slot."""
    exp: int | None = None
    gold: int | None = None
    mid: int | None = None
    jungle: int | None = None
    roam: int | None = None

    def to_dict(self) -> dict[str, int | None]:
        return {"exp": self.exp, "gold": self.gold, "mid": self.mid, "jungle": self.jungle, "roam": self.roam}

    def filled_ids(self) -> list[int]:
        return [v for v in self.to_dict().values() if v is not None]


class ErrorResponse(BaseModel):
    error_code: str
    detail: str
