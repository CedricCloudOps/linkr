from typing import Optional, Protocol

from .config import Settings


class Cache(Protocol):
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str, ttl: int) -> None: ...
    def delete(self, key: str) -> None: ...


class InMemoryCache:
    """Fallback cache used in local dev and tests when Redis is not configured.

    Not suitable for multi-replica production: state is per-process.
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    def set(self, key: str, value: str, ttl: int) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


class RedisCache:
    def __init__(self, client) -> None:
        self._client = client

    def get(self, key: str) -> Optional[str]:
        return self._client.get(key)

    def set(self, key: str, value: str, ttl: int) -> None:
        self._client.set(key, value, ex=ttl)

    def delete(self, key: str) -> None:
        self._client.delete(key)


def build_cache(settings: Settings) -> Cache:
    if settings.redis_url:
        import redis  # imported lazily so tests don't require the driver

        client = redis.from_url(settings.redis_url, decode_responses=True)
        return RedisCache(client)
    return InMemoryCache()
