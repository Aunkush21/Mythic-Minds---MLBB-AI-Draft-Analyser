"""
FastAPI application entrypoint.

Startup eagerly warms the ML caches (trained model, hero similarity
matrix, curated build/counter/synergy tables) so the first real request
isn't the one paying for it — these are loaded once via lru_cache'd
DataContext singletons in ml/, not per-request.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

logger = logging.getLogger("mlbb_backend")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Warming ML caches...")
    try:
        from app.services.ml_bridge import get_recommendation_data_context, load_build_recommendation_engine

        get_recommendation_data_context()
        load_build_recommendation_engine().get_build_context()
        logger.info("ML caches warmed successfully.")
    except Exception:
        logger.exception(
            "Failed to warm ML caches at startup — ML endpoints will error until this is resolved "
            "(commonly: ml/data/raw/*.parquet missing, run ml/src/data/extract.py first)."
        )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "REST API for the MLBB AI Draft Intelligence Platform — win probability "
        "prediction, hero recommendation, and build recommendation, each with a "
        "unified explainability layer."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
