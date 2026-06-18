from fastapi import APIRouter

from app.services.ml_bridge import refresh_ml_data

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/refresh-ml-data")
def refresh_ml_data_endpoint():
    """
    The ML engines read from pre-extracted parquet snapshots
    (ml/data/raw/), not live Postgres — call this after editing
    heroes/items/builds/counters/synergies/patches in the database so
    the running server picks up the change without a restart.
    """
    row_counts = refresh_ml_data()
    return {"status": "refreshed", "row_counts": row_counts}
