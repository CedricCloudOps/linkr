import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import __version__, models  # noqa: F401 - import models so tables register
from .cache import build_cache
from .config import settings
from .database import Base, engine
from .metrics import MetricsMiddleware
from .routers import health, links, redirect

logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cache = build_cache(settings)
    # Schema is owned by Alembic in production; auto-create only for local/dev.
    if settings.env != "production":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="linkr", version=__version__, lifespan=lifespan)
app.add_middleware(MetricsMiddleware)

# Order matters: the catch-all redirect route must be registered last.
app.include_router(health.router)
app.include_router(links.router)
app.include_router(redirect.router)


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {"service": "linkr", "version": __version__, "docs": "/docs"}
