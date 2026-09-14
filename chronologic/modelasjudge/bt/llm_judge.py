"""bt/llm_judge.py — wraps openrouter_client into a bt.collect judge_call.

Only this module (plus the CLI that calls it) ever touches the network.
Everything else in bt/ takes an injected judge_call callable.
"""

from __future__ import annotations

import sys
from pathlib import Path

MODELASJUDGE_DIR = Path(__file__).resolve().parent.parent
if str(MODELASJUDGE_DIR) not in sys.path:
    sys.path.insert(0, str(MODELASJUDGE_DIR))

from openrouter_client import is_openrouter_model, make_openrouter_client  # noqa: E402

_TOKEN_CAPS = {"none": 50, "low": 1024, "medium": 4096, "high": 16000}


def make_llm_judge_call(judge_model: str, reasoning_effort: str = "medium", *,
                        openrouter_cred=None, debug: bool = False):
    """Return judge_call(comparison, system, user) -> raw text for a real judge."""
    if not is_openrouter_model(judge_model):
        raise ValueError(
            f"bt_context_scoring only supports OpenRouter judge models currently; "
            f"got {judge_model!r}. See openrouter_client.OPENROUTER_PREFIXES."
        )
    from openrouter_client import call_openrouter_chat

    client = make_openrouter_client(openrouter_cred)
    max_tokens = _TOKEN_CAPS[reasoning_effort]

    def judge_call(comparison, system, user):
        return call_openrouter_chat(
            client, judge_model, user, system_content=system,
            max_tokens=max_tokens, debug=debug, reasoning_effort=reasoning_effort,
        )

    return judge_call
