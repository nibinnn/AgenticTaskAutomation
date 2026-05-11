import re
from typing import Any, Optional
from models.base_model import BaseModel
import json
import os
import urllib.request

class ClaudeModel(BaseModel):
    """

    """

    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: Optional[str] = None):
        super().__init__("ClaudeModel", "Delegates call to Claude via the Anthropic API")
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    def request(self, data:Any = None ):
        if data:
            data["model"] = self.model
            
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

        return cleaned
    


    def call_claude(
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
