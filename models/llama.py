import re
from typing import Any, Optional
from models.base_model import BaseModel
import json
import os
import urllib.request
# from openai import OpenAI

# client = OpenAI(
#     base_url="http://localhost:8000/v1",  # change if using hosted provider
#     api_key="EMPTY"  # not needed for local
# )

class LlamaModel(BaseModel):
    """

    """

    def __init__(self, model: str = "llama3:latest", api_key: Optional[str] = None):
        super().__init__("ClaudeModel", "Delegates call to Claude via the Anthropic API")
        self.model = model
        # self.api_key = api_key or ""

    def request(self, data:Any = None ):
        if data:
            data["model"] = self.model

        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                # "x-api-key": self.api_key,
                # "stream": False
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())

        print(body)
        texts = [b["text"] for b in body.get("content", []) if b.get("type") == "text"]
        raw = "\n".join(texts).strip()

        # Strip markdown fences if model wraps in them
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()

        return cleaned


    def call_agent(
        self,
        prompt: str,
        system: str,
        tools: Optional[list],
        max_tokens: int,
    ) -> Any:
        import urllib.request

        print(f"prompt={prompt}")
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
            "http://localhost:11434/api/generate",
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=300) as resp:
            body = json.loads(resp.read().decode())
        print(f"body={body}")
        # Extract text from response
        texts = [block["text"] for block in body.get("content", []) if block.get("type") == "text"]
        raw = "\n".join(texts).strip()

        # Auto-parse JSON for extraction/classification tasks
        try:
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return raw
