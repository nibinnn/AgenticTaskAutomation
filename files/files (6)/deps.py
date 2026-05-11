"""
deps.py — Shared FastAPI dependencies.
Provides singleton agent instances injected via Depends().
"""
import os
from functools import lru_cache
from agents.specialized_agents import DataAgent, FileAgent, TransformAgent, SchedulerAgent
from agents.ai_agent import AIAgent
from agents.planner_agent import PlannerAgent
from auto_orchestrator import AutoOrchestrator


@lru_cache(maxsize=1)
def get_data_agent() -> DataAgent:
    return DataAgent()


@lru_cache(maxsize=1)
def get_file_agent() -> FileAgent:
    return FileAgent(base_dir=os.environ.get("WORKSPACE", "/tmp/agent_workspace"))


@lru_cache(maxsize=1)
def get_transform_agent() -> TransformAgent:
    return TransformAgent()


@lru_cache(maxsize=1)
def get_scheduler_agent() -> SchedulerAgent:
    return SchedulerAgent()


@lru_cache(maxsize=1)
def get_ai_agent() -> AIAgent:
    return AIAgent(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


@lru_cache(maxsize=1)
def get_auto_orchestrator() -> AutoOrchestrator:
    return AutoOrchestrator(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
