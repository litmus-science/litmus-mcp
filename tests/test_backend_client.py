"""Unit tests for call_backend — fakes the backend via httpx.MockTransport
through the _transport_override seam, no real network/server involved.
"""

from __future__ import annotations

import httpx
import pytest

from litmus_mcp import backend_client
from litmus_mcp.backend_client import call_backend


def _install_transport(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    monkeypatch.setattr(backend_client, "_transport_override", httpx.MockTransport(handler))


async def test_successful_call_returns_parsed_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    _install_transport(monkeypatch, handler)

    result = await call_backend("GET", "/health")

    assert result == {"ok": True}


async def test_non_2xx_surfaces_as_backend_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": [{"loc": ["body", "x"], "msg": "required"}]})

    _install_transport(monkeypatch, handler)

    result = await call_backend("POST", "/estimate", json_body={})

    assert result["error_type"] == "backend_error"
    assert result["status_code"] == 422
    assert result["backend_detail"] == [{"loc": ["body", "x"], "msg": "required"}]


async def test_non_json_error_body_falls_back_to_text(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, text="Bad Gateway")

    _install_transport(monkeypatch, handler)

    result = await call_backend("POST", "/order-requests")

    assert result["error_type"] == "backend_error"
    assert result["backend_detail"] == "Bad Gateway"


async def test_missing_api_key_short_circuits_without_network_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LITMUS_API_KEY", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should have been made")

    _install_transport(monkeypatch, handler)

    result = await call_backend("POST", "/estimate", require_api_key=True)

    assert result == {
        "error": "LITMUS_API_KEY is not configured",
        "error_type": "missing_api_key",
        "hint": (
            "Set the LITMUS_API_KEY environment variable to a key obtained "
            "from POST /auth/register on your litmus-project backend, then "
            "restart the MCP server."
        ),
    }


async def test_api_key_attached_when_required_and_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LITMUS_API_KEY", "lk_test123")
    seen_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.update(request.headers)
        return httpx.Response(200, json={})

    _install_transport(monkeypatch, handler)

    await call_backend("POST", "/estimate", require_api_key=True)

    assert seen_headers.get("x-api-key") == "lk_test123"


async def test_api_key_never_attached_when_not_required(monkeypatch: pytest.MonkeyPatch) -> None:
    """litmus_get_cro_match must stay a pure public call, even if a key happens
    to be configured in the environment for the other two tools."""
    monkeypatch.setenv("LITMUS_API_KEY", "lk_test123")
    seen_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.update(request.headers)
        return httpx.Response(200, json={})

    _install_transport(monkeypatch, handler)

    await call_backend("POST", "/labs/matches", require_api_key=False)

    assert "x-api-key" not in seen_headers


async def test_connection_error_surfaces_as_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    _install_transport(monkeypatch, handler)

    result = await call_backend("GET", "/health")

    assert result["error_type"] == "connection_error"
    assert "localhost:8000" in result["error"]


async def test_uses_custom_api_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LITMUS_API_BASE", "https://staging.litmus.science")
    seen_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, json={})

    _install_transport(monkeypatch, handler)

    await call_backend("GET", "/health")

    assert seen_urls == ["https://staging.litmus.science/health"]
