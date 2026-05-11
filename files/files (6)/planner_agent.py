"""
PlannerAgent — The brain of the system.

Given a natural language requirement, it:
  1. Reasons about what needs to be done
  2. Designs a pipeline of tasks as structured JSON
  3. Returns that pipeline for the Orchestrator to execute

The planner knows about every available agent and their capabilities,
so it can compose multi-step workflows automatically.
"""
import json
import re
import os
import urllib.request
from typing import Optional, Any
from agents.base_agent import BaseAgent, TaskResult


# ── Agent capability manifest ─────────────────────────────────────────────────
# This is what the planner "knows" about the system.
# When you add a new agent, add it here too.

AGENT_MANIFEST = {
    "DataAgent": {
        "description": "Analyzes, filters, sorts, aggregates, validates, and summarizes structured JSON data (arrays of objects).",
        "operations": {
            "analyze":   "Compute min/max/mean/count for numeric fields. Input: data (list). Output: {record_count, field_stats}",
            "filter":    "Filter rows by a condition. Input: data, condition={field, op (eq/gt/lt/contains), value}. Output: filtered list",
            "sort":      "Sort rows by a field. Input: data, key (field name), reverse (bool). Output: sorted list",
            "aggregate": "Group and count rows by a field. Input: data, group_by (field name). Output: {group: count}",
            "summarize": "Quick summary of data shape. Input: data. Output: {total, fields, sample}",
            "validate":  "Validate data against a schema. Input: data, schema={field: {required, type}}. Output: {valid, errors}",
        },
        "task_types": ["analyze", "filter", "sort", "aggregate", "summarize", "validate"],
    },
    "TransformAgent": {
        "description": "Converts data between formats and transforms text.",
        "operations": {
            "json_to_csv": "Convert JSON array to CSV string. Input: data (list of dicts). Output: CSV string",
            "csv_to_json": "Convert CSV string to JSON array. Input: csv_text. Output: list of dicts",
            "flatten":     "Flatten a nested dict. Input: data (dict). Output: flat dict with dot-separated keys",
            "encode":      "Encode text. Input: text, method (base64/hex/url). Output: {original, encoded, method}",
            "template":    "Render a template with variables. Input: template (str with {{var}} placeholders), variables (dict). Output: rendered string",
            "extract":     "Extract regex matches from text. Input: text, pattern (regex). Output: list of matches",
        },
        "task_types": ["json_to_csv", "csv_to_json", "flatten", "encode", "template", "extract"],
    },
    "FileAgent": {
        "description": "Reads and writes files on disk.",
        "operations": {
            "write":    "Write content to a file. Input: filename, content (str). Output: {path, bytes, written}",
            "read":     "Read a file. Input: filename. Output: {filename, content, lines}",
            "list":     "List files. Input: pattern (glob, e.g. '*.csv'). Output: list of {name, size, is_dir}",
            "delete":   "Delete a file. Input: filename. Output: {deleted}",
            "checksum": "Get MD5+SHA256 of a file. Input: filename. Output: {md5, sha256}",
            "search":   "Search files by name pattern. Input: pattern. Output: list of matching paths",
        },
        "task_types": ["write", "read", "list", "delete", "checksum", "search"],
    },
    "SchedulerAgent": {
        "description": "Manages task scheduling and queuing.",
        "operations": {
            "schedule": "Queue a task for later. Input: priority (1-10), delay_seconds. Output: {queued, queue_length}",
            "chain":    "Define a dependency chain. Input: steps (list). Output: {steps, estimated_duration}",
        },
        "task_types": ["schedule", "chain"],
    },
    "AIAgent": {
        "description": "Uses Claude LLM for intelligent reasoning, generation, and analysis.",
        "operations": {
            "reason":    "Multi-step reasoning, Q&A. Input: question. Output: text answer",
            "summarize": "Summarize text. Input: text, depth (brief/detailed). Output: summary string",
            "extract":   "Extract structured entities from text. Input: text, fields (list). Output: JSON dict",
            "classify":  "Classify text. Input: text, categories (list). Output: {category, confidence}",
            "code_gen":  "Generate code. Input: description, language. Output: code string",
            "generate":  "Write content. Input: topic, style, length. Output: written text",
            "plan":      "Break a goal into steps. Input: goal, constraints. Output: numbered plan",
            "critique":  "Review content. Input: content, aspect. Output: feedback text",
        },
        "task_types": ["reason", "summarize", "extract", "classify", "code_gen", "generate", "plan", "critique"],
    },
}

SYSTEM_PROMPT = f"""You are a workflow planning AI for a multi-agent automation system.
Your job is to read a user's requirement and design the optimal pipeline of tasks to fulfill it.

## Available Agents and Their Capabilities

{json.dumps(AGENT_MANIFEST, indent=2)}

## Your Output Format

You MUST return a JSON object with this exact structure:
{{
  "goal_summary": "One sentence describing what this pipeline achieves",
  "reasoning": "2-3 sentences explaining why you chose these steps",
  "pipeline": [
    {{
      "step": 1,
      "name": "Short descriptive name",
      "agent": "AgentName",
      "task_type": "operation_name",
      "operation": "operation_name",
      "description": "What this step does",
      ... (other fields the agent needs, e.g. data, filename, condition, etc.)
    }},
    ...
  ]
}}

## Rules for Pipeline Design

1. Each step must use an agent and operation from the manifest above.
2. If a step's output feeds into the next step, add "inject_output": true on the RECEIVING step.
   - For FileAgent write steps receiving content, the content will be auto-injected.
   - For other steps receiving data, the data field will be auto-injected.
3. Use AIAgent for any step that needs intelligence: interpretation, summarization, classification, etc.
4. Use DataAgent for any step operating on structured JSON arrays.
5. Use TransformAgent to change data format (JSON→CSV, flatten, encode, render templates).
6. Use FileAgent to persist results.
7. For AIAgent steps, set max_tokens appropriately (200-500 for short answers, 1000+ for detailed).
8. If user provides data inline, embed it in the relevant step as the "data" field.
9. Keep pipelines focused. Prefer 3-6 steps. Only add steps that genuinely help.
10. Return ONLY the JSON object. No preamble, no markdown fences, no explanation outside the JSON.
"""


class PlannerAgent(BaseAgent):
    """
    Converts a natural language requirement into an executable pipeline.

    Usage:
        planner = PlannerAgent(api_key="sk-ant-...")
        result = planner.run({"requirement": "Analyze this sales data and write a summary report"})
        pipeline = result.output["pipeline"]   # ready to pass to Orchestrator.run_pipeline()
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: Optional[str] = None):
        super().__init__("PlannerAgent", "Converts natural language requirements into executable agent pipelines")
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    def can_handle(self, task_type: str) -> bool:
        return task_type in {"plan_pipeline", "auto"}

    def execute(self, task: dict) -> Any:
        requirement = task.get("requirement", task.get("prompt", ""))
        context = task.get("context", {})          # optional: any data/context to embed
        if not requirement:
            raise ValueError("PlannerAgent requires a 'requirement' field.")
        return self._plan(requirement, context)

    def _plan(self, requirement: str, context: dict) -> dict:
        """Call Claude to produce the pipeline JSON."""
        user_msg = f"Requirement: {requirement}"
        if context:
            user_msg += f"\n\nAvailable context/data:\n{json.dumps(context, indent=2)}"

        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_msg}],
        }

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())

        texts = [b["text"] for b in body.get("content", []) if b.get("type") == "text"]
        raw = "\n".join(texts).strip()

        # Strip markdown fences if model wraps in them
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()

        try:
            plan = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"PlannerAgent returned invalid JSON: {e}\n\nRaw output:\n{raw}")

        # Validate minimal structure
        if "pipeline" not in plan:
            raise ValueError(f"PlannerAgent output missing 'pipeline' key.\n\nGot: {raw}")

        return plan
