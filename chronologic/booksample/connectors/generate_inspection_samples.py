#!/usr/bin/env python3
"""
Generate samples for user inspection of cloze question pipeline.

This script produces output for three inspection items from the specification:
  0. Metadata prefix samples from existing metadata files
  2b. Connector parsing on real-world text (~25 cases)
  6. Negation distractor samples

Usage:
    python generate_inspection_samples.py metadata
    python generate_inspection_samples.py connectors path/to/textfile.txt [--limit 25]
    python generate_inspection_samples.py negations [--num 5]
    python generate_inspection_samples.py all path/to/textfile.txt
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from make_cloze_questions import (
    a_or_an,
    build_metadata_prefix,
    tokenize_and_tag_sentences,
    parse_connector_patterns,
    TAG_DESCRIPTIONS
)

# Categories are the keys of TAG_DESCRIPTIONS
CONNECTOR_CATEGORIES = list(TAG_DESCRIPTIONS.keys())


def generate_metadata_samples():
    """
    Item 0: Generate metadata prefix samples from existing metadata files.
    """
    print("=" * 70)
    print("METADATA PREFIX SAMPLES (Item 0)")
    print("=" * 70)
    print()

    # Find existing metadata files
    character_dir = Path(__file__).parent.parent / "character" / "process_files"
    metadata_files = list(character_dir.glob("*_metadata.json"))

    if not metadata_files:
        print(f"No metadata files found in {character_dir}")
        print("Creating synthetic examples instead...")
        print()

        # Synthetic examples to test a/an handling
        synthetic_metadata = [
            {
                "source_title": "The Mystic Gate",
                "source_author": "Annie Besant",
                "source_date": 1901,
                "author_nationality": "British",
                "genre": "religious treatise",
                "author_birth": 1847,
                "author_profession": "theosophist",
                "source_htid": "hvd.example1"
            },
            {
                "source_title": "Adventures in the Wild",
                "source_author": "Patrick O'Brien",
                "source_date": 1892,
                "author_nationality": "Irish",
                "genre": "adventure story",
                "author_birth": 1855,
                "author_profession": "explorer",
                "source_htid": "hvd.example2"
            },
            {
                "source_title": "The Industrial Revolution",
                "source_author": "Edward Thompson",
                "source_date": 1905,
                "author_nationality": "English",
                "genre": "historical analysis",
                "author_birth": 1860,
                "author_profession": "historian",
                "source_htid": "hvd.example3"
            },
            {
                "source_title": "An Unconventional Life",
                "source_author": "Oscar Wilde",
                "source_date": 1895,
                "author_nationality": "Irish",
                "genre": "autobiography",
                "author_birth": 1854,
                "author_profession": "author",
                "source_htid": "hvd.example4"
            },
            {
                "source_title": "The American Frontier",
                "source_author": "Abraham Lincoln Jr.",
                "source_date": 1888,
                "author_nationality": "American",
                "genre": "novel",
                "author_birth": 1850,
                "author_profession": "novelist",
                "source_htid": "hvd.example5"
            },
        ]

        for i, meta in enumerate(synthetic_metadata, 1):
            prefix = build_metadata_prefix(meta)
            print(f"Sample {i}:")
            print(f"  Input: {json.dumps(meta, indent=4)}")
            print(f"  Output: {prefix}")
            print()

            # Show a/an decisions
            genre_article = a_or_an(meta['genre'])
            nat_article = a_or_an(meta['author_nationality'])
            print(f"  a/an decisions: '{genre_article} {meta['genre']}', '{nat_article} {meta['author_nationality']}'")
            print()

        return

    print(f"Found {len(metadata_files)} metadata files in {character_dir}")
    print()

    for meta_file in metadata_files[:5]:  # Show up to 5
        try:
            with open(meta_file) as f:
                meta = json.load(f)

            # Add author_profession if missing (not in old files)
            if 'author_profession' not in meta:
                meta['author_profession'] = 'writer'

            prefix = build_metadata_prefix(meta)

            print(f"File: {meta_file.name}")
            print(f"  Title: {meta.get('source_title', 'N/A')}")
            print(f"  Author: {meta.get('source_author', 'N/A')}")
            print(f"  Genre: {meta.get('genre', 'N/A')}")
            print(f"  Nationality: {meta.get('author_nationality', 'N/A')}")
            print(f"  Profession: {meta.get('author_profession', 'N/A')}")
            print()
            print(f"  Generated prefix:")
            print(f"    {prefix}")
            print()

        except Exception as e:
            print(f"Error reading {meta_file.name}: {e}")
            print()


def generate_connector_samples(text_path: str, limit: int = 25):
    """
    Item 2b: Parse real-world text and show connector cases for inspection.
    """
    print("=" * 70)
    print(f"CONNECTOR PARSING SAMPLES (Item 2b)")
    print(f"File: {text_path}")
    print("=" * 70)
    print()

    # Read text file
    try:
        with open(text_path) as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {text_path}")
        return

    # Tokenize and tag
    print("Parsing text for connector patterns...")
    print()

    tagged_sentences = tokenize_and_tag_sentences(text)

    # Collect cases by category
    cases_by_category = {cat: [] for cat in CONNECTOR_CATEGORIES}

    for entry in tagged_sentences:
        sentence = entry['sentence']
        for cat in CONNECTOR_CATEGORIES:
            if cat in entry:
                connector, position = entry[cat]
                cases_by_category[cat].append({
                    'sentence': sentence,
                    'connector': connector,
                    'position': position,
                    'index': entry['index']
                })

    # Print results
    total_cases = sum(len(cases) for cases in cases_by_category.values())
    print(f"Total connector cases found: {total_cases}")
    print()

    shown = 0
    for cat in CONNECTOR_CATEGORIES:
        cases = cases_by_category[cat]
        if cases:
            print(f"\n{cat.upper()} ({len(cases)} cases):")
            print(f"  Mask description: {TAG_DESCRIPTIONS[cat]}")
            print("-" * 60)

            for case in cases[:limit // len(CONNECTOR_CATEGORIES) + 1]:
                if shown >= limit:
                    break
                print(f"  [{case['index']}] Connector: '{case['connector']}' at position {case['position']}")
                print(f"      Sentence: {case['sentence'][:100]}...")
                if len(case['sentence']) > 100:
                    print(f"                {case['sentence'][100:200]}...")
                print()
                shown += 1

    print()
    print(f"Showing {shown} of {total_cases} total cases (limit: {limit})")

    # Summary
    print()
    print("SUMMARY BY CATEGORY:")
    print("-" * 40)
    for cat in CONNECTOR_CATEGORIES:
        count = len(cases_by_category[cat])
        if count > 0:
            print(f"  {cat}: {count} cases")


def generate_negation_samples(num_samples: int = 5):
    """
    Item 6: Generate sample negations for inspection.

    This requires LLM calls, so we'll show the prompts and some example inputs.
    """
    print("=" * 70)
    print("NEGATION DISTRACTOR SAMPLES (Item 6)")
    print("=" * 70)
    print()

    from distractor_generator import (
        NEGATION_SENTENCE_PROMPT,
        NEGATION_CLAUSE_PROMPT,
        generate_negation
    )

    # Sample sentences for testing
    sample_sentences = [
        ("But the king refused to listen to their pleas.", False),
        ("because the hour was late", True),
        ("However, the merchants continued trading despite the war.", False),
        ("although he knew the dangers involved", True),
        ("Therefore, the council voted to proceed with the expedition.", False),
    ]

    print("NEGATION PROMPTS:")
    print()
    print("For SENTENCES:")
    print("-" * 50)
    print(NEGATION_SENTENCE_PROMPT[:500] + "...")
    print()
    print("For CLAUSES:")
    print("-" * 50)
    print(NEGATION_CLAUSE_PROMPT[:500] + "...")
    print()

    print("=" * 70)
    print("SAMPLE INPUTS (would generate negations via LLM):")
    print("=" * 70)
    print()

    for sentence, is_clause in sample_sentences[:num_samples]:
        sentence_type = "CLAUSE" if is_clause else "SENTENCE"
        print(f"Input ({sentence_type}):")
        print(f"  \"{sentence}\"")
        print()
        print(f"  Expected negation characteristics:")
        if is_clause:
            print(f"    - Should NOT start with capital letter")
            print(f"    - Should NOT end with period")
        else:
            print(f"    - Should start with capital letter")
            print(f"    - Should end with period")
        print(f"    - Should express opposite meaning")
        print(f"    - Should be similar length (0.5x to 2x)")
        print()

    # Try to generate actual negations if Ollama is available
    print("=" * 70)
    print("ATTEMPTING LIVE NEGATION GENERATION (requires Ollama):")
    print("=" * 70)
    print()

    try:
        for sentence, is_clause in sample_sentences[:3]:
            sentence_type = "CLAUSE" if is_clause else "SENTENCE"
            print(f"Generating negation for ({sentence_type}): \"{sentence}\"")

            negation = generate_negation(sentence, is_clause)

            if negation:
                print(f"  Result: \"{negation}\"")

                # Validate characteristics
                issues = []
                if is_clause:
                    if negation[0].isupper():
                        issues.append("starts with capital (should not for clause)")
                    if negation.endswith('.'):
                        issues.append("ends with period (should not for clause)")
                else:
                    if not negation[0].isupper():
                        issues.append("doesn't start with capital (should for sentence)")
                    if not negation.endswith('.'):
                        issues.append("doesn't end with period (should for sentence)")

                if issues:
                    print(f"  Issues: {', '.join(issues)}")
                else:
                    print(f"  Validation: PASS")
            else:
                print(f"  Result: FAILED TO GENERATE")
            print()

    except Exception as e:
        print(f"Could not generate live negations: {e}")
        print("This is expected if Ollama is not running.")


def generate_bert_ranking_samples(textfile: str, num_candidates: int = 10):
    """
    Item 7: Show BERT NSP ranking of distractor candidates for inspection.
    """
    print("=" * 70)
    print("BERT NSP RANKING SAMPLES (Item 7)")
    print("=" * 70)
    print()

    try:
        from distractor_generator import rank_candidates_by_nsp, BERT_AVAILABLE
    except ImportError as e:
        print(f"Could not import distractor_generator: {e}")
        return

    if not BERT_AVAILABLE:
        print("BERT not available (transformers/torch not installed)")
        return

    # Read text file and find some candidate sentences
    try:
        with open(textfile) as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {textfile}")
        return

    # Get tagged sentences
    tagged_sentences = tokenize_and_tag_sentences(text)

    # Find a contrast sentence to use as example
    target_entry = None
    target_idx = None
    for entry in tagged_sentences:
        if 'contrastsentence' in entry and entry['index'] > 10:
            target_entry = entry
            target_idx = entry['index']
            break

    if not target_entry:
        print("No suitable contrast sentence found in text")
        return

    # Build a passage around this sentence
    from make_cloze_questions import build_passage

    passage_data = build_passage(tagged_sentences, target_idx, 'contrastsentence')

    if not passage_data:
        print("Could not build passage (not enough preceding context)")
        return

    print(f"Target sentence (index {target_idx}):")
    print(f"  {target_entry['sentence'][:100]}...")
    print()
    print(f"Ground truth: {passage_data['ground_truth']}")
    print()
    print(f"Passage with mask:")
    print(f"  {passage_data['passage'][:200]}...")
    print()

    # Collect candidate sentences from the same category (same_book distractors)
    from make_cloze_questions import get_distractor_candidates

    candidates = get_distractor_candidates(
        tagged_sentences, 'contrastsentence', target_idx, passage_data['ground_truth']
    )

    print(f"Found {len(candidates)} unique contrastsentence candidates (excluding ground truth)")

    # Limit to requested number
    if len(candidates) > num_candidates:
        candidates = candidates[:num_candidates]

    print(f"Ranking {len(candidates)} candidate sentences by BERT NSP probability...")
    print()

    # Rank with verbose output
    ranked = rank_candidates_by_nsp(
        passage_data['passage'],
        passage_data['mask_string'],
        candidates,
        n=len(candidates),  # Return all to see full ranking
        verbose=True
    )

    print("Top 3 ranked candidates:")
    for i, cand in enumerate(ranked[:3]):
        print(f"  {i+1}. {cand[:80]}...")


def main():
    parser = argparse.ArgumentParser(
        description="Generate samples for user inspection of cloze question pipeline"
    )

    subparsers = parser.add_subparsers(dest='command', help='Inspection type')

    # Metadata subcommand
    meta_parser = subparsers.add_parser('metadata', help='Generate metadata prefix samples (Item 0)')

    # Connectors subcommand
    conn_parser = subparsers.add_parser('connectors', help='Parse text for connectors (Item 2b)')
    conn_parser.add_argument('textfile', help='Path to text file to parse')
    conn_parser.add_argument('--limit', type=int, default=25, help='Max cases to show')

    # Negations subcommand
    neg_parser = subparsers.add_parser('negations', help='Generate negation samples (Item 6)')
    neg_parser.add_argument('--num', type=int, default=5, help='Number of samples')

    # BERT ranking subcommand
    bert_parser = subparsers.add_parser('bert', help='Show BERT NSP ranking (Item 7)')
    bert_parser.add_argument('textfile', help='Path to text file for candidates')
    bert_parser.add_argument('--num-candidates', type=int, default=10, help='Number of candidates to rank')

    # All subcommand
    all_parser = subparsers.add_parser('all', help='Run all inspections')
    all_parser.add_argument('textfile', help='Path to text file for connector parsing')

    args = parser.parse_args()

    if args.command == 'metadata':
        generate_metadata_samples()
    elif args.command == 'connectors':
        generate_connector_samples(args.textfile, args.limit)
    elif args.command == 'negations':
        generate_negation_samples(args.num)
    elif args.command == 'bert':
        generate_bert_ranking_samples(args.textfile, args.num_candidates)
    elif args.command == 'all':
        generate_metadata_samples()
        print("\n" + "=" * 70 + "\n")
        generate_connector_samples(args.textfile)
        print("\n" + "=" * 70 + "\n")
        generate_negation_samples()
        print("\n" + "=" * 70 + "\n")
        generate_bert_ranking_samples(args.textfile)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
