"""
Unified explanation schema shared by all three AI modules (win prediction,
hero recommendation, build recommendation), so a frontend "Why?" panel can
render any of them with one component instead of three bespoke ones.

Two concerns are deliberately kept separate:
  - `factors`: WHY this specific output was produced (the reasoning).
  - `confidence`: HOW MUCH the user should trust it (the provenance).
A recommendation can have a crystal-clear reason and still deserve low
trust (e.g. a Tier 3 role-default build has a perfectly clear rule behind
it, but zero historical backing). Conflating the two would hide that.
"""
from dataclasses import dataclass, field, asdict

VALID_LEVELS = {"high", "medium", "low"}
VALID_SOURCES = {"curated_data", "transferred_data", "heuristic_default", "model_inference"}
VALID_DIRECTIONS = {"positive", "negative", "neutral"}
VALID_MODULES = {"win_prediction", "hero_recommendation", "build_recommendation"}


@dataclass
class ExplanationFactor:
    label: str
    description: str
    value: float | None = None
    direction: str = "neutral"

    def __post_init__(self):
        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(f"Invalid direction '{self.direction}', must be one of {VALID_DIRECTIONS}")


@dataclass
class Confidence:
    level: str       # "high" | "medium" | "low" — how much to trust this output
    source: str      # where the underlying signal comes from
    basis: str       # human-readable justification — must always disclose data caveats, never omit them

    def __post_init__(self):
        if self.level not in VALID_LEVELS:
            raise ValueError(f"Invalid confidence level '{self.level}', must be one of {VALID_LEVELS}")
        if self.source not in VALID_SOURCES:
            raise ValueError(f"Invalid confidence source '{self.source}', must be one of {VALID_SOURCES}")


@dataclass
class Explanation:
    module: str
    summary: str
    factors: list[ExplanationFactor] = field(default_factory=list)
    confidence: Confidence | None = None

    def __post_init__(self):
        if self.module not in VALID_MODULES:
            raise ValueError(f"Invalid module '{self.module}', must be one of {VALID_MODULES}")

    def to_dict(self) -> dict:
        return asdict(self)
