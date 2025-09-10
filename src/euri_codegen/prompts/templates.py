from __future__ import annotations

from typing import Any, Dict


SYSTEM_SAFETY = """
You are a senior Python engineer and performance-minded code reviewer.
- Generate idiomatic Python 3.10+ code following PEP8.
- Add minimal docstrings and type hints.
- Do not include placeholder text like 'your code here'.
- Avoid external dependencies beyond the standard library unless required by spec.
- Ensure deterministic behavior and avoid randomness.
""".strip()


def generation_prompt(spec: Dict[str, Any]) -> str:
    return f"""
{SYSTEM_SAFETY}

Task: Implement the following DSA specification as a complete Python module with:
- function(s) defined per signature
- clear docstrings and type hints
- edge case handling
- time and space complexity notes in a top-level module docstring
- minimal inline tests in `if __name__ == '__main__':` guarded block (optional)

Specification (JSON):
{spec}

Output ONLY valid Python code for a single .py file, with no markdown.
""".strip()


def tests_prompt(spec: Dict[str, Any], code: str) -> str:
    header = f"""
{SYSTEM_SAFETY}

Task: Write a pytest test module for the implementation below, reflecting the spec.
- Include happy-path tests and at least 2 edge cases.
- Use parameterized tests when appropriate.
- Avoid network or file I/O.

Spec (JSON):
{spec}

Implementation code:
""".strip()
    return header + "\n" + code + "\n\n" + "Output ONLY valid Python test code for a single test_*.py file, no markdown.".strip()


def optimization_prompt(code: str, level: str) -> str:
    header = f"""
{SYSTEM_SAFETY}

Refactor and optimize the following Python code. Apply these levels: {level}.
- Maintain identical public API and behavior.
- Improve readability (naming, structure) and add type hints.
- Optimize algorithmic complexity if feasible; otherwise micro-optimizations.
- Avoid premature optimization that harms clarity.

Original code:
""".strip()
    return header + "\n" + code + "\n\n" + "Output ONLY the optimized code as a single Python file.".strip()


def explanation_prompt(code: str) -> str:
    header = f"""
{SYSTEM_SAFETY}

Explain the code below for a mid-level Python developer.
- Overview, key functions, algorithm choice
- Complexity analysis
- Potential failure modes and tests worth adding

Code:
""".strip()
    return header + "\n" + code + "\n\n" + "Return a concise explanation in plain text.".strip()
