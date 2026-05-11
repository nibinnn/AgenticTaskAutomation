"""
routers/scheduler.py — SchedulerAgent endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ScheduleRequest, ChainRequest, TaskResponse
from api.deps import get_scheduler_agent
from agents.specialized_agents import SchedulerAgent

router = APIRouter(prefix="/scheduler", tags=["SchedulerAgent"])


def _run(agent: SchedulerAgent, task: dict) -> TaskResponse:
    result = agent.run(task)
    if not result.success:
        raise HTTPException(status_code=422, detail=result.error)
    return TaskResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        duration=result.duration,
        agent="SchedulerAgent",
    )


@router.post(
    "/schedule",
    response_model=TaskResponse,
    summary="Schedule a task",
    description="Queue a named task with a priority (1-10) and optional delay in seconds.",
)
def schedule(req: ScheduleRequest, agent: SchedulerAgent = Depends(get_scheduler_agent)):
    return _run(agent, {
        "name": "schedule", "task_type": "schedule", "operation": "schedule",
        "task_name": req.task_name,
        "priority": req.priority,
        "delay_seconds": req.delay_seconds,
    })


@router.post(
    "/chain",
    response_model=TaskResponse,
    summary="Chain task steps",
    description="Define a dependency chain of steps and get an estimated total duration.",
)
def chain(req: ChainRequest, agent: SchedulerAgent = Depends(get_scheduler_agent)):
    return _run(agent, {
        "name": "chain", "task_type": "chain", "operation": "chain",
        "steps": [s.model_dump() for s in req.steps],
    })


@router.get(
    "/queue",
    response_model=TaskResponse,
    summary="View scheduler queue",
    description="Return the current list of queued tasks ordered by priority.",
)
def view_queue(agent: SchedulerAgent = Depends(get_scheduler_agent)):
    queue_snapshot = [
        {"task_name": t.get("task_name", "?"), "priority": t.get("priority", 5), "scheduled_at": t.get("scheduled_at", 0)}
        for t in agent.queue
    ]
    return TaskResponse(success=True, output={"queue": queue_snapshot, "length": len(queue_snapshot)}, duration=0.0, agent="SchedulerAgent")
