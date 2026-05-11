"""
routers/files.py — FileAgent endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (
    FileWriteRequest, FileReadRequest, FileDeleteRequest,
    FileListRequest, FileChecksumRequest, FileSearchRequest,
    TaskResponse,
)
from api.deps import get_file_agent
from agents.specialized_agents import FileAgent

router = APIRouter(prefix="/files", tags=["FileAgent"])


def _run(agent: FileAgent, task: dict) -> TaskResponse:
    result = agent.run(task)
    if not result.success:
        raise HTTPException(status_code=422, detail=result.error)
    return TaskResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        duration=result.duration,
        agent="FileAgent",
    )


@router.post(
    "/write",
    response_model=TaskResponse,
    summary="Write a file",
    description="Write text content to a named file in the agent workspace.",
)
def write_file(req: FileWriteRequest, agent: FileAgent = Depends(get_file_agent)):
    return _run(agent, {"name": "write", "task_type": "write", "operation": "write", "filename": req.filename, "content": req.content})


@router.get(
    "/read/{filename:path}",
    response_model=TaskResponse,
    summary="Read a file",
    description="Read the content of a file from the agent workspace by filename.",
)
def read_file(filename: str, agent: FileAgent = Depends(get_file_agent)):
    return _run(agent, {"name": "read", "task_type": "read", "operation": "read", "filename": filename})


@router.get(
    "/list",
    response_model=TaskResponse,
    summary="List files",
    description="List files in the agent workspace, optionally filtered by a glob pattern.",
)
def list_files(pattern: str = "*", agent: FileAgent = Depends(get_file_agent)):
    return _run(agent, {"name": "list", "task_type": "list", "operation": "list", "pattern": pattern})


@router.delete(
    "/delete/{filename:path}",
    response_model=TaskResponse,
    summary="Delete a file",
    description="Delete a file from the agent workspace.",
)
def delete_file(filename: str, agent: FileAgent = Depends(get_file_agent)):
    return _run(agent, {"name": "delete", "task_type": "delete", "operation": "delete", "filename": filename})


@router.get(
    "/checksum/{filename:path}",
    response_model=TaskResponse,
    summary="File checksum",
    description="Compute MD5 and SHA-256 checksums of a file.",
)
def checksum_file(filename: str, agent: FileAgent = Depends(get_file_agent)):
    return _run(agent, {"name": "checksum", "task_type": "checksum", "operation": "checksum", "filename": filename})


@router.get(
    "/search",
    response_model=TaskResponse,
    summary="Search files",
    description="Search for files in the workspace whose names contain the given pattern.",
)
def search_files(pattern: str, agent: FileAgent = Depends(get_file_agent)):
    return _run(agent, {"name": "search", "task_type": "search", "operation": "search", "pattern": pattern})
