"""
openrouter_client.py — OpenRouter API helpers for the modelasjudge pipeline.

Shared by free_generation.py, judge_scoring.py, and judge_reliability.py.
"""

import json
import os
import time
from pathlib import Path

import httpx

# Transient failures worth retrying beyond rate limits: a truncated/malformed
# response body (JSONDecodeError -- seen from OpenRouter on long-running max-
# effort calls) and network-level errors (httpx.TransportError covers
# connect/read/write timeouts and dropped connections).
_TRANSIENT_EXCEPTIONS = (json.JSONDecodeError, httpx.TransportError)

# Extra wire max_tokens headroom granted to a same-effort retry when a
# provider rejects the disable-thinking downgrade with "Reasoning is
# mandatory for this endpoint and cannot be disabled" (seen live on
# google/gemini-3.7-flash; also documented for openai/gpt-oss-120b and
# google/gemini-3.1-pro-preview in stylejudge/model_stable.py). Bigger than
# the existing +2048 base bump because the model already exhausted that
# budget once while thinking.
_MANDATORY_REASONING_RETRY_BUMP = 4096


def _is_mandatory_reasoning_error(exc):
    """Return True if exc is OpenRouter's 400 refusing to disable reasoning.

    Matches loosely (case-insensitive "mandatory" + a "disab*" fragment)
    rather than pinning the exact observed sentence, to tolerate minor
    wording drift across providers.

    `openai` is imported lazily, function-local: call_openrouter_chat only
    ever runs with an already-constructed `client`, and any real client
    required `openai` to already be importable to build it in the first
    place (make_openrouter_client does `from openai import OpenAI`), so this
    import is a cache hit in practice. The ImportError guard is defensive
    only, preserving today's behavior in the practically-impossible case
    where it isn't.
    """
    try:
        import openai
    except ImportError:
        return False
    if not isinstance(exc, openai.BadRequestError):
        return False
    msg = str(exc).lower()
    return "mandatory" in msg and "disab" in msg


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

OPENROUTER_PREFIXES = (
    "qwen/", "meta-llama/", "anthropic/", "google/",
    "mistralai/", "deepseek/", "nvidia/", "openai/", "moonshotai/",
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


# Models that emit chain-of-thought as ordinary visible content unconditionally
# (baked into training, not gated by the API's reasoning.effort/enable_thinking
# flags). These need a large max_tokens regardless of the caller's
# reasoning_effort setting, or the CoT alone will exhaust the budget before any
# answer is produced.
ALWAYS_REASONS_PREFIXES = (
    "deepseek/deepseek-r1",
    "qwen/qwq",
)


def always_reasons(model_id):
    """Return True if model_id is known to always emit visible chain-of-thought."""
    return any(model_id.startswith(p) for p in ALWAYS_REASONS_PREFIXES)


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
    response_format=None, return_meta=False,
):
    """Call the OpenRouter chat completions endpoint with retry on rate limits.

    When reasoning_effort != "none", max_tokens is bumped by 2048 on the wire
    to leave headroom between thinking-token spend and the visible answer.
    A thinking-budget hint (max_tokens + 2048 - 1024) is also sent.

    If the model returns finish_reason=="length" while thinking was enabled,
    the call is retried once with thinking disabled — the assumption being that
    thinking consumed the budget and a direct answer is preferable to an empty one.
    Some endpoints (e.g. google/gemini-3.7-flash) reject that retry with a 400
    ("Reasoning is mandatory for this endpoint and cannot be disabled") since
    they don't allow disabling reasoning at all; in that case the call is
    retried once more at the ORIGINAL reasoning_effort with extra max_tokens
    headroom (_MANDATORY_REASONING_RETRY_BUMP) instead. If that also fails,
    the original (possibly length-truncated) content is kept rather than
    raising.

    Args:
        client:           openai.OpenAI client pointed at OpenRouter base URL.
        model_id:         OpenRouter model identifier string.
        user_content:     user message text.
        system_content:   system message text (omitted if empty).
        max_tokens:       maximum visible-answer tokens; bumped +2048 on the wire
                          when reasoning_effort != "none".
        max_retries:      number of attempts before raising.
        debug:            if True, print the full response object.
        reasoning_effort: one of "none", "minimal", "low", "medium", "high", "max".
                          Anthropic models receive this as verbosity (values outside
                          low/medium/high are unlikely to be accepted there); other
                          providers receive it as reasoning.effort.
        response_format:  optional structured-output spec, passed through to the API
                          unchanged. For a JSON schema the chat-completions shape is
                          {"type": "json_schema",
                           "json_schema": {"name": ..., "strict": True, "schema": {...}}}
                          -- note this nests under "json_schema", unlike the flat
                          Responses-API "text_format" used in evalcode/. When set,
                          provider.require_parameters is also sent, so routing skips
                          providers of this model that lack structured-output support.
                          None (the default) leaves every existing caller unaffected.
        return_meta:      if True, return (content, meta) instead of a bare string,
                          where meta = {"downgraded": bool, "finish_reason": str,
                          "mandatory_reasoning_retry": bool}. "downgraded" is True
                          iff the length-triggered retry-without-thinking actually
                          succeeded (False if the endpoint refuses to disable
                          reasoning at all, even if a same-effort bumped retry
                          then recovered an answer). "mandatory_reasoning_retry"
                          is True iff that bumped-retry fallback path fired.
                          Default False leaves every existing caller unaffected.

    Returns:
        str, or (str, dict) if return_meta: the assistant message content (or ""
        if content is None/empty), optionally paired with retry metadata.
    """
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    messages.append({"role": "user", "content": user_content})

    def _do_request(effort, extra_bump=0):
        effective_max = (max_tokens + 2048 if effort != "none" else max_tokens) + extra_bump
        # extra_body is always built from the pre-bump max_tokens, matching
        # _build_extra_body's documented contract regardless of extra_bump.
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
        kwargs = {}
        if response_format is not None:
            kwargs["response_format"] = response_format
            # The same model is served by several providers and only some support
            # structured outputs; require_parameters keeps routing to the ones that do.
            extra_body.setdefault("provider", {})["require_parameters"] = True
            if debug:
                print(f"  [debug] response_format: {response_format}")
        return client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=effective_max,
            extra_body=extra_body,
            **kwargs,
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
            original_content, original_finish_reason = content, finish_reason

            # If thinking ran the model out of tokens, retry once without thinking.
            downgraded = finish_reason == "length" and reasoning_effort != "none"
            mandatory_reasoning_retry = False
            if downgraded:
                if debug:
                    print(
                        f"  [debug] finish_reason=length with thinking enabled — "
                        f"retrying once with reasoning_effort='none'"
                    )
                try:
                    response = _do_request("none")
                    content, finish_reason = _extract(response)
                except Exception as disable_exc:
                    if not _is_mandatory_reasoning_error(disable_exc):
                        raise
                    # This endpoint won't allow disabling reasoning at all --
                    # retry once more at the ORIGINAL effort with extra
                    # headroom instead.
                    downgraded = False  # thinking was never actually disabled
                    mandatory_reasoning_retry = True
                    if debug:
                        print(
                            f"  [debug] disable-thinking retry rejected "
                            f"({disable_exc!r}) — retrying at "
                            f"effort={reasoning_effort!r} with "
                            f"+{_MANDATORY_REASONING_RETRY_BUMP} max_tokens"
                        )
                    try:
                        response = _do_request(
                            reasoning_effort, extra_bump=_MANDATORY_REASONING_RETRY_BUMP
                        )
                        bumped_content, bumped_finish_reason = _extract(response)
                    except Exception:
                        # Bumped retry also failed -- keep the original
                        # truncated content rather than crash. Deliberate:
                        # this is a one-shot inline decision and does not
                        # re-enter or consume the outer `for attempt` budget.
                        if debug:
                            print(
                                "  [debug] bumped same-effort retry also "
                                "failed — keeping original truncated content"
                            )
                        content, finish_reason = original_content, original_finish_reason
                    else:
                        if not bumped_content and original_content:
                            # Bumped retry ran but produced nothing usable --
                            # prefer the original partial content over empty.
                            content, finish_reason = original_content, original_finish_reason
                        else:
                            content, finish_reason = bumped_content, bumped_finish_reason

            if return_meta:
                return content, {
                    "downgraded": downgraded,
                    "finish_reason": finish_reason,
                    "mandatory_reasoning_retry": mandatory_reasoning_retry,
                }
            return content
        except Exception as exc:
            is_transient = "rate" in str(exc).lower() or isinstance(exc, _TRANSIENT_EXCEPTIONS)
            if attempt < max_retries - 1 and is_transient:
                if debug:
                    print(f"  [debug] transient error ({exc!r}) — retrying")
                time.sleep(2 ** attempt)
                continue
            raise
    if return_meta:
        return "", {"downgraded": False, "finish_reason": None, "mandatory_reasoning_retry": False}
    return ""
