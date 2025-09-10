from __future__ import annotations

from typing import Any, Dict, Optional

from euriai import EuriaiClient

from .config import Settings


class Euri:
    """Thin wrapper around the EuriaiClient to standardize calls and error handling."""

    def __init__(self, settings: Settings):
        self._client = EuriaiClient(api_key=settings.api_key, model=settings.model)
        self._temperature = settings.temperature
        self._max_tokens = settings.max_tokens

    def complete(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> str:
        """Generate a completion string from Euri AI, returning text content only.

        Falls back gracefully if the expected shape changes slightly.
        """
        params: Dict[str, Any] = {
            "prompt": prompt,
            "temperature": self._temperature if temperature is None else temperature,
            "max_tokens": self._max_tokens if max_tokens is None else max_tokens,
        }
        if model:
            # Some SDKs accept model in constructor only; try both.
            try:
                self._client.model = model  # type: ignore[attr-defined]
            except Exception:
                params["model"] = model
        resp = self._client.generate_completion(**params)
        # Expected: response["choices"][0]["message"]["content"]
        try:
            return resp["choices"][0]["message"]["content"].strip()
        except Exception:
            # Try alternative keys
            for key in ("content", "text"):
                if key in resp:
                    return str(resp[key]).strip()
            return str(resp)
