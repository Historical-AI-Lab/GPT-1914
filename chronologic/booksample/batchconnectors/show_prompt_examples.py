#!/usr/bin/env python3
"""
Generate sample anachronistic-distractor prompts for each connector category
and write them to prompt_examples.txt.

Not part of the formal test suite — just a quick way to inspect the prompts
that each category produces, using real passages from the cloze questions file.

Usage:
    python show_prompt_examples.py [CLOZE_FILE]

    Defaults to process_files/32044019979996_clozequestions.jsonl
"""

import json
import sys
from pathlib import Path

# Add parent dirs so imports resolve
sys.path.insert(0, str(Path(__file__).parent))
CONNECTORS_DIR = str(Path(__file__).parent.parent / "connectors")
if CONNECTORS_DIR not in sys.path:
    sys.path.append(CONNECTORS_DIR)

from distractor_generator_wcats import (
    ANACHRONISTIC_PROMPT,
    CONNECTOR_TERMS,
    format_length_spec,
    get_term_spec,
)

DEFAULT_CLOZE_FILE = Path(__file__).parent / "process_files" / "32044019979996_clozequestions.jsonl"
OUTPUT_FILE = Path(__file__).parent / "prompt_examples.txt"


def main():
    cloze_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CLOZE_FILE
    if not cloze_path.exists():
        print(f"Error: {cloze_path} not found")
        sys.exit(1)

    # Load all questions, keyed by category (strip 'cloze_' prefix)
    by_category = {}
    with open(cloze_path) as f:
        for line in f:
            rec = json.loads(line)
            cat = rec['question_category'].removeprefix('cloze_')
            if cat not in by_category:
                by_category[cat] = rec

    lines = []

    for cat in sorted(CONNECTOR_TERMS.keys()):
        rec = by_category.get(cat)
        if rec is None:
            lines.append(f"{'=' * 72}")
            lines.append(f"CATEGORY: {cat}")
            lines.append(f"  (no example found in {cloze_path.name})")
            lines.append("")
            continue

        # Reconstruct the pieces that generate_anachronistic would use
        ground_truth = rec['answer_strings'][0]
        gt_words = len(ground_truth.split())
        is_clause = cat.endswith('clause')

        metadata_prefix = rec['metadata_frame']
        # The main_question field contains "passage\n\nprompt"
        main_q = rec['main_question']

        question_text = f"{metadata_prefix}\n\n{main_q}"

        length_spec = format_length_spec(gt_words, is_clause)
        term_spec = get_term_spec(cat)

        full_prompt = ANACHRONISTIC_PROMPT.format(
            length_spec=length_spec,
            term_spec=term_spec,
            question_text=question_text,
        )

        lines.append("=" * 72)
        lines.append(f"CATEGORY: {cat}")
        lines.append(f"  is_clause: {is_clause}")
        lines.append(f"  ground_truth ({gt_words} words): {ground_truth[:120]}...")
        lines.append(f"  length_spec: {length_spec}")
        lines.append(f"  term_spec: {term_spec}")
        lines.append("-" * 72)
        lines.append("FULL PROMPT:")
        lines.append(full_prompt)
        lines.append("")

    output = "\n".join(lines)

    with open(OUTPUT_FILE, "w") as f:
        f.write(output)

    print(f"Wrote {len(CONNECTOR_TERMS)} category examples to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
