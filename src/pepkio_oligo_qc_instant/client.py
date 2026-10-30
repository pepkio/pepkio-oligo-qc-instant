# SPDX-License-Identifier: MIT
"""HTTP client for the Pepkio oligo-qc-instant tool."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .config import TOOL_ID, resolve_api_key, resolve_base_url, resolve_ssl_verify
from .exceptions import PepkioAPIError
from .models import RunResult, parse_run_response

_TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled"})


class PepkioClient:
    """Client for Pepkio Tools REST API (oligo-qc-instant)."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        *,
        timeout: float = 60.0,
        verify: bool | None = None,
    ) -> None:
        self._base_url = resolve_base_url(base_url)
        self._api_key = resolve_api_key(api_key, base_url=self._base_url)
        self._timeout = timeout
        self._verify = resolve_ssl_verify(verify, base_url=self._base_url)
        self._manifest: dict[str, Any] | None = None
        headers: dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        self._http = httpx.Client(
            base_url=self._base_url,
            headers=headers,
            timeout=timeout,
            verify=self._verify,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> PepkioClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @property
    def base_url(self) -> str:
        return self._base_url

    def _require_api_key(self) -> None:
        if not self._api_key:
            raise ValueError(
                "API key required. Set PEPKIO_API_KEY (or LOCAL_PEPKIO_API_KEY for local), "
                "or pass api_key= to PepkioClient."
            )

    def _tool_path(self, suffix: str) -> str:
        return f"/api/tools/v1/tools/{TOOL_ID}{suffix}"

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        try:
            body = response.json()
        except Exception:
            body = {}
        if response.is_success:
            if isinstance(body, dict):
                return body
            return {}
        error = body.get("error", {}) if isinstance(body, dict) else {}
        if isinstance(error, str):
            message = error
            code = None
            details = {}
        elif isinstance(error, dict):
            message = error.get("message", response.reason_phrase or "Request failed")
            code = error.get("code")
            details = error.get("details") if isinstance(error.get("details"), dict) else {}
        else:
            message = response.reason_phrase or "Request failed"
            code = None
            details = {}

        raise PepkioAPIError(
            message,
            status_code=response.status_code,
            code=code,
            details=details,
            response_body=body if isinstance(body, dict) else None,
        )

    def get_manifest(self, *, refresh: bool = False) -> dict[str, Any]:
        """Fetch and cache the tool manifest."""
        if self._manifest is not None and not refresh:
            return self._manifest
        response = self._http.get(self._tool_path("/manifest"))
        data = self._handle_response(response)
        self._manifest = data
        return data

    def list_examples(self) -> list[str]:
        """Return example names from the manifest."""
        manifest = self.get_manifest()
        examples = manifest.get("examples") or []
        return [ex["name"] for ex in examples if isinstance(ex, dict) and ex.get("name")]

    def get_example_input(self, name: str) -> dict[str, Any]:
        """Return input dict for a named manifest example."""
        manifest = self.get_manifest()
        for ex in manifest.get("examples") or []:
            if isinstance(ex, dict) and ex.get("name") == name:
                inp = ex.get("input")
                if isinstance(inp, dict):
                    return inp
                raise PepkioAPIError(f"Example {name!r} has no input dict")
        raise PepkioAPIError(f"Example not found: {name!r}")

    def run(
        self,
        input: dict[str, Any],
        *,
        idempotency_key: str | None = None,
        label: str | None = None,
    ) -> RunResult:
        """Run the tool with the given input."""
        self._require_api_key()
        payload: dict[str, Any] = {"input": input}
        options: dict[str, str] = {}
        if idempotency_key is not None:
            options["idempotency_key"] = idempotency_key
        if label is not None:
            options["label"] = label
        if options:
            payload["options"] = options
        response = self._http.post(self._tool_path("/run"), json=payload)
        data = self._handle_response(response)
        result = parse_run_response(data)
        result.raise_for_error()
        return result

    def get_run(self, run_id: str) -> RunResult:
        """Fetch a run by ID."""
        self._require_api_key()
        response = self._http.get(f"/api/tools/v1/runs/{run_id}")
        data = self._handle_response(response)
        result = parse_run_response(data)
        result.raise_for_error()
        return result

    def wait_for_run(
        self,
        run_id: str,
        *,
        poll_interval: float = 1.0,
        timeout: float = 300.0,
    ) -> RunResult:
        """Poll until the run reaches a terminal status."""
        self._require_api_key()
        deadline = time.monotonic() + timeout
        while True:
            result = self.get_run(run_id)
            if result.status in _TERMINAL_STATUSES:
                return result
            if time.monotonic() >= deadline:
                raise PepkioAPIError(
                    f"Run {run_id} did not complete within {timeout}s (status={result.status})",
                    code="TIMEOUT",
                )
            time.sleep(poll_interval)
