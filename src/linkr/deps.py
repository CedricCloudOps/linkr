from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from .cache import Cache
from .database import get_db


def get_cache(request: Request) -> Cache:
    return request.app.state.cache


# Reusable dependency annotations (FastAPI's Annotated style).
DbSession = Annotated[Session, Depends(get_db)]
CacheDep = Annotated[Cache, Depends(get_cache)]
