"""
schemas.py — Pydantic request/response models for all API endpoints.
"""
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


# ── Shared ─────────────────────────────────────────────────────────────────────

class TaskResponse(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None
    duration: float
    agent: str


# ── DataAgent ──────────────────────────────────────────────────────────────────

class FilterCondition(BaseModel):
    field: str
    op: Literal["eq", "gt", "lt", "contains"]
    value: Union[str, int, float]


class SchemaRule(BaseModel):
    required: bool = False
    type: Optional[str] = None


class DataAnalyzeRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Array of JSON objects to analyze")

class DataFilterRequest(BaseModel):
    data: List[Dict[str, Any]]
    condition: FilterCondition

class DataSortRequest(BaseModel):
    data: List[Dict[str, Any]]
    key: str = Field(..., description="Field name to sort by")
    reverse: bool = False

class DataAggregateRequest(BaseModel):
    data: List[Dict[str, Any]]
    group_by: str = Field(..., description="Field name to group by")

class DataSummarizeRequest(BaseModel):
    data: List[Dict[str, Any]]

class DataValidateRequest(BaseModel):
    data: List[Dict[str, Any]]
    schema: Dict[str, SchemaRule] = Field(..., description="Schema rules per field")


# ── TransformAgent ─────────────────────────────────────────────────────────────

class JsonToCsvRequest(BaseModel):
    data: List[Dict[str, Any]]

class CsvToJsonRequest(BaseModel):
    csv_text: str

class FlattenRequest(BaseModel):
    data: Dict[str, Any]
    separator: str = "."

class EncodeRequest(BaseModel):
    text: str
    method: Literal["base64", "hex", "url"] = "base64"

class TemplateRequest(BaseModel):
    template: str = Field(..., description="Template string with {{variable}} placeholders")
    variables: Dict[str, str] = Field(default_factory=dict)

class RegexExtractRequest(BaseModel):
    text: str
    pattern: str = Field(..., description="Regex pattern to match")


# ── FileAgent ──────────────────────────────────────────────────────────────────

class FileWriteRequest(BaseModel):
    filename: str
    content: str

class FileReadRequest(BaseModel):
    filename: str

class FileDeleteRequest(BaseModel):
    filename: str

class FileListRequest(BaseModel):
    pattern: str = "*"

class FileChecksumRequest(BaseModel):
    filename: str

class FileSearchRequest(BaseModel):
    pattern: str


# ── SchedulerAgent ─────────────────────────────────────────────────────────────

class ScheduleRequest(BaseModel):
    task_name: str
    priority: int = Field(default=5, ge=1, le=10)
    delay_seconds: int = Field(default=0, ge=0)

class ChainStep(BaseModel):
    name: str
    timeout: int = 5

class ChainRequest(BaseModel):
    steps: List[ChainStep]


# ── AIAgent ────────────────────────────────────────────────────────────────────

class AIReasonRequest(BaseModel):
    question: str
    max_tokens: int = Field(default=1024, ge=100, le=4096)

class AISummarizeRequest(BaseModel):
    text: str
    depth: Literal["brief", "detailed"] = "brief"
    max_tokens: int = 512

class AIExtractRequest(BaseModel):
    text: str
    fields: List[str] = Field(default_factory=list, description="Fields to extract")
    max_tokens: int = 512

class AIClassifyRequest(BaseModel):
    text: str
    categories: List[str] = Field(..., description="List of categories to classify into")
    max_tokens: int = 256

class AICodeGenRequest(BaseModel):
    description: str
    language: str = "python"
    context: str = ""
    max_tokens: int = 2048

class AIGenerateRequest(BaseModel):
    topic: str
    style: str = "professional"
    length: Literal["short", "medium", "long"] = "medium"
    max_tokens: int = 1024

class AIPlanRequest(BaseModel):
    goal: str
    constraints: str = ""
    max_tokens: int = 1024

class AICritiqueRequest(BaseModel):
    content: str
    aspect: str = "quality, clarity, and correctness"
    max_tokens: int = 1024


# ── PlannerAgent / AutoOrchestrator ───────────────────────────────────────────

class SolveRequest(BaseModel):
    requirement: str = Field(..., description="Plain-English description of what you want done")
    context: Dict[str, Any] = Field(default_factory=dict, description="Optional data context (e.g. {'data': [...]}) ")


class PipelineStep(BaseModel):
    step: int
    name: str
    agent: str
    task_type: str
    description: str
    success: bool
    output: Any
    error: Optional[str]
    duration: float


class SolveResponse(BaseModel):
    success: bool
    goal_summary: str
    reasoning: str
    pipeline: List[Dict[str, Any]]
    execution: List[PipelineStep]
    final_output: Any
    duration: float
