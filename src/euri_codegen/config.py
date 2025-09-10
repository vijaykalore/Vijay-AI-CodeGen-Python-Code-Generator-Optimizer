from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


def _get_from_secrets(key: str) -> Optional[str]:
    # Try to read from Streamlit secrets if available
    try:
        import streamlit as st  # type: ignore

        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return None


def _get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    # Prefer environment, then Streamlit secrets, then default
    val = os.getenv(key)
    if val is not None:
        return val
    sec = _get_from_secrets(key)
    if sec is not None:
        return sec
    return default


DEFAULT_MODEL = _get_config("EURI_MODEL", "gpt-4.1-nano") or "gpt-4.1-nano"


@dataclass
class Settings:
    api_key: str
    model: str = DEFAULT_MODEL
    temperature: float = 0.2
    max_tokens: int = 3000

    @staticmethod
    def load(env_file: Optional[str] = None) -> "Settings":
        # Load .env for local dev; on Streamlit Cloud, secrets drive values
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        key = _get_config("EURI_API_KEY")
        if not key:
            raise RuntimeError(
                "EURI_API_KEY is not set. Set it in environment, a .env file, or Streamlit secrets."
            )
        model = _get_config("EURI_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL
        temp_str = _get_config("EURI_TEMPERATURE", "0.2") or "0.2"
        max_tokens_str = _get_config("EURI_MAX_TOKENS", "3000") or "3000"
        temp = float(temp_str)
        max_tokens = int(max_tokens_str)
        return Settings(api_key=key, model=model, temperature=temp, max_tokens=max_tokens)
