"""
routers/ai.py — AIAgent endpoints (Claude-powered)
"""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (
    AIReasonRequest, AISummarizeRequest, AIExtractRequest,
    AIClassifyRequest, AICodeGenRequest, AIGenerateRequest,
    AIPlanRequest, AICritiqueRequest, TaskResponse,
)
from api.deps import get_ai_agent
from agents.ai_agent import AIAgent

router = APIRouter(prefix="/ai", tags=["AIAgent"])


def _run(agent: AIAgent, task: dict) -> TaskResponse:
    result = agent.run(task)
    if not result.success:
        raise HTTPException(status_code=422, detail=result.error)
    return TaskResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        duration=result.duration,
        agent="AIAgent",
    )


@router.post(
    "/reason",
    response_model=TaskResponse,
    summary="Multi-step reasoning",
    description="Ask Claude a question and get a step-by-step reasoned answer.",
)
def reason(req: AIReasonRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {"name": "reason", "task_type": "reason", "question": req.question, "max_tokens": req.max_tokens})


@router.post(
    "/summarize",
    response_model=TaskResponse,
    summary="Summarize text",
    description="Condense a document or long text into a brief or detailed summary.",
)
def summarize(req: AISummarizeRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {"name": "summarize", "task_type": "summarize", "text": req.text, "depth": req.depth, "max_tokens": req.max_tokens})


@router.post(
    "/extract",
    response_model=TaskResponse,
    summary="Extract entities",
    description="Extract structured key-value data from unstructured text. Returns JSON.",
)
def extract(req: AIExtractRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {"name": "extract", "task_type": "extract", "text": req.text, "fields": req.fields, "max_tokens": req.max_tokens})


@router.post(
    "/classify",
    response_model=TaskResponse,
    summary="Classify text",
    description="Classify text into one of the provided categories with a confidence score.",
)
def classify(req: AIClassifyRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {"name": "classify", "task_type": "classify", "text": req.text, "categories": req.categories, "max_tokens": req.max_tokens})


@router.post(
    "/code-gen",
    response_model=TaskResponse,
    summary="Generate code",
    description="Generate clean, production-quality code from a plain-English description.",
)
def code_gen(req: AICodeGenRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {
        "name": "code_gen", "task_type": "code_gen",
        "description": req.description, "language": req.language,
        "context": req.context, "max_tokens": req.max_tokens,
    })


@router.post(
    "/generate",
    response_model=TaskResponse,
    summary="Generate content",
    description="Write a professional, engaging piece of content on any topic.",
)
def generate(req: AIGenerateRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {
        "name": "generate", "task_type": "generate",
        "topic": req.topic, "style": req.style, "length": req.length, "max_tokens": req.max_tokens,
    })


@router.post(
    "/plan",
    response_model=TaskResponse,
    summary="Generate action plan",
    description="Break a high-level goal into a clear, numbered, actionable step-by-step plan.",
)
def plan(req: AIPlanRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {"name": "plan", "task_type": "plan", "goal": req.goal, "constraints": req.constraints, "max_tokens": req.max_tokens})


@router.post(
    "/critique",
    response_model=TaskResponse,
    summary="Critique content",
    description="Review text or code and provide specific, actionable improvement feedback.",
)
def critique(req: AICritiqueRequest, agent: AIAgent = Depends(get_ai_agent)):
    return _run(agent, {"name": "critique", "task_type": "critique", "content": req.content, "aspect": req.aspect, "max_tokens": req.max_tokens})
