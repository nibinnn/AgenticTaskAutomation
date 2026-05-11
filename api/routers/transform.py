"""
routers/transform.py — TransformAgent endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (
    JsonToCsvRequest, CsvToJsonRequest, FlattenRequest,
    EncodeRequest, TemplateRequest, RegexExtractRequest,
    TaskResponse,
)
from api.deps import get_transform_agent
from agents.specialized_agents import TransformAgent

router = APIRouter(prefix="/transform", tags=["TransformAgent"])


def _run(agent: TransformAgent, task: dict) -> TaskResponse:
    result = agent.run(task)
    if not result.success:
        raise HTTPException(status_code=422, detail=result.error)
    return TaskResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        duration=result.duration,
        agent="TransformAgent",
    )


@router.post(
    "/json-to-csv",
    response_model=TaskResponse,
    summary="JSON array → CSV string",
    description="Convert a JSON array of objects into a CSV formatted string.",
)
def json_to_csv(req: JsonToCsvRequest, agent: TransformAgent = Depends(get_transform_agent)):
    return _run(agent, {"name": "json_to_csv", "task_type": "json_to_csv", "operation": "json_to_csv", "data": req.data})


@router.post(
    "/csv-to-json",
    response_model=TaskResponse,
    summary="CSV string → JSON array",
    description="Parse a CSV string and convert it into a JSON array of objects.",
)
def csv_to_json(req: CsvToJsonRequest, agent: TransformAgent = Depends(get_transform_agent)):
    return _run(agent, {"name": "csv_to_json", "task_type": "csv_to_json", "operation": "csv_to_json", "csv_text": req.csv_text})


@router.post(
    "/flatten",
    response_model=TaskResponse,
    summary="Flatten nested object",
    description="Flatten a deeply nested JSON object into a single-level dict with dot-separated keys.",
)
def flatten(req: FlattenRequest, agent: TransformAgent = Depends(get_transform_agent)):
    return _run(agent, {"name": "flatten", "task_type": "flatten", "operation": "flatten", "data": req.data, "separator": req.separator})


@router.post(
    "/encode",
    response_model=TaskResponse,
    summary="Encode text",
    description="Encode a text string using base64, hex, or URL encoding.",
)
def encode(req: EncodeRequest, agent: TransformAgent = Depends(get_transform_agent)):
    return _run(agent, {"name": "encode", "task_type": "encode", "operation": "encode", "text": req.text, "method": req.method})


@router.post(
    "/template",
    response_model=TaskResponse,
    summary="Render template",
    description="Render a template string by substituting {{variable}} placeholders with provided values.",
)
def template(req: TemplateRequest, agent: TransformAgent = Depends(get_transform_agent)):
    return _run(agent, {"name": "template", "task_type": "template", "operation": "template", "template": req.template, "variables": req.variables})


@router.post(
    "/extract",
    response_model=TaskResponse,
    summary="Regex extract",
    description="Find all regex pattern matches within a text string.",
)
def extract(req: RegexExtractRequest, agent: TransformAgent = Depends(get_transform_agent)):
    return _run(agent, {"name": "extract", "task_type": "extract", "operation": "extract", "text": req.text, "pattern": req.pattern})
