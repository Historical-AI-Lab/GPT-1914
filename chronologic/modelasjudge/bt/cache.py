"""bt/cache.py — content-addressed cache for judge calls.

Keyed on sha256 of (judge model, reasoning effort, attempt index, repeat
index, system prompt, user prompt), so reruns and question subsets never
re-bill.  The attempt index is part of the key because retries re-ask the
same comparison with a suffix and must be cached independently —
otherwise a cached unparseable reply would make every retry fail
identically.

The repeat index is part of the key for the same reason in reverse: the
prompt for repeat 1 of an ordered pair is byte-identical to repeat 0, so
without it `--repeats N` would serve one call back N times.  That would
inflate the binomial n without adding an observation, understating the
standard error and overstating separation — the opposite of what repeats
are for.  Repeats vary only through the judge's own sampling temperature,
so they must each reach the judge.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


class PromptCache:
    def __init__(self, cache_dir: Path | str):
        self.cache_dir = Path(cache_dir)

    @staticmethod
    def key(judge_model: str, effort: str, attempt: int,
            system: str, user: str, repeat: int = 0) -> str:
        payload = "\x1f".join([judge_model, effort, str(attempt), str(repeat),
                               system, user])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _path(self, key: str) -> Path:
        return self.cache_dir / key[:2] / f"{key}.json"

    def get(self, key: str) -> str | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))["raw"]
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def put(self, key: str, raw: str, *, judge_model: str = "",
            effort: str = "", attempt: int = 0) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"model": judge_model, "effort": effort, "attempt": attempt,
                  "raw": raw, "ts": time.time()}
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(record), encoding="utf-8")
        tmp.replace(path)
