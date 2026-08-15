"""Unit tests for PepkioClient with mocked HTTP."""

from __future__ import annotations

import httpx
import pytest

from pepkio_oligo_qc_instant.client import PepkioClient
from pepkio_oligo_qc_instant.config import resolve_api_key, resolve_base_url
from pepkio_oligo_qc_instant.exceptions import PepkioAPIError


def test_resolve_base_url_default():
    assert resolve_base_url() == "https://tools.pepkio.com"
    assert resolve_base_url("https://tools.localtest.me/") == "https://tools.localtest.me"


def test_resolve_api_key(monkeypatch):
    monkeypatch.setenv("PEPKIO_API_KEY", "prod_key_123")
    monkeypatch.setenv("LOCAL_PEPKIO_API_KEY", "local_key_123")

    assert resolve_api_key(base_url="https://tools.pepkio.com") == "prod_key_123"
    assert resolve_api_key(base_url="https://tools.localtest.me") == "local_key_123"
    assert resolve_api_key("override_key") == "override_key"


def test_client_missing_api_key(monkeypatch):
    monkeypatch.delenv("PEPKIO_API_KEY", raising=False)
    monkeypatch.delenv("LOCAL_PEPKIO_API_KEY", raising=False)
    client = PepkioClient(api_key=None, base_url="https://tools.pepkio.com")
    with pytest.raises(ValueError, match="API key required"):
        client.run({"mode": "pair", "polymerase_id": "q5", "fwd_seq": "ATGC", "rev_seq": "GCAT"})


def test_get_manifest_success(mock_manifest):
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tools/v1/tools/oligo-qc-instant/manifest"
        return httpx.Response(200, json=mock_manifest)

    transport = httpx.MockTransport(handle_request)
    with PepkioClient(api_key="test_key", base_url="https://tools.pepkio.com") as client:
        client._http = httpx.Client(base_url=client.base_url, transport=transport)
        manifest = client.get_manifest()
        assert manifest["tool_id"] == "oligo-qc-instant"
        assert len(client.list_examples()) == 2
        assert "pair_q5" in client.list_examples()

        ex_input = client.get_example_input("pair_q5")
        assert ex_input["mode"] == "pair"
        assert ex_input["polymerase_id"] == "q5"


def test_run_success(mock_run_response):
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tools/v1/tools/oligo-qc-instant/run"
        assert request.headers.get("Authorization") == "Bearer test_key"
        return httpx.Response(200, json=mock_run_response)

    transport = httpx.MockTransport(handle_request)
    with PepkioClient(api_key="test_key", base_url="https://tools.pepkio.com") as client:
        client._http = httpx.Client(
            base_url=client.base_url,
            headers={"Authorization": "Bearer test_key"},
            transport=transport,
        )
        result = client.run(
            {
                "mode": "pair",
                "name": "GAPDH",
                "fwd_seq": "GAAGGTGAAGGTCGGAGTC",
                "rev_seq": "GAAGATGGTGATGGGATTTC",
                "polymerase_id": "q5",
            },
            label="test-run",
        )
        assert result.status == "completed"
        assert result.run_id == "run_instant123"
        assert result.result["mode"] == "pair"


def test_get_run_success(mock_run_response):
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tools/v1/runs/run_instant123"
        return httpx.Response(200, json=mock_run_response)

    transport = httpx.MockTransport(handle_request)
    with PepkioClient(api_key="test_key", base_url="https://tools.pepkio.com") as client:
        client._http = httpx.Client(
            base_url=client.base_url,
            headers={"Authorization": "Bearer test_key"},
            transport=transport,
        )
        result = client.get_run("run_instant123")
        assert result.status == "completed"
        assert result.run_id == "run_instant123"


def test_api_error_response():
    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"error": {"message": "Invalid primer sequence", "code": "INVALID_INPUT"}},
        )

    transport = httpx.MockTransport(handle_request)
    with PepkioClient(api_key="test_key", base_url="https://tools.pepkio.com") as client:
        client._http = httpx.Client(
            base_url=client.base_url,
            headers={"Authorization": "Bearer test_key"},
            transport=transport,
        )
        with pytest.raises(PepkioAPIError) as exc_info:
            client.run({"mode": "pair", "polymerase_id": "q5", "fwd_seq": "INVALID", "rev_seq": "ATGC"})
        assert exc_info.value.status_code == 400
        assert "Invalid primer sequence" in str(exc_info.value)
