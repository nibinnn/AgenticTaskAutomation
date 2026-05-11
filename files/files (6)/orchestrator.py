"""
Orchestrator - Routes tasks to the appropriate agent and manages the pipeline.
Now includes AIAgent for intelligent task automation.
"""
import time
import logging
from typing import Optional
from agents.base_agent import BaseAgent, TaskResult, AgentStatus
from agents.specialized_agents import DataAgent, FileAgent, TransformAgent, SchedulerAgent
from agents.ai_agent import AIAgent

logger = logging.getLogger("Orchestrator")


class Orchestrator:
    def __init__(self, api_key: str = ""):
        self.agents: dict[str, BaseAgent] = {}
        self.pipeline_results: list[dict] = []
        self._register_defaults(api_key)

    def _register_defaults(self, api_key: str = ""):
        for agent in [DataAgent(), FileAgent(), TransformAgent(), SchedulerAgent()]:
            self.register(agent)
        self.register(AIAgent(api_key=api_key))

    def register(self, agent: BaseAgent):
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    def route(self, task: dict) -> Optional[BaseAgent]:
        task_type = task.get("task_type", "")
        if "agent" in task and task["agent"] in self.agents:
            return self.agents[task["agent"]]
        for agent in self.agents.values():
            if agent.can_handle(task_type):
                return agent
        return None

    def run_task(self, task: dict) -> TaskResult:
        agent = self.route(task)
        if not agent:
            return TaskResult(success=False, output=None,
                              error=f"No agent found for task_type='{task.get('task_type')}'")
        logger.info(f"Routing '{task.get('name', '?')}' → {agent.name}")
        return agent.run(task)

    def run_pipeline(self, tasks: list[dict], stop_on_failure: bool = False) -> list[dict]:
        results = []
        previous_output = None
        for i, task in enumerate(tasks):
            if task.get("inject_output") and previous_output is not None:
                if task.get("operation") == "write":
                    task["content"] = previous_output if isinstance(previous_output, str) else str(previous_output)
                else:
                    task["data"] = previous_output
            result = self.run_task(task)
            previous_output = result.output
            routed = self.route(task)
            entry = {
                "step": i + 1, "name": task.get("name", f"Step {i+1}"),
                "agent": routed.name if routed else "none",
                "success": result.success, "output": result.output,
                "error": result.error, "duration": result.duration,
            }
            results.append(entry)
            self.pipeline_results.append(entry)
            if stop_on_failure and not result.success:
                break
        return results

    def ai_task(self, task_type: str, **kwargs) -> TaskResult:
        """Shortcut: orc.ai_task('summarize', text='...')"""
        return self.run_task({"task_type": task_type, "agent": "AIAgent", "name": task_type, **kwargs})

    def status_report(self) -> dict:
        return {
            "agents": {
                name: {"status": agent.status.value, "description": agent.description, **agent.stats}
                for name, agent in self.agents.items()
            },
            "total_pipeline_steps": len(self.pipeline_results),
        }
