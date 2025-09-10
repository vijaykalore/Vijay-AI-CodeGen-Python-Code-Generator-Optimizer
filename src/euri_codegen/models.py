from __future__ import annotations

from typing import Any, List, Optional, Tuple, Union
from pydantic import BaseModel, Field, ValidationError, field_validator


class SpecInput(BaseModel):
    name: str
    type: str
    desc: str


class SpecExample(BaseModel):
    input: dict[str, Any]
    output: Any


class Spec(BaseModel):
    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    title: str
    summary: str
    function_signature: str
    inputs: List[SpecInput] = Field(default_factory=list)
    outputs: dict[str, Any]
    constraints: List[str] = Field(default_factory=list)
    examples: List[SpecExample] = Field(default_factory=list)

    @field_validator("function_signature")
    @classmethod
    def ensure_signature_like(cls, v: str) -> str:
        if "def " not in v and not v.strip().startswith("class "):
            raise ValueError("function_signature must contain 'def ' or start with 'class '")
        return v


def validate_specs(data: list[dict[str, Any]]) -> list[Spec]:
    return [Spec.model_validate(item) for item in data]
