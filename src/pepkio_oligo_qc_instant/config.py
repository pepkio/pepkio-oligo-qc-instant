"""Configuration and environment resolution."""

from __future__ import annotations

import os

DEFAULT_API_BASE_URL = "https://tools.pepkio.com"
TOOL_ID = "oligo-qc-instant"


def resolve_base_url(override: str | None = None) -> str:
    """Resolve API base URL from override, PEPKIO_API_BASE_URL, or default."""
    return (override or os.getenv("PEPKIO_API_BASE_URL") or DEFAULT_API_BASE_URL).rstrip("/")


def resolve_ssl_verify(override: bool | None = None, *, base_url: str | None = None) -> bool:
    """Resolve TLS certificate verification (off for localtest.me unless overridden)."""
    if override is not None:
        return override
    env = os.getenv("PEPKIO_SSL_VERIFY")
    if env is not None:
        return env.strip().lower() not in ("0", "false", "no", "off")
    base = base_url or resolve_base_url()
    if "localtest.me" in base:
        return False
    return True


def resolve_api_key(override: str | None = None, *, base_url: str | None = None) -> str | None:
    """Resolve API key from override or environment (local vs production)."""
    if override:
        return override
    base = base_url or resolve_base_url()
    if "localtest.me" in base:
        return os.getenv("LOCAL_PEPKIO_API_KEY") or os.getenv("PEPKIO_API_KEY")
    return os.getenv("PEPKIO_API_KEY")
