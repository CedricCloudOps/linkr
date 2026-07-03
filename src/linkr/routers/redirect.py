from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from .. import service
from ..config import settings
from ..deps import CacheDep, DbSession
from ..metrics import CACHE_HITS, CACHE_MISSES, REDIRECTS

router = APIRouter()


@router.get("/{code}", include_in_schema=False)
def redirect(code: str, request: Request, db: DbSession, cache: CacheDep) -> RedirectResponse:
    cached = cache.get(code)
    if cached is not None:
        CACHE_HITS.inc()
        link_id_raw, target = cached.split("|", 1)
        link_id = int(link_id_raw)
    else:
        CACHE_MISSES.inc()
        link = service.get_active_link(db, code)
        if not link:
            raise HTTPException(status_code=404, detail="link not found")
        link_id, target = link.id, link.target_url
        cache.set(code, f"{link_id}|{target}", settings.cache_ttl_seconds)

    # Analytics are best-effort: a logging failure must never break a redirect.
    try:
        service.record_click(
            db,
            link_id,
            request.headers.get("referer"),
            request.headers.get("user-agent"),
        )
    except Exception:  # noqa: BLE001
        db.rollback()

    REDIRECTS.inc()
    return RedirectResponse(url=target, status_code=302)
