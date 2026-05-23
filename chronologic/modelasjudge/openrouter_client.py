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
# API call
# ---------------------------------------------------------------------------

def call_openrouter_chat(
    client, model_id, user_content, system_content="",
    max_tokens=400, max_retries=3, debug=False, reasoning_effort="none",
):
    """Call the OpenRouter chat completions endpoint with retry on rate limits.

    Args:
        client:           openai.OpenAI client pointed at OpenRouter base URL.
        model_id:         OpenRouter model identifier string.
        user_content:     user message text.
        system_content:   system message text (omitted if empty).
        max_tokens:       maximum tokens in the response.
        max_retries:      number of attempts before raising.
        debug:            if True, print the full response object.
        reasoning_effort: one of "none", "low", "medium", "high"; forwarded to
                          OpenRouter's unified reasoning.effort field, which
                          translates to Anthropic thinking tokens, Gemini thoughts,
                          or OpenAI reasoning_effort as appropriate.

    Returns:
        str: the assistant message content, or "" if content is None/empty.
    """
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    messages.append({"role": "user", "content": user_content})

    if debug:
        print(f"  [debug] OpenRouter → model={model_id}, max_tokens={max_tokens}, reasoning_effort={reasoning_effort!r}")
        print(f"  [debug] prompt (first 300 chars): {user_content[:300]!r}")

    extra_body = {"reasoning": {"effort": reasoning_effort}}
    if reasoning_effort == "none":
        extra_body["chat_template_kwargs"] = {"enable_thinking": False}

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                extra_body=extra_body,
            )
            if debug:
                print(f"  [debug] raw response: {response}")

            if not response.choices:
                print(f"  WARNING: OpenRouter returned no choices — {response}")
                return ""
            content = response.choices[0].message.content
            if content is None:
                msg = response.choices[0].message
                fallback = getattr(msg, "reasoning", None) or getattr(msg, "text", None)
                if not debug:
                    print(
                        f"  WARNING: content=None from OpenRouter "
                        f"(finish_reason={response.choices[0].finish_reason!r}); "
                        f"fallback={'found' if fallback else 'not found'}. "
                        f"Try --debug for full response."
                    )
                return fallback or ""
            return content
        except Exception as exc:
            if attempt < max_retries - 1 and "rate" in str(exc).lower():
                time.sleep(2 ** attempt)
                continue
            raise
    return ""
