"""
routers/data.py — DataAgent endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (
    DataAnalyzeRequest, DataFilterRequest, DataSortRequest,
    DataAggregateRequest, DataSummarizeRequest, DataValidateRequest,
    TaskResponse,
)
from api.deps import get_data_agent
from agents.specialized_agents import DataAgent

router = APIRouter(prefix="/data", tags=["DataAgent"])


def _run(agent: DataAgent, task: dict) -> TaskResponse:
    result = agent.run(task)
    if not result.success:
        raise HTTPException(status_code=422, detail=result.error)
    return TaskResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        duration=result.duration,
        agent="DataAgent",
    )


@router.post(
    "/analyze",
    response_model=TaskResponse,
    summary="Analyze dataset",
    description="Compute min, max, mean, and count for all numeric fields in the dataset.",
)
def analyze(req: DataAnalyzeRequest, agent: DataAgent = Depends(get_data_agent)):
    return _run(agent, {"name": "analyze", "task_type": "analyze", "operation": "analyze", "data": req.data})


@router.post(
    "/filter",
    response_model=TaskResponse,
    summary="Filter rows",
    description="Filter rows by a field condition (eq / gt / lt / contains).",
)
def filter_data(req: DataFilterRequest, agent: DataAgent = Depends(get_data_agent)):
    return _run(agent, {
        "name": "filter", "task_type": "filter", "operation": "filter",
        "data": req.data, "condition": req.condition.model_dump(),
    })


@router.post(
    "/sort",
    response_model=TaskResponse,
    summary="Sort rows",
    description="Sort the dataset by a specified field, ascending or descending.",
)
def sort_data(req: DataSortRequest, agent: DataAgent = Depends(get_data_agent)):
    return _run(agent, {
        "name": "sort", "task_type": "sort", "operation": "sort",
        "data": req.data, "key": req.key, "reverse": req.reverse,
    })


@router.post(
    "/aggregate",
    response_model=TaskResponse,
    summary="Aggregate / group by",
    description="Group rows by a field and return per-group counts.",
)
def aggregate(req: DataAggregateRequest, agent: DataAgent = Depends(get_data_agent)):
    return _run(agent, {
        "name": "aggregate", "task_type": "aggregate", "operation": "aggregate",
        "data": req.data, "group_by": req.group_by,
    })


@router.post(
    "/summarize",
    response_model=TaskResponse,
    summary="Summarize dataset",
    description="Return total record count, field names, and a sample of the first 3 rows.",
)
def summarize(req: DataSummarizeRequest, agent: DataAgent = Depends(get_data_agent)):
    return _run(agent, {"name": "summarize", "task_type": "summarize", "operation": "summarize", "data": req.data})


@router.post(
    "/validate",
    response_model=TaskResponse,
    summary="Validate dataset schema",
    description="Check that all rows conform to the given field schema (required fields, types).",
)
def validate(req: DataValidateRequest, agent: DataAgent = Depends(get_data_agent)):
    return _run(agent, {
        "name": "validate", "task_type": "validate", "operation": "validate",
        "data": req.data,
        "schema": {k: v.model_dump() for k, v in req.schema.items()},
    })
