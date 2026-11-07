"""All LLM calls go through ask_llm(), so the provider can be swapped in one place."""
from dataclasses import dataclass

import anthropic

from src.config import LLM_API_KEY, LLM_MODEL


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY is not set. Add it to .env in the project root.")
        _client = anthropic.Anthropic(api_key=LLM_API_KEY)
    return _client


def ask_llm(system: str, user: str, max_tokens: int = 600) -> LLMResponse:
    response = _get_client().messages.create(
        model=LLM_MODEL,
        system=system,
        messages=[{"role": "user", "content": user}],
        max_tokens=max_tokens,
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return LLMResponse(
        text=text,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )