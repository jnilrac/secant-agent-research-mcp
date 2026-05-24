from __future__ import annotations

import os
from typing import Any

import httpx
from fastmcp import FastMCP


DEFAULT_API_BASE_URL = "https://agentic.secantoutreach.com"
API_BASE_URL = os.getenv("SECANT_AGENT_RESEARCH_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")

mcp = FastMCP(
    "Secant Agent Research Pack",
    instructions=(
        "Paid web research tools for autonomous agents. Calls without payment proof "
        "return the upstream x402 payment requirement. Calls with valid payment proof "
        "return the paid API result."
    ),
)


def _compact(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


async def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{API_BASE_URL}{path}", json=_compact(payload))
    try:
        body: Any = response.json()
    except ValueError:
        body = {"raw": response.text}
    return {
        "ok": response.is_success,
        "status_code": response.status_code,
        "payment_required": response.status_code == 402,
        "api_base_url": API_BASE_URL,
        "path": path,
        "body": body,
    }


@mcp.tool
async def search(
    query: str,
    max_results: int = 5,
    payment: dict[str, Any] | None = None,
    payment_identifier: str | None = None,
) -> dict[str, Any]:
    """Run paid ranked web search, or return x402 payment requirements if unpaid."""
    return await _post(
        "/services/search",
        {
            "query": query,
            "max_results": max_results,
            "payment": payment,
            "payment_identifier": payment_identifier,
        },
    )


@mcp.tool
async def research_pack(
    query: str,
    max_results: int = 5,
    extract_pages: int = 1,
    payment: dict[str, Any] | None = None,
    payment_identifier: str | None = None,
) -> dict[str, Any]:
    """Run paid search plus page extraction and citations, or return x402 payment requirements if unpaid."""
    return await _post(
        "/services/research-pack",
        {
            "query": query,
            "max_results": max_results,
            "extract_pages": extract_pages,
            "payment": payment,
            "payment_identifier": payment_identifier,
        },
    )


@mcp.tool
async def extract_page(
    urls: list[str],
    payment: dict[str, Any] | None = None,
    payment_identifier: str | None = None,
) -> dict[str, Any]:
    """Extract readable text and metadata from paid page URLs, or return x402 payment requirements if unpaid."""
    return await _post(
        "/services/extract",
        {
            "urls": urls,
            "payment": payment,
            "payment_identifier": payment_identifier,
        },
    )


@mcp.tool
async def monitor_diff(
    url: str,
    previous_hash: str | None = None,
    previous_text: str | None = None,
    payment: dict[str, Any] | None = None,
    payment_identifier: str | None = None,
) -> dict[str, Any]:
    """Check a URL for changes against previous text or hash, or return x402 payment requirements if unpaid."""
    return await _post(
        "/services/monitor/diff",
        {
            "url": url,
            "previous_hash": previous_hash,
            "previous_text": previous_text,
            "payment": payment,
            "payment_identifier": payment_identifier,
        },
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
