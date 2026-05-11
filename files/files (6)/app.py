"""
app.py — FastAPI application for the Multi-Agent Task Automation System
"""
import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import data, transform, files, scheduler, ai, pipeline

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("app")

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🤖 Multi-Agent API starting up...")
    yield
    logger.info("Multi-Agent API shutting down.")


app = FastAPI(
    title="Multi-Agent Task Automation API",
    description="""
A FastAPI application exposing every agent operation as a REST endpoint.

## Agents

| Agent | Base path | Operations |
|---|---|---|
| **DataAgent** | `/data` | analyze, filter, sort, aggregate, summarize, validate |
| **TransformAgent** | `/transform` | json-to-csv, csv-to-json, flatten, encode, template, extract |
| **FileAgent** | `/files` | write, read, list, delete, checksum, search |
| **SchedulerAgent** | `/scheduler` | schedule, chain, queue |
| **AIAgent** | `/ai` | reason, summarize, extract, classify, code-gen, generate, plan, critique |
| **AutoOrchestrator** | `/pipeline` | solve (AI-generated pipeline), agents |

## Quick start

1. Set `ANTHROPIC_API_KEY` to use AI endpoints
2. Hit `POST /pipeline/solve` with a plain-English requirement
3. The AI designs and executes the full pipeline automatically
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(data.router)
app.include_router(transform.router)
app.include_router(files.router)
app.include_router(scheduler.router)
app.include_router(ai.router)
app.include_router(pipeline.router)


# ── Health & root ──────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "Multi-Agent Task Automation API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "data":      ["/data/analyze", "/data/filter", "/data/sort", "/data/aggregate", "/data/summarize", "/data/validate"],
            "transform": ["/transform/json-to-csv", "/transform/csv-to-json", "/transform/flatten", "/transform/encode", "/transform/template", "/transform/extract"],
            "files":     ["/files/write", "/files/read/{filename}", "/files/list", "/files/delete/{filename}", "/files/checksum/{filename}", "/files/search"],
            "scheduler": ["/scheduler/schedule", "/scheduler/chain", "/scheduler/queue"],
            "ai":        ["/ai/reason", "/ai/summarize", "/ai/extract", "/ai/classify", "/ai/code-gen", "/ai/generate", "/ai/plan", "/ai/critique"],
            "pipeline":  ["/pipeline/solve", "/pipeline/agents"],
        },
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "api_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
    }
