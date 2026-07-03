import secrets

# URL-safe base62 alphabet; excludes lookalike-prone symbols by design.
_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Reserved paths that must never be used as a short code.
RESERVED = frozenset({"api", "healthz", "readyz", "metrics", "docs", "openapi.json", "redoc"})


def generate_code(length: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
