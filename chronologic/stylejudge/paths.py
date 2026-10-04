"""Filesystem roots for the style judge.

Two things vary between machines: where the dating corpus lives, and where the
two frozen DeBERTa instruments live. Both are resolved here, so that no other
module has to hardcode a path under one particular home directory.

CHRONOLOGIC_DATA
    Root of the dating corpus -- calibration passages, the scored reference
    distributions, and the per-candidate style intermediates. Set the
    environment variable of the same name to relocate it:

        export CHRONOLOGIC_DATA=/scratch/chronologic-dating-corpus

    When unset it falls back to ~/workdata/chronologic-dating-corpus, which is
    the layout the benchmark was developed under, so existing checkouts keep
    working with no environment set at all.

The instruments
    `resolve_model_dir()` prefers a local directory and falls back to the
    HuggingFace Hub, so a fresh clone can score without first hunting down
    1.7 GB of weights. Both instruments are DeBERTa-v3-large fine-tunes:
    the authenticity detector is a single-output regression head, the date
    predictor a 36-way ordinal softmax over date bins.
"""

import os
from pathlib import Path

# --- corpus root -----------------------------------------------------------

DEFAULT_CHRONOLOGIC_DATA = Path.home() / "workdata" / "chronologic-dating-corpus"


def data_root() -> Path:
    """Corpus root, honouring $CHRONOLOGIC_DATA."""
    env = os.environ.get("CHRONOLOGIC_DATA")
    return Path(env).expanduser() if env else DEFAULT_CHRONOLOGIC_DATA


CHRONOLOGIC_DATA = data_root()

# --- the two frozen instruments --------------------------------------------

HF_AUTHENTICITY_REPO = "chronologic/chronologic-authenticity-deberta"
HF_DATE_REPO = "chronologic/chronologic-date-deberta"


def resolve_model_dir(local_dir, hf_repo, what="model"):
    """Return a directory holding a DeBERTa checkpoint.

    Uses `local_dir` when it exists; otherwise downloads `hf_repo` from the
    HuggingFace Hub and returns the cache directory. The download is cached by
    huggingface_hub, so the cost is paid once per machine.

    Raising rather than returning a missing path keeps the failure legible: a
    stranger who has neither the local checkout nor huggingface_hub installed
    gets told which of the two to fix.
    """
    local_dir = Path(local_dir)
    if local_dir.exists():
        return local_dir
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:                              # pragma: no cover
        raise FileNotFoundError(
            f"{what} not found at {local_dir}, and huggingface_hub is not "
            f"installed to fetch it from {hf_repo}. Either install it "
            f"(pip install huggingface_hub) or point the corresponding "
            f"--*-model-dir / --*-run-dir flag at a local checkout."
        ) from exc
    return Path(snapshot_download(repo_id=hf_repo))
