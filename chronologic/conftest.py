"""Root pytest configuration.

Two things have to be arranged before any test module imports cleanly from the
repository root.

First, there are ten directories named `tests/`, each with an `__init__.py`
(modelasjudge/, stylejudge/, evalcode/, bertclassify/, augment/, memorize/,
booksample/connectors/, booksample/batchconnectors/, booksample/summary/,
modelasjudge/erroranalysis/). Under pytest's default "prepend" import mode they
all claim the top-level package name `tests`, the first one wins, and every
later suite fails collection with `No module named 'tests.test_...'`. Selecting
importlib import mode (see pytest.ini) gives each module a unique internal name
and removes the collision.

Second, importlib mode deliberately does *not* put a test file's directory on
sys.path, and these suites import their siblings by bare name -- `import
naming`, `import typicality`, `from bt import artifacts`. So we add each source
directory here. Adding the parent of every `tests/` directory keeps this in step
with the tree automatically, rather than hardcoding a list that will drift.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Directories that are never worth walking: vendored environments, the frozen
# collaborator fork, superseded code kept only for history, and the bulk data
# trees. Pruning the data trees matters for speed as much as correctness --
# bt_artifacts/cache alone holds ~75,700 files, and walking it took most of the
# 1.3s this import used to cost.
_PRUNE = {".git", "__pycache__", ".pytest_cache", "qlora-env",
          "shubham", "deprecated", "node_modules",
          "cache", "bt_artifacts", "scored_answers", "generated_answers",
          "sample1000books", "averybooks", "benchmarkbooks", "edgebooks",
          "model_output", "large_tok196", "baseline", "authentic", "imitation"}


def _source_dirs():
    """Every directory that owns a `tests/` subdirectory, plus the root."""
    found = [ROOT]
    stack = [ROOT]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except (PermissionError, OSError):
            continue
        for entry in entries:
            if not entry.is_dir() or entry.name in _PRUNE:
                continue
            if entry.name == "tests":
                found.append(current)
            else:
                stack.append(entry)
    return found


for _path in _source_dirs():
    _as_str = str(_path)
    if _as_str not in sys.path:
        sys.path.insert(0, _as_str)
