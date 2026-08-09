"""HTTP client for the real litmus-project backend.

Every other tool in this server operates on local JSON files, an in-memory
router, or mock dicts. The three `litmus_*` tools are the exception: they call
the actual backend over HTTP, so this module exists to hold that one seam.

Auth is via `X-API-Key` (the backend's `Depends(get_current_user)` accepts
either a Bearer JWT or this header — see backend/auth.py in litmus-project).
Keys are minted once at `POST /auth/register` and never re-exposed afterward,
so the caller is expected to obtain one out-of-band and set it as
LITMUS_API_KEY when configuring this MCP server.
"""

from __future__ import annotations

import os

import httpx

DEFAULT_API_BASE = "http://localhost:8000"

# Test seam: set to an httpx.MockTransport to fake the backend without a real
# server. None in production, which is a no-op for httpx.AsyncClient (falls
# back to the real network transport).
_transport_override: httpx.BaseTransport | None = None


async def call_backend(
    method: str,
    path: str,
    *,
    json_body: dict | None = None,
    require_api_key: bool = False,
) -> dict:
    """Call the litmus-project backend and return its parsed JSON response.

    Never raises for expected failure modes (missing key, connection error,
    non-2xx) — returns a tagged {"error": ..., "error_type": ...} dict instead,
    so callers (the `handle_*` tool functions) can just json.dumps() the
    result either way, mirroring this server's existing convention of
    surfacing failures as JSON payloads rather than exceptions.
    """
    base = os.environ.get("LITMUS_API_BASE", DEFAULT_API_BASE)
    api_key = os.environ.get("LITMUS_API_KEY")

    if require_api_key and not api_key:
        return {
            "error": "LITMUS_API_KEY is not configured",
            "error_type": "missing_api_key",
            "hint": (
                "Set the LITMUS_API_KEY environment variable to a key obtained "
                "from POST /auth/register on your litmus-project backend, then "
                "restart the MCP server."
            ),
        }

    headers = {}
    if require_api_key and api_key:
        headers["X-API-Key"] = api_key

    try:
        async with httpx.AsyncClient(
            base_url=base, transport=_transport_override, timeout=30.0
        ) as client:
            response = await client.request(method, path, json=json_body, headers=headers)
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        return {
            "error": f"Could not reach litmus backend at {base}: {exc}",
            "error_type": "connection_error",
        }

    if response.status_code >= 300:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        return {
            "error": f"Backend returned {response.status_code}",
            "error_type": "backend_error",
            "status_code": response.status_code,
            "backend_detail": detail,
        }

    return response.json()
