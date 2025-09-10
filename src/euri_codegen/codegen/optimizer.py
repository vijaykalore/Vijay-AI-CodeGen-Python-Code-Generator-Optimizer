from __future__ import annotations

from typing import Literal

from ..euri_client import Euri
from ..prompts.templates import optimization_prompt


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def optimize_code(euri: Euri, code: str, *, level: Literal["one", "readability", "performance", "memory", "all"] = "all") -> str:
    prompt = optimization_prompt(code, level)
    return _strip_code_fences(euri.complete(prompt, max_tokens=2500))
