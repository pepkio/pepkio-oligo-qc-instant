# SPDX-License-Identifier: MIT
"""Typed API request/response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from .exceptions import PepkioAPIError


class RunOptions(BaseModel):
    """Optional fields for POST .../run."""

    idempotency_key: str | None = None
    label: str | None = None


class RunResult(BaseModel):
    """Tool run response envelope."""

    model_config = ConfigDict(extra="allow")

    run_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | dict[str, Any] | None = None
    result_url: str | None = None
    permalink: str | None = None
    duration_ms: int | None = None

    def raise_for_error(self) -> None:
        """Raise PepkioAPIError if the run response includes an error field or failed status."""
        if self.error is None:
            return
        err = self.error
        if isinstance(err, str):
            msg = err
            code = None
            details = {}
        elif isinstance(err, dict):
            msg = err.get("message", "Tool run failed")
            code = err.get("code")
            details = err.get("details") if isinstance(err.get("details"), dict) else {}
        else:
            msg = str(err)
            code = None
            details = {}

        raise PepkioAPIError(
            msg,
            code=code,
            details=details,
            response_body={"run_id": self.run_id, "status": self.status, "error": self.error},
        )


def parse_run_response(data: dict[str, Any]) -> RunResult:
    """Parse a run API JSON body into RunResult."""
    return RunResult.model_validate(data)
