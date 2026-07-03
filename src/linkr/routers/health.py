from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from ..deps import DbSession
from ..metrics import metrics_response

router = APIRouter()


@router.get("/healthz", include_in_schema=False)
def liveness() -> dict:
    """Liveness: the process is running. Cheap and dependency-free."""
    return {"status": "ok"}


@router.get("/readyz", include_in_schema=False)
def readiness(db: DbSession) -> dict:
    """Readiness: the instance can serve traffic (database reachable)."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - readiness must translate any failure
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready"}


@router.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_response()
