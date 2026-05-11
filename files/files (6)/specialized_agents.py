"""
Specialized Agents for different task domains.
"""
import os
import json
import csv
import time
import random
import hashlib
import re
from pathlib import Path
from typing import Any
from agents.base_agent import BaseAgent


# ─── Data Agent ───────────────────────────────────────────────────────────────

class DataAgent(BaseAgent):
    """Handles data analysis, aggregation, and statistical tasks."""

    SUPPORTED = {"analyze", "aggregate", "filter", "sort", "summarize", "validate"}

    def __init__(self):
        super().__init__("DataAgent", "Analyzes and processes structured data")

    def can_handle(self, task_type: str) -> bool:
        return task_type in self.SUPPORTED

    def execute(self, task: dict) -> Any:
        op = task.get("operation", "analyze")
        data = task.get("data", [])

        if op == "analyze":
            return self._analyze(data)
        elif op == "aggregate":
            return self._aggregate(data, task.get("group_by"))
        elif op == "filter":
            return self._filter(data, task.get("condition", {}))
        elif op == "sort":
            return self._sort(data, task.get("key"), task.get("reverse", False))
        elif op == "summarize":
            return self._summarize(data)
        elif op == "validate":
            return self._validate(data, task.get("schema", {}))
        else:
            raise ValueError(f"Unknown operation: {op}")

    def _analyze(self, data: list) -> dict:
        if not data:
            return {"count": 0}
        numeric_fields = {}
        for item in data:
            for k, v in item.items():
                if isinstance(v, (int, float)):
                    numeric_fields.setdefault(k, []).append(v)
        stats = {}
        for field, values in numeric_fields.items():
            stats[field] = {
                "min": min(values),
                "max": max(values),
                "mean": round(sum(values) / len(values), 2),
                "count": len(values),
            }
        return {"record_count": len(data), "field_stats": stats}

    def _aggregate(self, data: list, group_by: str) -> dict:
        if not group_by:
            return {"error": "group_by field required"}
        groups = {}
        for item in data:
            key = item.get(group_by, "unknown")
            groups.setdefault(key, []).append(item)
        return {k: len(v) for k, v in groups.items()}

    def _filter(self, data: list, condition: dict) -> list:
        field = condition.get("field")
        op = condition.get("op", "eq")
        value = condition.get("value")
        results = []
        for item in data:
            v = item.get(field)
            if op == "eq" and v == value:
                results.append(item)
            elif op == "gt" and isinstance(v, (int, float)) and v > value:
                results.append(item)
            elif op == "lt" and isinstance(v, (int, float)) and v < value:
                results.append(item)
            elif op == "contains" and value in str(v):
                results.append(item)
        return results

    def _sort(self, data: list, key: str, reverse: bool) -> list:
        return sorted(data, key=lambda x: x.get(key, 0), reverse=reverse)

    def _summarize(self, data: list) -> dict:
        return {
            "total_records": len(data),
            "fields": list(data[0].keys()) if data else [],
            "sample": data[:3],
        }

    def _validate(self, data: list, schema: dict) -> dict:
        errors = []
        for i, item in enumerate(data):
            for field, rules in schema.items():
                if rules.get("required") and field not in item:
                    errors.append(f"Row {i}: missing required field '{field}'")
                elif field in item and "type" in rules:
                    expected = rules["type"]
                    actual = type(item[field]).__name__
                    if actual != expected:
                        errors.append(f"Row {i}: '{field}' expected {expected}, got {actual}")
        return {"valid": len(errors) == 0, "errors": errors, "checked": len(data)}


# ─── File Agent ───────────────────────────────────────────────────────────────

class FileAgent(BaseAgent):
    """Handles file I/O operations: read, write, copy, delete, list."""

    SUPPORTED = {"read", "write", "list", "delete", "checksum", "search"}

    def __init__(self, base_dir: str = "/tmp/agent_workspace"):
        super().__init__("FileAgent", "Manages file system operations")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def can_handle(self, task_type: str) -> bool:
        return task_type in self.SUPPORTED

    def execute(self, task: dict) -> Any:
        op = task.get("operation", "list")
        if op == "write":
            return self._write(task["filename"], task["content"])
        elif op == "read":
            return self._read(task["filename"])
        elif op == "list":
            return self._list(task.get("pattern", "*"))
        elif op == "delete":
            return self._delete(task["filename"])
        elif op == "checksum":
            return self._checksum(task["filename"])
        elif op == "search":
            return self._search(task["pattern"], task.get("directory"))
        else:
            raise ValueError(f"Unknown operation: {op}")

    def _write(self, filename: str, content: str) -> dict:
        path = self.base_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return {"path": str(path), "bytes": len(content.encode()), "written": True}

    def _read(self, filename: str) -> dict:
        path = self.base_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        content = path.read_text()
        return {"filename": filename, "content": content, "lines": content.count("\n") + 1}

    def _list(self, pattern: str) -> list:
        files = list(self.base_dir.glob(pattern))
        return [{"name": f.name, "size": f.stat().st_size, "is_dir": f.is_dir()} for f in files]

    def _delete(self, filename: str) -> dict:
        path = self.base_dir / filename
        if path.exists():
            path.unlink()
            return {"deleted": True, "filename": filename}
        return {"deleted": False, "error": "File not found"}

    def _checksum(self, filename: str) -> dict:
        path = self.base_dir / filename
        content = path.read_bytes()
        return {"filename": filename, "md5": hashlib.md5(content).hexdigest(),
                "sha256": hashlib.sha256(content).hexdigest()}

    def _search(self, pattern: str, directory: str = None) -> list:
        search_dir = Path(directory) if directory else self.base_dir
        results = []
        for f in search_dir.rglob("*"):
            if f.is_file() and pattern.lower() in f.name.lower():
                results.append(str(f))
        return results


# ─── Transform Agent ──────────────────────────────────────────────────────────

class TransformAgent(BaseAgent):
    """Handles data format transformations: JSON↔CSV, text processing, encoding."""

    SUPPORTED = {"json_to_csv", "csv_to_json", "flatten", "encode", "template", "extract"}

    def __init__(self):
        super().__init__("TransformAgent", "Transforms data between formats")

    def can_handle(self, task_type: str) -> bool:
        return task_type in self.SUPPORTED

    def execute(self, task: dict) -> Any:
        op = task.get("operation")
        if op == "json_to_csv":
            return self._json_to_csv(task["data"])
        elif op == "csv_to_json":
            return self._csv_to_json(task["csv_text"])
        elif op == "flatten":
            return self._flatten(task["data"], task.get("separator", "."))
        elif op == "encode":
            return self._encode(task["text"], task.get("method", "base64"))
        elif op == "template":
            return self._template(task["template"], task.get("variables", {}))
        elif op == "extract":
            return self._extract(task["text"], task.get("pattern"))
        else:
            raise ValueError(f"Unknown operation: {op}")

    def _json_to_csv(self, data: list) -> str:
        if not data:
            return ""
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def _csv_to_json(self, csv_text: str) -> list:
        import io
        reader = csv.DictReader(io.StringIO(csv_text))
        return list(reader)

    def _flatten(self, data: dict, separator: str, prefix: str = "") -> dict:
        result = {}
        for k, v in data.items():
            key = f"{prefix}{separator}{k}" if prefix else k
            if isinstance(v, dict):
                result.update(self._flatten(v, separator, key))
            else:
                result[key] = v
        return result

    def _encode(self, text: str, method: str) -> dict:
        import base64
        if method == "base64":
            encoded = base64.b64encode(text.encode()).decode()
        elif method == "hex":
            encoded = text.encode().hex()
        elif method == "url":
            from urllib.parse import quote
            encoded = quote(text)
        else:
            encoded = text
        return {"original": text, "encoded": encoded, "method": method}

    def _template(self, template: str, variables: dict) -> str:
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def _extract(self, text: str, pattern: str) -> list:
        return re.findall(pattern, text) if pattern else []


# ─── Scheduler Agent ──────────────────────────────────────────────────────────

class SchedulerAgent(BaseAgent):
    """Manages task scheduling, retries, and dependency resolution."""

    def __init__(self):
        super().__init__("SchedulerAgent", "Orchestrates task scheduling and retries")
        self.queue: list[dict] = []
        self.completed: list[str] = []

    def can_handle(self, task_type: str) -> bool:
        return task_type in {"schedule", "retry", "chain", "parallel"}

    def execute(self, task: dict) -> Any:
        op = task.get("operation", "schedule")
        if op == "schedule":
            return self._schedule(task)
        elif op == "retry":
            return self._retry(task)
        elif op == "chain":
            return self._chain(task.get("steps", []))
        return {"scheduled": True}

    def _schedule(self, task: dict) -> dict:
        priority = task.get("priority", 5)
        delay = task.get("delay_seconds", 0)
        self.queue.append({**task, "priority": priority, "scheduled_at": time.time() + delay})
        self.queue.sort(key=lambda x: (-x["priority"], x["scheduled_at"]))
        return {"queued": True, "queue_length": len(self.queue), "priority": priority}

    def _retry(self, task: dict) -> dict:
        max_retries = task.get("max_retries", 3)
        return {"retries_allowed": max_retries, "strategy": task.get("strategy", "linear")}

    def _chain(self, steps: list) -> dict:
        return {"steps": len(steps), "estimated_duration": sum(s.get("timeout", 5) for s in steps)}
