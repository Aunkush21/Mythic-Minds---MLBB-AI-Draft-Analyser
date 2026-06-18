"""
Loads all reference data once into memory — heroes, hero_stats, counters,
synergies, patches, the trained win predictor, and a precomputed hero
similarity matrix. Designed to be loaded once at API startup and reused
across requests (40 heroes / ~40 counters / ~30 synergies is trivially
small — no per-request DB round trip needed).
"""
import sys
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "features"))

from config import DATA_RAW_DIR, MODELS_DIR
from counter_features import build_counter_lookup
from synergy_features import build_synergy_lookup
from meta_features import build_hero_stats_lookup
from utils import nearest_patch_leq

from similarity import build_similarity_matrix

MODEL_VERSION = "v1"


class DataContext:
    def __init__(self):
        self.heroes = pd.read_parquet(DATA_RAW_DIR / "heroes.parquet").set_index("id")
        hero_stats = pd.read_parquet(DATA_RAW_DIR / "hero_stats.parquet")
        counters = pd.read_parquet(DATA_RAW_DIR / "counters.parquet")
        synergies = pd.read_parquet(DATA_RAW_DIR / "synergies.parquet")
        patches = pd.read_parquet(DATA_RAW_DIR / "patches.parquet")

        self.hero_stats_lookup = build_hero_stats_lookup(hero_stats)
        self.counter_lookup = build_counter_lookup(counters)
        self.synergy_lookup = build_synergy_lookup(synergies)

        current_rows = patches[patches["is_current"]]
        self.current_patch = (
            current_rows.iloc[0]["patch_version"]
            if len(current_rows) else patches["patch_version"].iloc[-1]
        )

        self.similarity_matrix, self.similarity_hero_ids = build_similarity_matrix(
            self.heroes, hero_stats
        )

        model_dir = MODELS_DIR / MODEL_VERSION
        self.win_model = None
        self.win_model_feature_columns = None
        self.win_model_feature_groups = None
        if (model_dir / "model.json").exists():
            self.win_model = xgb.XGBClassifier()
            self.win_model.load_model(model_dir / "model.json")
            self.win_model_feature_columns = joblib.load(model_dir / "feature_columns.pkl")
            import json
            with open(model_dir / "metadata.json") as f:
                self.win_model_feature_groups = json.load(f)["feature_groups"]

    def resolve_patch(self, requested_patch: str | None) -> str:
        if requested_patch is None:
            return self.current_patch
        available = set(self.hero_stats_lookup.keys())
        return nearest_patch_leq(requested_patch, list(available)) if available else requested_patch


@lru_cache(maxsize=1)
def get_context() -> DataContext:
    return DataContext()
