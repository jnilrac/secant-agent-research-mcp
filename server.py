from __future__ import annotations

import os
from typing import Annotated, Any

import httpx
from fastmcp import FastMCP
from pydantic import Field


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
    query: Annotated[str, Field(description="Natural language web search query to run for the agent.")],
    max_results: Annotated[int, Field(ge=1, le=10, description="Maximum number of ranked search results to return.")] = 5,
    payment: Annotated[dict[str, Any] | None, Field(description="Optional x402 payment proof returned by the buyer after accepting the 402 payment requirement.")] = None,
    payment_identifier: Annotated[str | None, Field(description="Optional idempotency key/payment identifier used to retry safely without rerunning expensive work.")] = None,
) -> dict[str, Any]:
    """Run ranked web search for autonomous agents.

    Unpaid calls return the upstream HTTP 402/x402 payment requirement before
    execution. Paid retries with a valid payment proof return structured search
    results from the live Secant Agent Research API.
    """
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
    query: Annotated[str, Field(description="Research question or search query for the workflow.")],
    max_results: Annotated[int, Field(ge=1, le=10, description="Maximum number of ranked search results to include.")] = 5,
    extract_pages: Annotated[int, Field(ge=0, le=5, description="Number of top-ranked result pages to extract for readable text and citations.")] = 1,
    payment: Annotated[dict[str, Any] | None, Field(description="Optional x402 payment proof returned by the buyer after accepting the 402 payment requirement.")] = None,
    payment_identifier: Annotated[str | None, Field(description="Optional idempotency key/payment identifier used to retry safely without rerunning expensive work.")] = None,
) -> dict[str, Any]:
    """Run the full paid research workflow: search, extraction, JSON, and citations.

    Use this when an agent needs a compact source-backed research packet rather
    than raw search results. Unpaid calls return x402 payment terms; paid retries
    return normalized results and extraction details.
    """
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
    urls: Annotated[list[str], Field(description="One or more absolute page URLs to extract. The live API enforces service limits.")],
    payment: Annotated[dict[str, Any] | None, Field(description="Optional x402 payment proof returned by the buyer after accepting the 402 payment requirement.")] = None,
    payment_identifier: Annotated[str | None, Field(description="Optional idempotency key/payment identifier used to retry safely without rerunning expensive work.")] = None,
) -> dict[str, Any]:
    """Extract readable content, metadata, links, and hashes from page URLs.

    Use this when the caller already knows which pages matter and only needs
    cleaned extraction output. Blocked or failed pages are returned as extraction
    errors by the upstream API.
    """
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
    url: Annotated[str, Field(description="Absolute page URL to fetch and compare against prior state.")],
    previous_hash: Annotated[str | None, Field(description="Optional previous content hash from an earlier extract or diff check.")] = None,
    previous_text: Annotated[str | None, Field(description="Optional previous readable text to compare with the current page text.")] = None,
    payment: Annotated[dict[str, Any] | None, Field(description="Optional x402 payment proof returned by the buyer after accepting the 402 payment requirement.")] = None,
    payment_identifier: Annotated[str | None, Field(description="Optional idempotency key/payment identifier used to retry safely without rerunning expensive work.")] = None,
) -> dict[str, Any]:
    """Check whether a page changed since a previous hash or text snapshot.

    Use this for lightweight monitoring of docs, pricing pages, competitor
    pages, status pages, or other URLs an agent revisits. Unpaid calls return
    x402 payment terms before execution.
    """
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
