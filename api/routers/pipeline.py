"""
routers/pipeline.py — AutoOrchestrator endpoint
One endpoint: POST /pipeline/solve — describe what you want, get a full execution back.
"""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import SolveRequest, SolveResponse, PipelineStep
from api.deps import get_auto_orchestrator
from auto_orchestrator import AutoOrchestrator

router = APIRouter(prefix="/pipeline", tags=["AutoOrchestrator"])


@router.post(
    "/solve",
    response_model=SolveResponse,
    summary="AI-generated pipeline",
    description=(
        "Provide a plain-English requirement and optional data context. "
        "The PlannerAgent (Claude) designs the optimal multi-agent pipeline, "
        "then each step is executed automatically. Returns full execution trace."
    ),
)
def solve(req: SolveRequest, orc: AutoOrchestrator = Depends(get_auto_orchestrator)):
    print(req.requirement)
    print(req.context)
    result = orc.solve(req.requirement, context=req.context, verbose=False)
    if not result.get("pipeline"):
        raise HTTPException(
            status_code=422,
            detail=result.get("error", "PlannerAgent returned an empty pipeline"),
        )

    execution_steps = []
    for step in result.get("execution", []):
        execution_steps.append(PipelineStep(
            step=step.get("step", 0),
            name=step.get("name", ""),
            agent=step.get("agent", ""),
            task_type=step.get("task_type", ""),
            description=step.get("description", ""),
            success=step.get("success", False),
            output=step.get("output"),
            error=step.get("error"),
            duration=step.get("duration", 0.0),
        ))

    return SolveResponse(
        success=result["success"],
        goal_summary=result.get("goal_summary", ""),
        reasoning=result.get("reasoning", ""),
        pipeline=result.get("pipeline", []),
        execution=execution_steps,
        final_output=result.get("final_output"),
        duration=result.get("duration", 0.0),
    )


@router.get(
    "/agents",
    summary="List available agents",
    description="Return metadata about all registered agents and their capabilities.",
)
def list_agents(orc: AutoOrchestrator = Depends(get_auto_orchestrator)):
    return {
        name: {
            "description": agent.description,
            "status": agent.status.value,
            **agent.stats,
        }
        for name, agent in orc.agents.items()
    }
