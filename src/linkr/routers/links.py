from fastapi import APIRouter, HTTPException, Response

from .. import service
from ..config import settings
from ..deps import CacheDep, DbSession
from ..schemas import LinkCreate, LinkResponse, StatsResponse

router = APIRouter(prefix="/api/v1/links", tags=["links"])

_MAX_STATS_WINDOW_DAYS = 90


def _short_url(code: str) -> str:
    return f"{settings.base_url.rstrip('/')}/{code}"


@router.post("", response_model=LinkResponse, status_code=201)
def create_link(payload: LinkCreate, db: DbSession) -> LinkResponse:
    try:
        link = service.create_link(db, str(payload.url), payload.custom_alias)
    except service.InvalidAlias as exc:
        raise HTTPException(status_code=422, detail="alias is reserved") from exc
    except service.AliasConflict as exc:
        raise HTTPException(status_code=409, detail="alias already in use") from exc
    return LinkResponse(
        code=link.code,
        short_url=_short_url(link.code),
        target_url=link.target_url,
        created_at=link.created_at,
        total_clicks=0,
    )


@router.get("/{code}", response_model=LinkResponse)
def get_link(code: str, db: DbSession) -> LinkResponse:
    link = service.get_active_link(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    return LinkResponse(
        code=link.code,
        short_url=_short_url(link.code),
        target_url=link.target_url,
        created_at=link.created_at,
        total_clicks=service.count_clicks(db, link.id),
    )


@router.get("/{code}/stats", response_model=StatsResponse)
def get_stats(code: str, db: DbSession, days: int = 7) -> StatsResponse:
    link = service.get_active_link(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    days = max(1, min(days, _MAX_STATS_WINDOW_DAYS))
    return StatsResponse(
        code=code,
        total_clicks=service.count_clicks(db, link.id),
        window_days=days,
        by_day=service.daily_stats(db, link.id, days),
    )


@router.delete("/{code}", status_code=204)
def delete_link(code: str, db: DbSession, cache: CacheDep) -> Response:
    link = service.get_active_link(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    service.deactivate_link(db, link)
    cache.delete(code)
    return Response(status_code=204)
