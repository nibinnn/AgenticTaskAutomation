"""
Base Agent - Foundation for all specialized agents.
"""
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    WAITING = "waiting"


@dataclass
class TaskResult:
    success: bool
    output: Any
    error: Optional[str] = None
    duration: float = 0.0
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        return f"{status} | Duration: {self.duration:.2f}s | Output: {self.output}"


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(name)
        self.task_history: list[TaskResult] = []

    def run(self, task: dict) -> TaskResult:
        """Execute a task and track its result."""
        self.status = AgentStatus.RUNNING
        start = time.time()
        self.logger.info(f"Starting task: {task.get('name', 'unnamed')}")

        try:
            output = self.execute(task)
            duration = time.time() - start
            result = TaskResult(success=True, output=output, duration=duration)
            self.status = AgentStatus.SUCCESS
            self.logger.info(f"Task completed in {duration:.2f}s")
        except Exception as e:
            duration = time.time() - start
            result = TaskResult(success=False, output=None, error=str(e), duration=duration)
            self.status = AgentStatus.FAILED
            self.logger.error(f"Task failed: {e}")

        self.task_history.append(result)
        return result

    @abstractmethod
    def execute(self, task: dict) -> Any:
        """Subclasses implement this to define task logic."""
        pass

    def can_handle(self, task_type: str) -> bool:
        """Return True if this agent handles the given task type."""
        return False

    @property
    def stats(self) -> dict:
        if not self.task_history:
            return {"total": 0, "success": 0, "failed": 0, "avg_duration": 0}
        successes = [r for r in self.task_history if r.success]
        return {
            "total": len(self.task_history),
            "success": len(successes),
            "failed": len(self.task_history) - len(successes),
            "avg_duration": sum(r.duration for r in self.task_history) / len(self.task_history),
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name}, status={self.status.value})>"
