"""All LLM calls go through ask_llm(), so the provider can be swapped in one place.

Anthropic API notes (SDK 2.x, API version 2026-10-21):
- temperature / top_p / top_k are no longer accepted.
- Claude Haiku 5.5 uses adaptive thinking by default. Thinking tokens count toward
  max_tokens, so a small limit can end the response inside the thinking block,
  before any text: stop_reason == "max_tokens" with an empty answer.
- Effort ("low" ... "max") trades quality for speed and cost; it is set through
  output_config. Thinking can be disabled with thinking={"type": "disabled"}.
"""
from dataclasses import dataclass

import anthropic

from src.config import LLM_API_KEY, LLM_EFFORT, LLM_MAX_TOKENS, LLM_MODEL, LLM_THINKING


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int              # includes thinking tokens (billed as output)
    stop_reason: str = "end_turn"   # "max_tokens" means the answer was cut off

    @property
    def truncated(self) -> bool:
        return self.stop_reason == "max_tokens"


class LLMError(RuntimeError):
    pass


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not LLM_API_KEY:
            raise LLMError("LLM_API_KEY is not set. Add it to .env in the project root.")
        _client = anthropic.Anthropic(api_key=LLM_API_KEY)
    return _client


def ask_llm(system: str, user: str, max_tokens: int = LLM_MAX_TOKENS,
            effort: str | None = LLM_EFFORT, thinking: bool = LLM_THINKING) -> LLMResponse:
    options = {}
    if effort is not None:
        options["output_config"] = {"effort": effort}
    if not thinking:
        options["thinking"] = {"type": "disabled"}

    response = _get_client().messages.create(
        model=LLM_MODEL,
        system=system,
        messages=[{"role": "user", "content": user}],
        max_tokens=max_tokens,
        **options,
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    result = LLMResponse(
        text=text,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        stop_reason=response.stop_reason,
    )
    if not text.strip():
        # Fail loudly: an empty answer must never be shown or scored as a real answer.
        raise LLMError(f"Empty answer (stop_reason={result.stop_reason}, "
                       f"output_tokens={result.output_tokens}). "
                       "If stop_reason is 'max_tokens', raise LLM_MAX_TOKENS or lower LLM_EFFORT.")
    return result
