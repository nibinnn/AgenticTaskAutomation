"""
AutoOrchestrator — Self-assembling pipeline engine.

Given a plain-English requirement, it:
  1. Calls PlannerAgent to design the pipeline
  2. Executes each step with the correct agent
  3. Returns full execution trace + final output

Usage:
    orc = AutoOrchestrator(api_key="sk-ant-...")
    result = orc.solve("Analyze this sales data and save a CSV report", context={"data": [...]})
"""
import json
import time
import logging
from typing import Any, Optional

from agents.base_agent import BaseAgent, TaskResult
from agents.specialized_agents import DataAgent, FileAgent, TransformAgent, SchedulerAgent
from agents.ai_agent import AIAgent
from agents.planner_agent import PlannerAgent

logger = logging.getLogger("AutoOrchestrator")

RESET   = "\033[0m"; BOLD    = "\033[1m"
CYAN    = "\033[96m"; GREEN   = "\033[92m"
RED     = "\033[91m"; YELLOW  = "\033[93m"
BLUE    = "\033[94m"; GREY    = "\033[90m"
MAGENTA = "\033[95m"; WHITE   = "\033[97m"


class AutoOrchestrator:
    """
    The self-assembling orchestrator.
    All you give it is a requirement in plain English (+ optional data context).
    It handles everything else.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.agents: dict[str, BaseAgent] = {}
        self._register_all()
        self.planner = PlannerAgent(api_key=api_key)
        self.execution_log: list[dict] = []

    def _register_all(self):
        for agent in [
            DataAgent(),
            FileAgent(),
            TransformAgent(),
            SchedulerAgent(),
            AIAgent(api_key=self.api_key),
        ]:
            self.agents[agent.name] = agent

    # ── Public API ─────────────────────────────────────────────────────────────

    def solve(self, requirement: str, context: dict = None, verbose: bool = True) -> dict:
        """
        Main entry point. Give it a requirement, get back a full execution report.

        Args:
            requirement: Plain-English description of what you want done.
            context: Optional dict with any data the planner might need (e.g. {"data": [...]}).
            verbose: Print live progress to stdout.

        Returns:
            {
                "goal_summary": str,
                "reasoning": str,
                "pipeline": [...],       # the plan produced by PlannerAgent
                "execution": [...],      # step-by-step execution results
                "final_output": Any,     # output of the last successful step
                "success": bool,
                "duration": float,
            }
        """
        start = time.time()

        if verbose:
            print(f"\n{CYAN}{BOLD}◆ AutoOrchestrator{RESET}")
            print(f"  {GREY}Requirement:{RESET} {requirement}\n")

        # ── Step 1: Plan ───────────────────────────────────────────────────────
        if verbose:
            print(f"  {YELLOW}[1/2] Planning pipeline...{RESET}")

        plan_result = self.planner.run({
            "requirement": requirement,
            "context": context or {},
        })

        if not plan_result.success:
            return self._fail(requirement, plan_result.error, time.time() - start)

        plan = plan_result.output
        pipeline = plan.get("pipeline", [])

        if verbose:
            print(f"  {GREEN}✓{RESET} Plan ready: {BOLD}{plan.get('goal_summary', '')}{RESET}")
            print(f"  {GREY}  Reasoning: {plan.get('reasoning', '')}{RESET}")
            print(f"\n  {YELLOW}[2/2] Executing {len(pipeline)} steps...{RESET}\n")

        # ── Step 2: Execute ────────────────────────────────────────────────────
        execution = []
        previous_output = None

        for step_def in pipeline:
            step_num  = step_def.get("step", len(execution) + 1)
            step_name = step_def.get("name", f"Step {step_num}")
            agent_name = step_def.get("agent", "")
            task_type  = step_def.get("task_type", step_def.get("operation", ""))

            # Inject previous output if step requests it
            if step_def.get("inject_output") and previous_output is not None:
                if step_def.get("operation") == "write":
                    step_def["content"] = (
                        previous_output if isinstance(previous_output, str)
                        else json.dumps(previous_output, indent=2)
                    )
                else:
                    step_def["data"] = previous_output

            # Route to agent
            agent = self.agents.get(agent_name)
            if not agent:
                # Fallback: find any agent that can handle this task_type
                agent = next(
                    (a for a in self.agents.values() if a.can_handle(task_type)), None
                )

            if not agent:
                result = TaskResult(
                    success=False, output=None,
                    error=f"No agent available for agent='{agent_name}', task_type='{task_type}'"
                )
            else:
                # Merge step_def fields into the task dict
                task = {
                    "name": step_name,
                    "task_type": task_type,
                    **step_def,
                }
                result = agent.run(task)

            previous_output = result.output if result.success else previous_output

            step_record = {
                "step": step_num,
                "name": step_name,
                "agent": agent.name if agent else agent_name,
                "task_type": task_type,
                "description": step_def.get("description", ""),
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "duration": result.duration,
            }
            execution.append(step_record)
            self.execution_log.append(step_record)

            if verbose:
                icon  = f"{GREEN}✓{RESET}" if result.success else f"{RED}✗{RESET}"
                aname = agent.name if agent else agent_name
                print(f"  {icon}  Step {step_num:02d}  {BOLD}{step_name:<35}{RESET}"
                      f"  {GREY}[{aname}]  {result.duration:.2f}s{RESET}")
                if not result.success:
                    print(f"      {RED}→ {result.error}{RESET}")

        total = time.time() - start
        success = all(s["success"] for s in execution)

        if verbose:
            passed = sum(1 for s in execution if s["success"])
            color  = GREEN if success else YELLOW
            print(f"\n  {color}{BOLD}{passed}/{len(execution)} steps succeeded  |  total {total:.2f}s{RESET}")

        return {
            "goal_summary": plan.get("goal_summary", ""),
            "reasoning":    plan.get("reasoning", ""),
            "pipeline":     pipeline,
            "execution":    execution,
            "final_output": previous_output,
            "success":      success,
            "duration":     total,
        }

    def _fail(self, requirement: str, error: str, duration: float) -> dict:
        logger.error(f"Planning failed: {error}")
        return {
            "goal_summary": requirement,
            "reasoning":    "",
            "pipeline":     [],
            "execution":    [],
            "final_output": None,
            "success":      False,
            "duration":     duration,
            "error":        error,
        }

    def status(self) -> dict:
        return {
            name: {"status": a.status.value, **a.stats}
            for name, a in self.agents.items()
        }
