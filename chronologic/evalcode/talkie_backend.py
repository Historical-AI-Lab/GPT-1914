"""Adapter to run Talkie custom LMs inside benchmark_evaluation.py's HF-mode helpers.

Talkie is a 13B custom GPT-style decoder that is not a HuggingFace model. Three
things make it incompatible with the existing HF eval path:

1. Its forward() returns [B, V] last-position logits only.  We need [B, T, V] for
   per-token log-likelihood scoring of answer continuations.  _TalkieModelAdapter
   re-runs the transformer trunk without the [:, -1, :] slice.

2. It has no model.generate().  _TalkieModelAdapter provides a greedy argmax loop.

3. Its tokenizer is tiktoken, not HuggingFace.  _TalkieTokenizerAdapter wraps it
   to expose __call__(text, return_tensors="pt") and decode(ids, ...) as expected by
   _score_answer_ll_hf and _generate_hf.

4. The IT variant was trained with a chat template.  _TalkieTokenizerAdapter exposes
   format_context(text) which applies the template for IT and is a no-op for base.
   _score_answer_ll_hf and _generate_hf call this hook via getattr duck-typing.

Usage
-----
  model_id may be:
  - A registered name: 'talkie-1930-13b-base', 'talkie-1930-13b-it',
    'talkie-web-13b-base' — resolved via HuggingFace Hub cache.
  - A local directory containing vocab.txt, talkie_style.txt, and one *.ckpt
    or *.pt file — for your own fine-tuned Talkie models.

  Local directory layout for fine-tunes
  --------------------------------------
  /path/to/my-ft/
    vocab.txt          # copy from upstream Talkie HF repo
    talkie_style.txt   # one word: 'base' or 'it'
    final.ckpt         # (or any single *.ckpt / *.pt)
"""

from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

# ---------------------------------------------------------------------------
# Registered model names (must match talkie.config.MODELS keys)
# ---------------------------------------------------------------------------

_REGISTERED_NAMES = frozenset({
    "talkie-1930-13b-base",
    "talkie-1930-13b-it",
    "talkie-web-13b-base",
})

MAX_SEQ_LEN = 2048  # rotary buffers are precomputed for this length


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def is_talkie_model(model_id: str) -> bool:
    """Return True if model_id identifies a Talkie model.

    Accepts registered HF names or a local directory containing vocab.txt.
    """
    if model_id in _REGISTERED_NAMES:
        return True
    p = Path(model_id)
    return p.is_dir() and (p / "vocab.txt").exists()


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _resolve_talkie_paths(model_id: str) -> tuple[Path, Path, str]:
    """Return (checkpoint_path, vocab_path, style) for model_id.

    style is 'base' or 'it'.
    """
    if model_id in _REGISTERED_NAMES:
        from talkie.download import get_model_files
        from talkie.config import MODELS
        ckpt_path, vocab_path = get_model_files(model_id)
        style: str = MODELS[model_id].style
        return Path(ckpt_path), Path(vocab_path), style

    d = Path(model_id)
    if not d.is_dir():
        raise ValueError(
            f"model_id {model_id!r} is not a registered Talkie name and not a local "
            f"directory. Registered names: {sorted(_REGISTERED_NAMES)}"
        )

    vocab_path = d / "vocab.txt"
    if not vocab_path.exists():
        raise FileNotFoundError(f"Expected vocab.txt in {d}")

    style_file = d / "talkie_style.txt"
    if not style_file.exists():
        raise FileNotFoundError(
            f"Expected talkie_style.txt in {d} containing 'base' or 'it'. "
            f"Create it with:  echo base > {style_file}"
        )
    style = style_file.read_text().strip()
    if style not in ("base", "it"):
        raise ValueError(
            f"talkie_style.txt must contain 'base' or 'it', got {style!r}"
        )

    ckpt_files = sorted(d.glob("*.ckpt")) + sorted(d.glob("*.pt"))
    if not ckpt_files:
        raise FileNotFoundError(f"No *.ckpt or *.pt file found in {d}")
    if len(ckpt_files) > 1:
        raise ValueError(
            f"Multiple checkpoint files in {d}: {[f.name for f in ckpt_files]}. "
            f"Remove all but one."
        )
    return ckpt_files[0], vocab_path, style


# ---------------------------------------------------------------------------
# Minimal output types (mimic HF API shape)
# ---------------------------------------------------------------------------

class _LogitsOutput:
    """Minimal stand-in for a HF model output with .logits [B, T, V]."""
    __slots__ = ("logits",)

    def __init__(self, logits: torch.Tensor) -> None:
        self.logits = logits


class _TokenizerOutput:
    """Minimal stand-in for a HF tokenizer call result with .input_ids."""
    __slots__ = ("input_ids",)

    def __init__(self, input_ids: torch.Tensor) -> None:
        self.input_ids = input_ids


# ---------------------------------------------------------------------------
# Tokenizer adapter
# ---------------------------------------------------------------------------

class _TalkieTokenizerAdapter:
    """Wraps a tiktoken Encoding to expose the HF tokenizer interface.

    Specifically provides:
      __call__(text, return_tensors='pt')  → _TokenizerOutput with .input_ids
      decode(ids, skip_special_tokens=True) → str
      format_context(text)                 → str  (IT chat template, or no-op)
    """

    def __init__(
        self,
        enc,
        style: str,
        special_ids: frozenset[int],
    ) -> None:
        self._enc = enc
        self._style = style
        self._special_ids = special_ids

    def __call__(
        self, text: str, return_tensors: str = "pt"
    ) -> _TokenizerOutput:
        ids = self._enc.encode(text, allowed_special="all")
        t = torch.tensor(ids, dtype=torch.long).unsqueeze(0)
        return _TokenizerOutput(t)

    def decode(self, ids, skip_special_tokens: bool = True) -> str:
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        if skip_special_tokens:
            ids = [i for i in ids if i not in self._special_ids]
        return self._enc.decode(ids)

    def format_context(self, text: str) -> str:
        """Wrap text in the IT chat template for talkie-it; pass through for base.

        Called by _score_answer_ll_hf and _generate_hf via getattr duck-typing
        before tokenizing the context/prompt.  The IT model was trained to
        continue after <|assistant|>, so the context must end with that token.
        """
        if self._style == "it":
            from talkie.chat import format_prompt
            return format_prompt(text)
        return text


# ---------------------------------------------------------------------------
# Model adapter
# ---------------------------------------------------------------------------

class _TalkieModelAdapter(nn.Module):
    """Wraps TalkieModel to expose the interface required by benchmark_evaluation.py.

    Contracts honored:
      - next(model.parameters()).device  works (inner is registered as submodule)
      - model(input_ids).logits          returns [B, T, V]  (all positions)
      - model.generate(input_ids, max_new_tokens, do_sample=False)
                                         returns [1, T_prompt + n_new]
    """

    def __init__(self, inner, stop_ids: frozenset[int]) -> None:
        super().__init__()
        self.inner = inner  # nn.Module → auto-registered as submodule
        self._stop_ids = stop_ids

    def _forward_all(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Full-sequence forward returning [B, T, V] logits (float32).

        Identical to TalkieModel.forward but drops the [:, -1, :] slice so
        that all token positions are returned.  Raises if the sequence would
        exceed the precomputed rotary-embedding buffers (2048 tokens).
        """
        m = self.inner
        _, seq_len = input_ids.shape
        if seq_len > MAX_SEQ_LEN:
            raise ValueError(
                f"Input length {seq_len} tokens exceeds Talkie's MAX_SEQ_LEN={MAX_SEQ_LEN}. "
                f"The cos/sin rotary buffers only cover {MAX_SEQ_LEN} positions; longer "
                f"inputs would index out of range and silently return wrong log-probs. "
                f"Shorten the prompt or re-instantiate the model with a larger max_seq_len."
            )
        cos_sin = m.cos[:, :seq_len], m.sin[:, :seq_len]
        x = m.embed(input_ids)
        x = F.rms_norm(x, (x.shape[-1],))
        e_x = x
        for block in m.blocks:
            x = block(e_x, x, cos_sin)
        x = F.rms_norm(x, (x.shape[-1],))
        return F.linear(x, m.lm_head_gain(m.lm_head)).float()  # [B, T, V]

    def forward(self, input_ids: torch.Tensor) -> _LogitsOutput:
        """Return _LogitsOutput with .logits [B, T, V] for _score_answer_ll_hf."""
        return _LogitsOutput(self._forward_all(input_ids))

    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 10,
        do_sample: bool = False,
    ) -> torch.Tensor:
        """Greedy decoding loop for _generate_hf (MCQ mode).

        Returns the full token sequence [1, T_prompt + n_new].  Stops early
        on any special token (EOS, <|end|>, etc.) or when max_new_tokens is
        reached.  No KV cache — each step recomputes the full prefix; fine
        for max_new_tokens=10 (MCQ).
        """
        tokens = input_ids.clone()
        with torch.no_grad():
            for _ in range(max_new_tokens):
                if tokens.shape[1] >= MAX_SEQ_LEN:
                    break
                logits = self._forward_all(tokens)  # [1, T, V]
                next_id = int(logits[0, -1, :].argmax().item())
                next_tensor = torch.tensor(
                    [[next_id]], dtype=torch.long, device=tokens.device
                )
                tokens = torch.cat([tokens, next_tensor], dim=1)
                if next_id in self._stop_ids:
                    break
        return tokens


# ---------------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------------

def load_talkie_model(
    model_id: str,
    device: str | None = None,
    device_map: str | None = None,
) -> tuple[_TalkieModelAdapter, _TalkieTokenizerAdapter]:
    """Load a Talkie model and tokenizer, returning (model_adapter, tokenizer_adapter).

    Args:
        model_id:   Registered name (e.g. 'talkie-1930-13b-base') or local
                    directory path (for fine-tuned models — see module docstring).
        device:     'cuda' or 'cpu'; None for auto-detect.
        device_map: Not supported — raises NotImplementedError.  13B in bfloat16
                    fits on a single 40GB A100 without sharding.
    """
    if device_map is not None:
        raise NotImplementedError(
            "Talkie does not support --device-map. The 13B model in bfloat16 "
            "fits on a single 40GB A100 without multi-GPU sharding. "
            "Drop --device-map to use a single device."
        )

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    ckpt_path, vocab_path, style = _resolve_talkie_paths(model_id)

    from talkie.tokenizer import (
        build_tokenizer,
        IT_VOCAB_SIZE,
        _IT_SPECIAL_TOKENS,
        _BASE_SPECIAL_TOKENS,
    )
    from talkie.model import load_checkpoint

    enc = build_tokenizer(str(vocab_path), style=style)
    special_ids = frozenset(
        (_IT_SPECIAL_TOKENS if style == "it" else _BASE_SPECIAL_TOKENS).values()
    )
    tokenizer = _TalkieTokenizerAdapter(enc, style, special_ids)

    target_vocab = IT_VOCAB_SIZE if style == "it" else None
    raw_model = load_checkpoint(
        str(ckpt_path), torch.device(device), target_vocab_size=target_vocab
    )

    model = _TalkieModelAdapter(raw_model, stop_ids=special_ids)
    return model, tokenizer
