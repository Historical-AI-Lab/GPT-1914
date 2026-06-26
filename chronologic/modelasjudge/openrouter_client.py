"""
openrouter_client.py — OpenRouter API helpers for the modelasjudge pipeline.

Shared by free_generation.py, judge_scoring.py, and judge_reliability.py.
"""

import os
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

OPENROUTER_PREFIXES = (
    "qwen/", "meta-llama/", "anthropic/", "google/",
    "mistralai/", "deepseek/", "nvidia/", "openai/",
)

_SCRIPT_DIR = Path(__file__).parent


def is_openrouter_model(model_id):
    """Return True if model_id starts with a known OpenRouter provider prefix.

    OpenRouter model IDs use lowercase provider prefixes (e.g. ``anthropic/claude-opus-4-7``),
    while HuggingFace IDs use title-case (e.g. ``Qwen/Qwen2.5-7B-Instruct``).
    """
    return any(model_id.startswith(p) for p in OPENROUTER_PREFIXES)


def _is_anthropic_openrouter(model_id):
    """Return True if model_id is an Anthropic model served via OpenRouter."""
    return model_id.startswith("anthropic/")


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

_DEFAULT_CRED_PATH = _SCRIPT_DIR.parent / "bertclassify" / "OpenRouterCredentials.txt"


def load_openrouter_api_key(cred_path=None):
    """Return the OpenRouter API key.

    Resolution order:
    1. ``OPENROUTER_API_KEY`` environment variable.
    2. ``password:`` line in *cred_path* (default: ``bertclassify/OpenRouterCredentials.txt``).

    Args:
        cred_path: path to credentials file, or None for the default.

    Returns:
        str: API key.

    Raises:
        ValueError: if the credentials file has no ``password:`` line.
        FileNotFoundError: if *cred_path* does not exist.
    """
    env_key = os.environ.get("OPENROUTER_API_KEY")
    if env_key:
        return env_key

    path = Path(cred_path) if cred_path else _DEFAULT_CRED_PATH
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip().lower().startswith("password:"):
            return line.split(":", 1)[1].strip()
    raise ValueError(f"No 'password:' line found in {path}")


def make_openrouter_client(cred_path=None):
    """Create an openai.OpenAI client pointed at the OpenRouter API.

    Args:
        cred_path: path to credentials file, or None for the default.

    Returns:
        openai.OpenAI instance.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "The 'openai' package is required for OpenRouter models. "
            "Install it with: pip install openai"
        ) from exc
    api_key = load_openrouter_api_key(cred_path)
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


# ---------------------------------------------------------------------------
# Request shaping
# ---------------------------------------------------------------------------

def _build_extra_body(model_id, reasoning_effort, max_tokens):
    """Build the extra_body dict for an OpenRouter chat-completions request.

    Rules:
    - effort=="none": disable thinking (chat_template_kwargs); Anthropic also gets
      verbosity="low" since Opus 4.7 is adaptive-only and can't fully opt out.
      No +2048 bump, no budget hint.
    - effort in {low,medium,high}: Anthropic gets verbosity=effort (the live knob
      per output_config.effort); all providers get reasoning.max_tokens set to
      max_tokens - 1024 as a soft budget hint. Non-Anthropic providers also get
      reasoning.effort (the OpenRouter unified field).

    Args:
        model_id:        OpenRouter model identifier.
        reasoning_effort: "none" | "low" | "medium" | "high"
        max_tokens:      the *caller-specified* cap before the +2048 bump is applied
                         (used to compute the thinking-budget hint).

    Returns:
        dict: extra_body to pass to client.chat.completions.create().
    """
    is_anthropic = _is_anthropic_openrouter(model_id)

    if reasoning_effort == "none":
        body = {"chat_template_kwargs": {"enable_thinking": False}}
        if is_anthropic:
            body["verbosity"] = "low"
        else:
            body["reasoning"] = {"effort": "none"}
        return body

    # thinking enabled — reasoning_effort in {low, medium, high}
    # Budget hint: max_tokens here is the caller-specified value; the +2048 bump
    # will be added to the wire call, so effective budget = (max_tokens+2048)-1024.
    thinking_budget = (max_tokens + 2048) - 1024

    if is_anthropic:
        # reasoning.effort is silently ignored on Opus 4.7 / Sonnet 4.6;
        # verbosity is the live control for output_config.effort.
        body = {
            "verbosity": reasoning_effort,
            "reasoning": {"max_tokens": thinking_budget},
        }
    else:
        # OpenRouter rejects sending both "effort" and "max_tokens" together
        # for non-Anthropic models; send only the effort knob.
        body = {
            "reasoning": {
                "effort": reasoning_effort,
            },
        }
    return body


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------

def call_openrouter_chat(
    client, model_id, user_content, system_content="",
    max_tokens=400, max_retries=3, debug=False, reasoning_effort="none",
):
    """Call the OpenRouter chat completions endpoint with retry on rate limits.

    When reasoning_effort != "none", max_tokens is bumped by 2048 on the wire
    to leave headroom between thinking-token spend and the visible answer.
    A thinking-budget hint (max_tokens + 2048 - 1024) is also sent.

    If the model returns finish_reason=="length" while thinking was enabled,
    the call is retried once with thinking disabled — the assumption being that
    thinking consumed the budget and a direct answer is preferable to an empty one.

    Args:
        client:           openai.OpenAI client pointed at OpenRouter base URL.
        model_id:         OpenRouter model identifier string.
        user_content:     user message text.
        system_content:   system message text (omitted if empty).
        max_tokens:       maximum visible-answer tokens; bumped +2048 on the wire
                          when reasoning_effort != "none".
        max_retries:      number of attempts before raising.
        debug:            if True, print the full response object.
        reasoning_effort: one of "none", "low", "medium", "high". Anthropic models
                          receive this as verbosity; other providers receive it as
                          reasoning.effort.

    Returns:
        str: the assistant message content, or "" if content is None/empty.
    """
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    messages.append({"role": "user", "content": user_content})

    def _do_request(effort):
        effective_max = max_tokens + 2048 if effort != "none" else max_tokens
        extra_body = _build_extra_body(model_id, effort, max_tokens)
        if debug:
            thinking_budget = extra_body.get("reasoning", {}).get("max_tokens", "n/a")
            verbosity = extra_body.get("verbosity", "n/a")
            print(
                f"  [debug] OpenRouter → model={model_id}, "
                f"max_tokens={effective_max}, effort={effort!r}, "
                f"verbosity={verbosity!r}, thinking_budget={thinking_budget}"
            )
            print(f"  [debug] prompt (first 300 chars): {user_content[:300]!r}")
        return client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=effective_max,
            extra_body=extra_body,
        )

    def _extract(response):
        if debug:
            print(f"  [debug] raw response: {response}")
        if not response.choices:
            print(f"  WARNING: OpenRouter returned no choices — {response}")
            return "", None
        choice = response.choices[0]
        finish_reason = choice.finish_reason
        content = choice.message.content
        if content is None:
            msg = choice.message
            fallback = getattr(msg, "reasoning", None) or getattr(msg, "text", None)
            if not debug:
                print(
                    f"  WARNING: content=None from OpenRouter "
                    f"(finish_reason={finish_reason!r}); "
                    f"fallback={'found' if fallback else 'not found'}. "
                    f"Try --debug for full response."
                )
            return fallback or "", finish_reason
        return content, finish_reason

    for attempt in range(max_retries):
        try:
            response = _do_request(reasoning_effort)
            content, finish_reason = _extract(response)

            # If thinking ran the model out of tokens, retry once without thinking.
            if finish_reason == "length" and reasoning_effort != "none":
                if debug:
                    print(
                        f"  [debug] finish_reason=length with thinking enabled — "
                        f"retrying once with reasoning_effort='none'"
                    )
                response = _do_request("none")
                content, finish_reason = _extract(response)

            return content
        except Exception as exc:
            if attempt < max_retries - 1 and "rate" in str(exc).lower():
                time.sleep(2 ** attempt)
                continue
            raise
    return ""
