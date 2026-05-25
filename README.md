# Secant Agent Research MCP

[![smithery badge](https://smithery.ai/badge/hello-j2mo/secant-agent-research-pack)](https://smithery.ai/servers/hello-j2mo/secant-agent-research-pack)

MCP wrapper for the [Secant Agent Research Pack](https://agentic.secantoutreach.com/agent-research), a paid x402 research API for autonomous agents.

The server exposes tools for:

- `search`: ranked web search.
- `research_pack`: search, selected page extraction, normalized JSON, and citations.
- `extract_page`: readable page text and metadata extraction.
- `monitor_diff`: page change checks.

The native paid API uses HTTP `402` and Base USDC over x402. If you call a tool without a payment proof, the tool returns the upstream payment requirement so an agent can pay and retry. If you include a valid payment proof, the tool forwards it to the live API.

## Run

```bash
docker build -t secant-agent-research-mcp .
docker run --rm -i secant-agent-research-mcp
```

## Environment

| Variable | Default | Description |
| --- | --- | --- |
| `SECANT_AGENT_RESEARCH_API_BASE_URL` | `https://agentic.secantoutreach.com` | Base URL for the live Secant Agent Research API. |

## Canonical Discovery

- Buyer page: <https://agentic.secantoutreach.com/agent-research>
- Smithery listing: <https://smithery.ai/servers/hello-j2mo/secant-agent-research-pack>
- x402 manifest: <https://agentic.secantoutreach.com/.well-known/x402.json>
- OpenAPI: <https://agentic.secantoutreach.com/openapi.yaml>
- Agent card: <https://agentic.secantoutreach.com/agent-card.json>
