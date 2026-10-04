#!/usr/bin/env python3
"""
Compatibility shim for the batch pipeline's distractor generator.

This module used to be a fork of connectors/distractor_generator.py that added
category-aware prompting (connector-term guidance and an explicit length spec).
That behavior now lives in the original module, so the two have been unified and
this file only re-exports it.

New code should import connectors/distractor_generator.py directly. This shim
exists because batched_cloze_questions.py, show_prompt_examples.py and the batch
test suite still import `distractor_generator_wcats`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "connectors"))

from distractor_generator import (  # noqa: F401
    ANACHRONISTIC_PROMPT,
    BERT_AVAILABLE,
    BERT_MODEL_NAME,
    CONNECTOR_TERMS,
    MAX_RETRIES,
    MAX_TOKENS,
    NEGATION_SENTENCE_PROMPT,
    PRIMARY_MODEL,
    SECONDARY_MODEL,
    assign_metadataless_variant,
    call_openrouter_model,
    format_length_spec,
    generate_anachronistic,
    generate_distractors,
    generate_negation,
    get_client,
    get_nsp_probability,
    get_term_spec,
    model_slug,
    normalize_distractor_format,
    parse_distractor_type,
    rank_candidates_by_nsp,
)
