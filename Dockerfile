FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SECANT_AGENT_RESEARCH_API_BASE_URL=https://agentic.secantoutreach.com

WORKDIR /app

COPY pyproject.toml README.md server.py ./
RUN pip install --no-cache-dir .

CMD ["secant-agent-research-mcp"]
