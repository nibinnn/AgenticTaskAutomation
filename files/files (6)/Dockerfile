# ── Stage 1: base ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

LABEL maintainer="agent-project"
LABEL description="Multi-Agent Task Automation System — FastAPI + Claude AI"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    WORKSPACE=/tmp/agent_workspace

RUN mkdir -p ${WORKSPACE}
WORKDIR /app

# ── Stage 2: dependencies ──────────────────────────────────────────────────────
FROM base AS deps

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 3: final image ───────────────────────────────────────────────────────
FROM deps AS final

# Copy application source
COPY agents/           ./agents/
COPY api/              ./api/
COPY app.py \
     orchestrator.py \
     auto_orchestrator.py \
     main.py \
     main_auto.py \
     entrypoint.sh ./

RUN chmod +x entrypoint.sh

# Non-root user for security
RUN useradd --create-home --shell /bin/bash agent && \
    chown -R agent:agent /app ${WORKSPACE}
USER agent

ENV ANTHROPIC_API_KEY=""
ENV LOG_LEVEL=INFO
ENV RUN_MODE=api
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV API_WORKERS=1

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
