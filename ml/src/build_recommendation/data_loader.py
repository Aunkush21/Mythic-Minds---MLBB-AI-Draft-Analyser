"""
Loads items/emblems/spells/hero_builds, and reuses the Hero Recommendation
Engine's DataContext (heroes, similarity matrix, patch resolution) rather
than duplicating that loading logic.
"""
import importlib.util
import sys
from functools import lru_cache
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import DATA_RAW_DIR
from item_tags import tag_items


def _load_recommendation_data_loader():
    """
    Loaded via importlib (not sys.path + import) because both this file
    and ../recommendation/data_loader.py are named `data_loader.py` — a
    plain `from data_loader import ...` would resolve to whichever one
    Python's import cache saw first, silently shadowing the other.

    Checks sys.modules first (under this fixed key) before exec'ing —
    important once multiple services share one long-running process (the
    FastAPI backend): without this guard, every caller would re-execute
    and re-load a brand new recommendation DataContext (heroes, win
    model, similarity matrix) instead of reusing the one already built.
    """
    if "recommendation_data_loader" in sys.modules:
        return sys.modules["recommendation_data_loader"]

    recommendation_dir = Path(__file__).resolve().parents[1] / "recommendation"
    # Appended, not inserted at front: build_recommendation's own same-named
    # files (e.g. explain.py exists in both folders) must keep resolving to
    # themselves first. This module's own directory is already at sys.path[0]
    # (inserted by engine.py before it imported this file).
    sys.path.append(str(recommendation_dir))

    path = recommendation_dir / "data_loader.py"
    spec = importlib.util.spec_from_file_location("recommendation_data_loader", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["recommendation_data_loader"] = module
    spec.loader.exec_module(module)
    return module


_rec_data_loader = _load_recommendation_data_loader()
get_recommendation_context = _rec_data_loader.get_context


class BuildDataContext:
    def __init__(self):
        self.recommendation_ctx = get_recommendation_context()
        self.heroes = self.recommendation_ctx.heroes
        self.similarity_matrix = self.recommendation_ctx.similarity_matrix
        self.similarity_hero_ids = self.recommendation_ctx.similarity_hero_ids
        self.current_patch = self.recommendation_ctx.current_patch

        items = pd.read_parquet(DATA_RAW_DIR / "items.parquet")
        self.items = tag_items(items).set_index("id")
        self.emblems = pd.read_parquet(DATA_RAW_DIR / "emblems.parquet").set_index("id")
        self.spells = pd.read_parquet(DATA_RAW_DIR / "spells.parquet").set_index("id")
        self.hero_builds = pd.read_parquet(DATA_RAW_DIR / "hero_builds.parquet")

    def resolve_patch(self, requested_patch: str | None) -> str:
        return self.recommendation_ctx.resolve_patch(requested_patch)


@lru_cache(maxsize=1)
def get_build_context() -> BuildDataContext:
    return BuildDataContext()