"""Integration-style tests for the three live-backend tools, dispatched through
server.call_tool() for full coverage of the wiring (not just the handlers in
isolation). The backend is faked via the same httpx.MockTransport seam used in
test_backend_client.py — no real network/server involved.
"""

from __future__ import annotations

import json

import httpx
import pytest

from litmus_mcp import backend_client
from litmus_mcp.server import call_tool


def _install_transport(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    monkeypatch.setattr(backend_client, "_transport_override", httpx.MockTransport(handler))


def _body(result: list) -> dict:
    assert len(result) == 1
    return json.loads(result[0].text)


# ── litmus_get_cro_match ────────────────────────────────────────────────────


async def test_get_cro_match_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/labs/matches"
        assert json.loads(request.content) == {"assay_type": "QPCR_EXPRESSION"}
        return httpx.Response(200, json={
            "matches": [{"id": "lab-1", "name": "Lab One", "profile": {}}],
            "count": 1,
        })

    _install_transport(monkeypatch, handler)

    result = await call_tool("litmus_get_cro_match", {"assay_type": "QPCR_EXPRESSION"})

    assert _body(result) == {
        "matches": [{"id": "lab-1", "name": "Lab One", "profile": {}}],
        "count": 1,
    }


async def test_get_cro_match_never_sends_api_key_even_if_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LITMUS_API_KEY", "lk_test123")
    seen_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.update(request.headers)
        return httpx.Response(200, json={"matches": [], "count": 0})

    _install_transport(monkeypatch, handler)

    await call_tool("litmus_get_cro_match", {"assay_type": "QPCR_EXPRESSION"})

    assert "x-api-key" not in seen_headers


async def test_get_cro_match_passes_through_criteria(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content) == {
            "assay_type": "QPCR_EXPRESSION",
            "criteria": {"region": "US"},
        }
        return httpx.Response(200, json={"matches": [], "count": 0})

    _install_transport(monkeypatch, handler)

    await call_tool(
        "litmus_get_cro_match",
        {"assay_type": "QPCR_EXPRESSION", "criteria": {"region": "US"}},
    )


# ── litmus_calculate_estimate ───────────────────────────────────────────────


async def test_calculate_estimate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LITMUS_API_KEY", "lk_test123")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/estimate"
        assert request.headers["x-api-key"] == "lk_test123"
        return httpx.Response(200, json={
            "estimated_cost_usd": {"low": 200, "high": 400},
            "estimated_turnaround_days": {"low": 5, "high": 10},
            "cost_breakdown": {
                "materials": 100, "labor": 200, "equipment": 50,
                "platform_fee": 20, "privacy_premium": 0,
            },
            "operator_availability": "high",
        })

    _install_transport(monkeypatch, handler)

    result = await call_tool(
        "litmus_calculate_estimate",
        {"intake": {"experiment_type": "CELL_VIABILITY_IC50"}},
    )

    body = _body(result)
    assert body["operator_availability"] == "high"
    assert body["estimated_cost_usd"] == {"low": 200, "high": 400}


async def test_calculate_estimate_missing_experiment_type_short_circuits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LITMUS_API_KEY", "lk_test123")

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should have been made")

    _install_transport(monkeypatch, handler)

    result = await call_tool("litmus_calculate_estimate", {"intake": {}})

    assert _body(result) == {
        "error": "intake.experiment_type is required",
        "error_type": "invalid_input",
    }


async def test_calculate_estimate_backend_422_passes_through(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LITMUS_API_KEY", "lk_test123")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": [{"msg": "invalid experiment_type"}]})

    _install_transport(monkeypatch, handler)

    result = await call_tool(
        "litmus_calculate_estimate",
        {"intake": {"experiment_type": "NOT_A_REAL_TYPE"}},
    )

    body = _body(result)
    assert body["error_type"] == "backend_error"
    assert body["status_code"] == 422


async def test_calculate_estimate_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LITMUS_API_KEY", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should have been made")

    _install_transport(monkeypatch, handler)

    result = await call_tool(
        "litmus_calculate_estimate",
        {"intake": {"experiment_type": "CELL_VIABILITY_IC50"}},
    )

    assert _body(result)["error_type"] == "missing_api_key"


# ── litmus_create_order ─────────────────────────────────────────────────────


async def test_create_order_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LITMUS_API_KEY", "lk_test123")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/order-requests"
        assert request.headers["x-api-key"] == "lk_test123"
        assert json.loads(request.content) == {"raw_payload": {"experiment_type": "QPCR_EXPRESSION"}}
        return httpx.Response(201, json={
            "id": "order-1",
            "submitter_name": "Ada",
            "submitter_email": "ada@example.com",
            "submitted_by_user_id": "user-1",
            "status": "received",
            "raw_payload": {"experiment_type": "QPCR_EXPRESSION"},
            "pdf_key": None,
            "pdf_url": None,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        })

    _install_transport(monkeypatch, handler)

    result = await call_tool(
        "litmus_create_order",
        {"raw_payload": {"experiment_type": "QPCR_EXPRESSION"}},
    )

    body = _body(result)
    assert body["id"] == "order-1"
    assert body["status"] == "received"


async def test_create_order_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LITMUS_API_KEY", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no request should have been made")

    _install_transport(monkeypatch, handler)

    result = await call_tool(
        "litmus_create_order", {"raw_payload": {"experiment_type": "QPCR_EXPRESSION"}}
    )

    assert _body(result)["error_type"] == "missing_api_key"
