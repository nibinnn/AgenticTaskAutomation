"""
Base LLM model - Foundation for all LLM.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


class BaseModel(ABC):
    """Abstract base class for all llm models."""

    def __init__(self, model: str, api_key: str = ""):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def request(self, task: dict) -> Any:
        """Subclasses implement to make llm calls."""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.model})>"
