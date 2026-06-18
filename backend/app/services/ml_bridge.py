"""
Bridges the FastAPI backend to the existing ml/ codebase without modifying
ml/'s actual logic (only one small, justified efficiency fix was made to
build_recommendation/data_loader.py — see its docstring).

ml/'s modules use flat sys.path-based imports rather than an installable
package (a deliberate earlier choice, documented in each module). That
works fine for standalone scripts, each running in its own process. The
FastAPI backend is different: it loads BOTH recommendation/ and
build_recommendation/ into ONE long-running process, and those two
folders each define their own engine.py, data_loader.py, and explain.py.
A plain `import engine` would silently resolve to whichever one Python's
sys.modules cache saw first and stay wrong for the rest of the process.

The fix: load each folder's engine.py by explicit file path, with the
three colliding bare names removed from sys.modules immediately before
the import and cleaned up immediately after — so each folder's internal
sibling imports (`from data_loader import ...`, `from explain import
...`) resolve to themselves regardless of which folder was touched first.

Each loader is memoized (loaded once per process, not once per request)
so the expensive parts — the trained model, the hero similarity matrix —
are built once and reused, exactly as the lru_cache'd DataContext classes
already intend.

Known, accepted tradeoff: build_recommendation's engine internally builds
its own recommendation DataContext (for similarity-transfer), separate
from the one win-prediction/hero-recommendation share. That's two
DataContext instances total in the process instead of the theoretical
minimum of one — a few hundred KB and well under a second of extra
startup time for 40 heroes, not a correctness issue. Documented here
rather than quietly accepted.
"""
import contextlib
import importlib.util
import sys

from app.core.config import ML_SRC_DIR

_ML_SUBDIRS = ["", "features", "models", "explainability", "recommendation", "build_recommendation"]
_COLLIDING_MODULE_NAMES = ["data_loader", "engine", "explain"]

_loaded_engines: dict[str, object] = {}


def ensure_ml_path() -> None:
    for sub in _ML_SUBDIRS:
        path = str(ML_SRC_DIR / sub) if sub else str(ML_SRC_DIR)
        if path not in sys.path:
            sys.path.append(path)


ensure_ml_path()


@contextlib.contextmanager
def _isolated_folder_import(folder_path):
    """
    Full sys.path save/restore, not just sys.modules cleanup — engine.py
    (and its siblings) insert several of their own directories onto
    sys.path during exec, and those must not leak into the next isolated
    import either, or a later call could resolve a colliding bare name
    against the wrong folder despite sys.modules being clean.
    """
    saved_path = list(sys.path)
    saved_modules = {name: sys.modules.pop(name) for name in _COLLIDING_MODULE_NAMES if name in sys.modules}
    sys.path.insert(0, str(folder_path))
    try:
        yield
    finally:
        sys.path[:] = saved_path
        for name in _COLLIDING_MODULE_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved_modules)


def load_recommendation_engine():
    """The recommendation/engine.py module (recommend_hero_pick). Loaded
    once per process; safe to call from multiple service files."""
    if "recommendation" not in _loaded_engines:
        with _isolated_folder_import(ML_SRC_DIR / "recommendation"):
            import engine
            _loaded_engines["recommendation"] = engine
    return _loaded_engines["recommendation"]


def load_build_recommendation_engine():
    """The build_recommendation/engine.py module (recommend_build)."""
    if "build_recommendation" not in _loaded_engines:
        with _isolated_folder_import(ML_SRC_DIR / "build_recommendation"):
            import engine
            _loaded_engines["build_recommendation"] = engine
    return _loaded_engines["build_recommendation"]


def load_recommendation_explain_module():
    """recommendation/explain.py — the unified-explanation adapter
    functions (to_explanation_best_pick etc.) that engine.py itself never
    re-exports, so they need their own loader."""
    if "recommendation_explain" not in _loaded_engines:
        with _isolated_folder_import(ML_SRC_DIR / "recommendation"):
            import explain
            _loaded_engines["recommendation_explain"] = explain
    return _loaded_engines["recommendation_explain"]


def load_build_recommendation_explain_module():
    if "build_recommendation_explain" not in _loaded_engines:
        with _isolated_folder_import(ML_SRC_DIR / "build_recommendation"):
            import explain
            _loaded_engines["build_recommendation_explain"] = explain
    return _loaded_engines["build_recommendation_explain"]


def load_recommendation_similarity_module():
    """recommendation/similarity.py — not a colliding name (build_recommendation
    has no similarity.py of its own), so no isolation needed, just a clean
    memoized loader for consistency with the rest of this bridge."""
    if "recommendation_similarity" not in _loaded_engines:
        import similarity
        _loaded_engines["recommendation_similarity"] = similarity
    return _loaded_engines["recommendation_similarity"]


def load_win_predictor_module():
    """The ml/src/models/predict.py module (predict_win_probability)."""
    if "win_predictor" not in _loaded_engines:
        with _isolated_folder_import(ML_SRC_DIR / "models"):
            import predict
            _loaded_engines["win_predictor"] = predict
    return _loaded_engines["win_predictor"]


def get_recommendation_data_context():
    """heroes/counter/synergy lookups + win model — shared singleton used
    by win-prediction and hero-recommendation services."""
    return load_recommendation_engine().get_context()


def load_extract_module():
    """ml/src/data/extract.py — Postgres -> parquet snapshot refresh."""
    if "extract" not in _loaded_engines:
        path = str(ML_SRC_DIR / "data")
        if path not in sys.path:
            sys.path.append(path)
        import extract
        _loaded_engines["extract"] = extract
    return _loaded_engines["extract"]


def refresh_ml_data() -> dict[str, int]:
    """
    Re-runs the Postgres -> parquet extraction, then clears every
    lru_cache'd DataContext singleton so the next request rebuilds from
    the fresh snapshot. Clears both the shared recommendation DataContext
    and the separate internal copy build_recommendation loads (see this
    module's docstring on the known dual-instance tradeoff) — otherwise
    half the engines would silently keep serving stale data.
    """
    extract = load_extract_module()
    tables = extract.fetch_all()
    extract.save_raw(tables)

    if "recommendation" in _loaded_engines:
        _loaded_engines["recommendation"].get_context.cache_clear()
    if "build_recommendation" in _loaded_engines:
        _loaded_engines["build_recommendation"].get_build_context.cache_clear()
    if "recommendation_data_loader" in sys.modules:
        sys.modules["recommendation_data_loader"].get_context.cache_clear()

    return {name: len(df) for name, df in tables.items()}


def explanation_to_schema(explanation):
    """Converts an ml/src/explainability/schema.Explanation dataclass into
    the API layer's ExplanationSchema (backend/app/schemas/common.py)."""
    from app.schemas.common import ConfidenceSchema, ExplanationFactorSchema, ExplanationSchema

    return ExplanationSchema(
        module=explanation.module,
        summary=explanation.summary,
        factors=[
            ExplanationFactorSchema(
                label=f.label, description=f.description, value=f.value, direction=f.direction,
            )
            for f in explanation.factors
        ],
        confidence=ConfidenceSchema(
            level=explanation.confidence.level,
            source=explanation.confidence.source,
            basis=explanation.confidence.basis,
        ),
    )
