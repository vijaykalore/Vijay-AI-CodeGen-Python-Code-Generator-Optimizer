from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from ..euri_client import Euri
from ..prompts.templates import generation_prompt, tests_prompt, explanation_prompt


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    # Remove common markdown fences
    if t.startswith("```"):
        # remove first line
        lines = t.splitlines()
        # drop leading ```lang or ```
        if lines:
            lines = lines[1:]
        # drop trailing ``` if present
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def generate_code_for_topic(
    euri: Euri,
    spec: Dict[str, Any],
    out_dir: Path,
    *,
    max_tokens: Optional[int] = None,
) -> Tuple[Path, Path]:
    """Generate a Python module and its pytest file for a DSA spec."""
    module_name = spec["id"]
    module_path = out_dir / f"{module_name}.py"
    test_path = out_dir / f"test_{module_name}.py"

    prompt = generation_prompt(spec)
    code = _strip_code_fences(euri.complete(prompt, max_tokens=max_tokens))

    test_code = _strip_code_fences(euri.complete(tests_prompt(spec, code), max_tokens=max_tokens))

    module_path.write_text(code, encoding="utf-8")
    test_path.write_text(test_code, encoding="utf-8")
    return module_path, test_path


def explain_code(euri: Euri, code: str) -> str:
    return euri.complete(explanation_prompt(code), max_tokens=2000)
