"""
Unit tests for openrouter_client._build_extra_body and the length-retry path
of call_openrouter_chat. No network calls.
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, call as mock_call

sys.path.insert(0, str(Path(__file__).parent.parent))
from openrouter_client import _build_extra_body, call_openrouter_chat


# ---------------------------------------------------------------------------
# _build_extra_body
# ---------------------------------------------------------------------------

class TestBuildExtraBody:

    def test_anthropic_medium_effort(self):
        body = _build_extra_body("anthropic/claude-opus-4-7", "medium", 4096)
        # verbosity is the live knob; reasoning.effort must NOT appear
        assert body["verbosity"] == "medium"
        assert "effort" not in body.get("reasoning", {})
        # thinking budget = (4096 + 2048) - 1024 = 5120
        assert body["reasoning"]["max_tokens"] == 5120

    def test_anthropic_none_effort(self):
        body = _build_extra_body("anthropic/claude-sonnet-4-6", "none", 50)
        # thinking off; Anthropic gets verbosity=low so Opus 4.7 adaptive effort is minimised
        assert body.get("verbosity") == "low"
        assert body["chat_template_kwargs"] == {"enable_thinking": False}
        # no reasoning.max_tokens when thinking is disabled
        assert "max_tokens" not in body.get("reasoning", {})

    def test_anthropic_low_effort(self):
        body = _build_extra_body("anthropic/claude-sonnet-4-6", "low", 1024)
        assert body["verbosity"] == "low"
        assert "effort" not in body.get("reasoning", {})
        # (1024 + 2048) - 1024 = 2048
        assert body["reasoning"]["max_tokens"] == 2048

    def test_anthropic_high_effort(self):
        body = _build_extra_body("anthropic/claude-opus-4-7", "high", 16000)
        assert body["verbosity"] == "high"
        # (16000 + 2048) - 1024 = 17024
        assert body["reasoning"]["max_tokens"] == 17024
        assert "verbosity" not in body.get("reasoning", {})

    def test_qwen_high_effort(self):
        body = _build_extra_body("qwen/qwen3-72b-instruct", "high", 4096)
        # non-Anthropic: reasoning.effort is the live knob, verbosity must not appear
        assert body["reasoning"]["effort"] == "high"
        assert "verbosity" not in body
        assert body["reasoning"]["max_tokens"] == 5120

    def test_qwen_none_effort(self):
        body = _build_extra_body("qwen/qwen3-72b-instruct", "none", 50)
        assert body["reasoning"]["effort"] == "none"
        assert body["chat_template_kwargs"] == {"enable_thinking": False}
        assert "verbosity" not in body
        assert "max_tokens" not in body.get("reasoning", {})

    def test_meta_llama_medium_effort(self):
        body = _build_extra_body("meta-llama/llama-4-maverick", "medium", 2048)
        assert body["reasoning"]["effort"] == "medium"
        assert "verbosity" not in body
        # (2048 + 2048) - 1024 = 3072
        assert body["reasoning"]["max_tokens"] == 3072

    def test_google_none_effort(self):
        body = _build_extra_body("google/gemini-2.5-pro", "none", 200)
        assert body["reasoning"]["effort"] == "none"
        assert body["chat_template_kwargs"] == {"enable_thinking": False}


# ---------------------------------------------------------------------------
# call_openrouter_chat — length-retry behaviour
# ---------------------------------------------------------------------------

def _make_mock_choice(content, finish_reason):
    choice = MagicMock()
    choice.finish_reason = finish_reason
    choice.message.content = content
    return choice


def _make_mock_response(content, finish_reason):
    response = MagicMock()
    response.choices = [_make_mock_choice(content, finish_reason)]
    return response


class TestLengthRetry:

    def _make_client(self, responses):
        """Return a mock client whose completions.create returns responses in order."""
        client = MagicMock()
        client.chat.completions.create.side_effect = responses
        return client

    def test_no_retry_when_stop(self):
        client = self._make_client([
            _make_mock_response('{"question fit": "A"}', "stop"),
        ])
        result = call_openrouter_chat(
            client, "anthropic/claude-opus-4-7", "Q", reasoning_effort="medium"
        )
        assert result == '{"question fit": "A"}'
        assert client.chat.completions.create.call_count == 1

    def test_length_triggers_retry_with_no_thinking(self):
        """A length finish_reason when thinking is on should cause one retry without thinking."""
        client = self._make_client([
            _make_mock_response("", "length"),           # first call: truncated
            _make_mock_response('{"question fit": "B"}', "stop"),  # retry: success
        ])
        result = call_openrouter_chat(
            client, "anthropic/claude-opus-4-7", "Q", reasoning_effort="medium"
        )
        assert result == '{"question fit": "B"}'
        assert client.chat.completions.create.call_count == 2

        # Verify the retry used effort="none" shaping: verbosity should be "low"
        # (Anthropic + effort==none), not "medium".
        retry_kwargs = client.chat.completions.create.call_args_list[1]
        extra_body = retry_kwargs[1]["extra_body"]
        assert extra_body.get("verbosity") == "low"
        assert "effort" not in extra_body.get("reasoning", {})

    def test_no_length_retry_when_effort_none(self):
        """length with effort=="none" should NOT retry (thinking was already off)."""
        client = self._make_client([
            _make_mock_response("", "length"),
        ])
        result = call_openrouter_chat(
            client, "anthropic/claude-opus-4-7", "Q", reasoning_effort="none"
        )
        assert result == ""
        assert client.chat.completions.create.call_count == 1

    def test_length_retry_non_anthropic(self):
        """length-retry also fires for non-Anthropic models (Qwen, etc.)."""
        client = self._make_client([
            _make_mock_response("", "length"),
            _make_mock_response('{"question fit": "C"}', "stop"),
        ])
        result = call_openrouter_chat(
            client, "qwen/qwen3-72b-instruct", "Q", reasoning_effort="high"
        )
        assert result == '{"question fit": "C"}'
        assert client.chat.completions.create.call_count == 2

    def test_max_tokens_bump_applied(self):
        """Wire max_tokens should be caller value + 2048 when effort != none."""
        client = self._make_client([
            _make_mock_response("answer", "stop"),
        ])
        call_openrouter_chat(
            client, "anthropic/claude-sonnet-4-6", "Q",
            max_tokens=1024, reasoning_effort="low",
        )
        wire_max = client.chat.completions.create.call_args[1]["max_tokens"]
        assert wire_max == 1024 + 2048

    def test_no_max_tokens_bump_when_effort_none(self):
        """Wire max_tokens should equal the caller value when effort == none."""
        client = self._make_client([
            _make_mock_response("answer", "stop"),
        ])
        call_openrouter_chat(
            client, "anthropic/claude-opus-4-7", "Q",
            max_tokens=50, reasoning_effort="none",
        )
        wire_max = client.chat.completions.create.call_args[1]["max_tokens"]
        assert wire_max == 50
