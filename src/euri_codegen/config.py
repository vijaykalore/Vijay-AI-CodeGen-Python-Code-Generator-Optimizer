from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

DEFAULT_MODEL = os.getenv("EURI_MODEL", "gpt-4.1-nano")


@dataclass
class Settings:
    api_key: str
    model: str = DEFAULT_MODEL
    temperature: float = 0.2
    max_tokens: int = 3000

    @staticmethod
    def load(env_file: Optional[str] = None) -> "Settings":
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        key = os.getenv("EURI_API_KEY")
        if not key:
            raise RuntimeError(
                "EURI_API_KEY is not set. Set it in environment or a .env file."
            )
        model = os.getenv("EURI_MODEL", DEFAULT_MODEL)
        temp = float(os.getenv("EURI_TEMPERATURE", "0.2"))
        max_tokens = int(os.getenv("EURI_MAX_TOKENS", "3000"))
        return Settings(api_key=key, model=model, temperature=temp, max_tokens=max_tokens)
