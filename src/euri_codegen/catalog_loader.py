from __future__ import annotations

import json
from importlib import resources
from typing import Any, List


def load_catalog() -> List[dict[str, Any]]:
    with resources.files("euri_codegen.catalog").joinpath("dsa_catalog.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def list_topics() -> list[str]:
    return [item["id"] for item in load_catalog()]
