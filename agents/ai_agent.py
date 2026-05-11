"""
AIAgent - Uses the Anthropic Claude API for intelligent task execution.
Supports: reasoning, content generation, data extraction, code generation,
          classification, summarization, and tool-augmented tasks.
"""
import os
import json
import time
import re
from typing import Any, Optional
from agents.base_agent import BaseAgent, TaskResult
from models.llm_connector import LLMConnector


class AIAgent(BaseAgent):
    """
    An agent that delegates tasks to the Claude API.

    Supported task types:
      - reason         : Multi-step reasoning / Q&A
      - generate       : Content / text generation
      - summarize      : Summarize a document or text
      - extract        : Extract structured data from unstructured text
      - classify       : Classify text into categories
      - code_gen       : Generate code from a description
      - critique       : Review and improve text or code
      - plan           : Break a goal into actionable steps
      - tool_use       : Use built-in tools (web_search) alongside reasoning
    """

    SUPPORTED = {
        "reason", "generate", "summarize", "extract",
        "classify", "code_gen", "critique", "plan", "tool_use"
    }

    # def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: Optional[str] = None):
    def __init__(self, model: Optional[str] = None):
        super().__init__("AIAgent", "Delegates tasks to Claude via the Anthropic API")
        self.model = model
        # self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.llm = LLMConnector.get_model(model)()

    def can_handle(self, task_type: str) -> bool:
        return task_type in self.SUPPORTED

    def execute(self, task: dict) -> Any:
        print("reached ai agent", self.model)
        task_type = task.get("task_type", "reason")
        prompt = self._build_prompt(task_type, task)
        system = task.get("system_prompt", self._default_system(task_type))
        tools = task.get("tools")
        if self.model == "claude":
            return self.llm.call_claude(prompt, system, tools, task.get("max_tokens", 1024))
        return self.llm.call_agent(prompt, system, tools, task.get("max_tokens", 1024))
    
    # ── Prompt builders ───────────────────────────────────────────────────────

    def _build_prompt(self, task_type: str, task: dict) -> str:
        if task_type == "reason":
            return task.get("question", task.get("prompt", ""))

        elif task_type == "generate":
            topic = task.get("topic", "")
            style = task.get("style", "professional")
            length = task.get("length", "medium")
            return f"Write a {length}, {style} piece about: {topic}"

        elif task_type == "summarize":
            text = task.get("text", "")
            depth = task.get("depth", "concise")
            return f"Provide a {depth} summary of the following:\n\n{text}"

        elif task_type == "extract":
            text = task.get("text", "")
            fields = task.get("fields", [])
            schema = json.dumps(fields, indent=2) if fields else "all key entities"
            return (
                f"Extract the following fields from the text below and return ONLY valid JSON.\n"
                f"Fields: {schema}\n\nText:\n{text}"
            )

        elif task_type == "classify":
            text = task.get("text", "")
            categories = task.get("categories", [])
            cats = ", ".join(categories) if categories else "auto-detect"
            return (
                f"Classify the following text into one of these categories: {cats}\n"
                f"Return ONLY the category name and a confidence score (0-1) as JSON.\n\nText:\n{text}"
            )

        elif task_type == "code_gen":
            description = task.get("description", "")
            language = task.get("language", "python")
            context = task.get("context", "")
            ctx_part = f"\n\nContext:\n{context}" if context else ""
            return f"Write {language} code for:\n{description}{ctx_part}\n\nReturn only the code, no explanations."

        elif task_type == "critique":
            content = task.get("content", "")
            aspect = task.get("aspect", "quality, clarity, and correctness")
            return (
                f"Critique the following for {aspect}. "
                f"Provide specific, actionable feedback.\n\n{content}"
            )

        elif task_type == "plan":
            goal = task.get("goal", "")
            constraints = task.get("constraints", "")
            con_part = f"\n\nConstraints: {constraints}" if constraints else ""
            return (
                f"Break this goal into a clear, numbered action plan with concrete steps:\n{goal}{con_part}"
            )

        elif task_type == "tool_use":
            return task.get("prompt", "")

        return task.get("prompt", str(task))

    def _default_system(self, task_type: str) -> str:
        systems = {
            "reason":    "You are a precise, logical reasoning assistant. Show your thinking step by step.",
            "generate":  "You are a skilled writer. Produce engaging, well-structured content.",
            "summarize": "You are a concise summarizer. Extract the key points without losing critical meaning.",
            "extract":   "You extract structured data from text. Always return valid JSON only, no prose.",
            "classify":  "You classify text accurately. Return your result as JSON: {\"category\": ..., \"confidence\": ...}",
            "code_gen":  "You are an expert programmer. Write clean, well-commented, production-quality code.",
            "critique":  "You are a thorough reviewer. Be constructive, specific, and prioritize high-impact feedback.",
            "plan":      "You are a strategic planner. Create clear, actionable plans with measurable steps.",
            "tool_use":  "You are a capable assistant with access to tools. Use them when beneficial.",
        }
        return systems.get(task_type, "You are a helpful assistant.")

    # ── API call ──────────────────────────────────────────────────────────────

    def _call_claude(
        self,
        prompt: str,
        system: str,
        tools: Optional[list],
        max_tokens: int,
    ) -> Any:
        import urllib.request

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. "
                "Export it: export ANTHROPIC_API_KEY='sk-ant-...'"
            )

        payload: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if tools:
            payload["tools"] = tools

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

        # Extract text from response
        texts = [block["text"] for block in body.get("content", []) if block.get("type") == "text"]
        raw = "\n".join(texts).strip()

        # Auto-parse JSON for extraction/classification tasks
        try:
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return raw

    # ── Convenience class methods ─────────────────────────────────────────────

    @classmethod
    def quick(cls, task_type: str, **kwargs) -> TaskResult:
        """One-liner helper: AIAgent.quick('summarize', text='...')"""
        agent = cls()
        return agent.run({"task_type": task_type, "name": task_type, **kwargs})
