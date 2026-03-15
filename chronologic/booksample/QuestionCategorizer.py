#!/usr/bin/env python3
"""
QuestionCategorizer.py

Aggregates benchmark questions from pipeline subfolders into a single
chronologic_en_1875.jsonl file, adding reasoning_type, frame_type, and
answer_length fields while normalizing irregular answer_types.

Usage:
    python QuestionCategorizer.py <subfolder> [--start-line N]

Subfolders: connectors, batchconnectors, character, knowledge, manual, poetry, summary
"""

import argparse
import glob
import json
import os
import re
import sys
import textwrap

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'chronologic_en_1875.jsonl')

ALLOWABLE_ANSWER_TYPES = {
    'ground_truth', 'same_book', 'manual', 'negation',
    'anachronistic_gpt-oss:20b', 'anachronistic_metadataless_mistral-small:24b',
    'anachronistic_mistral-small:24b', 'anachronistic_metadataless_gpt-oss:20b',
    'same_character', 'manual_negation',
    'anachronistic_gpt-5.2', 'anachronistic_wikipedia', 'anachronistic_sonnet-4.6',
    'anachronistic_distort1_gpt-oss:20b', 'anachronistic_distort2_mistral-small:24b',
    'manual_anachronistic_mistral-small:24b', 'anachronistic_older',
    'anachronistic_qwen2.5:7b-instruct', 'manual_anachronistic_gpt-oss:20b',
    'manual_anachronistic_metadataless_mistral-small:24b',
    'anachronistic_google', 'manual_anachronistic_distort2_mistral-small:24b',
    'anachronistic_manual',
    'manual_anachronistic_metadataless_gpt-oss:20b',
}

REASONING_TO_FRAME = {
    'knowledge': 'world_context',
    'refusal': 'world_context',
    'inference': 'world_context',
    'character_modeling': 'book_context',
    'constrained_generation': 'book_context',
    'topic_sentence': 'book_context',
    'phrase_cloze': 'passage_context',
    'sentence_cloze': 'passage_context',
}

SHORT_ANSWER_MEDIAN_MAX = 29
SHORT_ANSWER_MAX_MAX = 75
SENTENCE_PLUS_MEDIAN_MIN = 30

FILE_PATTERNS = {
    'connectors': '*_clozequestions.jsonl',
    'batchconnectors': '*_clozequestions.jsonl',
    'character': '*_questions.jsonl',
    'knowledge': '*_knowledgequestions.jsonl',
    'manual': '*_manualquestions.jsonl',
    'poetry': '*_poetryquestions.jsonl',
    'summary': '*_topicquestions.jsonl',
}

KNOWN_ANSWER_TYPE_DATES = {
    'britannica1911ab': 1911,
    'britannica1875ab': 1875,
    'gilman1910': 1910,
    'henryjames1880s': 1880,
    'ruskin1865': 1865,
    'iaappleton': 1897,
}

# For the manual subfolder: categories that map automatically to reasoning_type
MANUAL_AUTO_MAP = {
    'attribution': 'knowledge',
    'refusal': 'refusal',
    'inference': 'inference',
    'parallax': 'constrained_generation',
    'constrained_generation': 'constrained_generation',
    'topic_sentence': 'topic_sentence',
    'contrastclause': 'phrase_cloze',
}

# Categories requiring interactive inspection in the manual subfolder
MANUAL_INTERACTIVE_CATS = {'textbook', 'handcrafted', 'knowledge'}

REQUIRED_FIELDS = [
    'metadata_frame', 'main_question', 'question_category', 'question_process',
    'source_htid', 'source_title', 'source_author', 'source_date',
    'source_genre', 'author_nationality', 'author_profession',
    'answer_strings', 'answer_types', 'answer_probabilities',
]

COLUMBIAN_FRAME = ("The following question asks for information from an "
                   "American encyclopedia published in 1897; your answer "
                   "should reflect the state of knowledge and style of "
                   "exposition current at the time.")


class UserQuit(Exception):
    pass


# ---------------------------------------------------------------------------
# Metadata loading
# ---------------------------------------------------------------------------

_metadata_df = None
_barcode_to_date = None


def load_metadata():
    global _metadata_df, _barcode_to_date
    if _metadata_df is not None:
        return _metadata_df, _barcode_to_date

    csv_path = os.path.join(SCRIPT_DIR, 'primary_metadata.csv')
    _metadata_df = pd.read_csv(csv_path)
    _barcode_to_date = {}

    for _, row in _metadata_df.iterrows():
        barcode = str(row['barcode_src'])
        date_val = row['firstpub']
        if pd.isna(date_val):
            date_int = None
        else:
            date_int = int(date_val)

        # Store under multiple key variants
        for key in _barcode_variants(barcode):
            _barcode_to_date[key] = date_int

    return _metadata_df, _barcode_to_date


def _barcode_variants(barcode):
    """Generate lookup variants for a barcode string."""
    variants = {barcode, barcode.lower()}
    if barcode.startswith('hvd.'):
        stripped = barcode[4:]
        variants.update({stripped, stripped.lower()})
    else:
        prefixed = 'hvd.' + barcode
        variants.update({prefixed, prefixed.lower()})
    return variants


def retrieve_date(possible_barcode):
    """Look up a firstpub date for a barcode string. Returns int or None."""
    _, barcode_to_date = load_metadata()
    for key in _barcode_variants(possible_barcode):
        if key in barcode_to_date:
            return barcode_to_date[key]
    return None


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def confirm_fields(question):
    """Check all 14 required fields are present."""
    for field in REQUIRED_FIELDS:
        if field not in question:
            return False
    return True


def display_question_info(question):
    """Pretty-print key fields of a question for user review."""
    fields = ['metadata_frame', 'main_question', 'question_category',
              'manual_comment', 'answer_types', 'answer_strings', 'answer_length']
    for field in fields:
        if field in question:
            if field == 'answer_strings':
                print(f"{field}:")
                for ans in question[field]:
                    print(f"  - {ans}")
            elif field == 'answer_types':
                print(f"{field}:")
                for at in question[field]:
                    print(f"  - {at}")
            else:
                print(f"{field}:")
                print(textwrap.fill(str(question[field]), width=80))
        else:
            print(f"{field}: Not found")
    print()


def determine_answer_length(question):
    """Heuristic to classify answer length."""
    cat = question.get('question_category', '')
    if cat.endswith('clause'):
        return 'phrase'

    answer_strings = question['answer_strings']
    answer_lengths = [len(ans) for ans in answer_strings]
    median_length = sorted(answer_lengths)[len(answer_lengths) // 2]
    max_length = max(answer_lengths)

    if median_length < SHORT_ANSWER_MEDIAN_MAX and max_length < SHORT_ANSWER_MAX_MAX:
        return 'short_answer'
    elif median_length >= SENTENCE_PLUS_MEDIAN_MIN:
        return 'sentence_plus'
    else:
        print("Answer strings:")
        for ans in answer_strings:
            print(f"  - {ans}")
        print("\nThe answer length is ambiguous. Please choose:")
        print("1) short_answer   2) sentence_plus   3) phrase")
        choice = prompt_with_quit("Choice [1/2/3]: ", {'1', '2', '3'})
        return {'1': 'short_answer', '2': 'sentence_plus', '3': 'phrase'}[choice]


def _resolve_year_type(year):
    """Given a year int, return other_book_YYYY or anachronistic_YYYY."""
    if 1875 <= year <= 1924:
        return f'other_book_{year}'
    else:
        return f'anachronistic_{year}'


def check_answer_types(question):
    """Normalize answer_types in-place. May prompt user for unresolvable types."""
    for i, at in enumerate(question['answer_types']):
        # Step 1: direct renames
        if at == 'manual_distractor':
            question['answer_types'][i] = 'manual'
            at = 'manual'
        elif at == 'manual_anachronistic_distractor':
            question['answer_types'][i] = 'anachronistic_manual'
            at = 'anachronistic_manual'
        elif at == 'manual_same_book':
            question['answer_types'][i] = 'same_book'
            at = 'same_book'

        # Step 2: fix typo prefix
        if at.startswith('anachornistic_'):
            at = 'anachronistic_' + at[len('anachornistic_'):]
            question['answer_types'][i] = at

        # Step 2b: fix leading hyphen (e.g. anachronistic-sonnet_4.6)
        # Convention: underscore after 'anachronistic', hyphen between
        # model name and version (e.g. anachronistic_sonnet-4.6).
        if at.startswith('anachronistic-'):
            rest = at[len('anachronistic-'):]
            # Also fix internal separator: sonnet_4.6 -> sonnet-4.6
            rest = re.sub(r'^([a-zA-Z]+)_(\d)', r'\1-\2', rest)
            at = 'anachronistic_' + rest
            question['answer_types'][i] = at

        # Step 3: already allowable?
        if at in ALLOWABLE_ANSWER_TYPES:
            continue

        # Step 4: check anachronistic_YYYY or other_book_YYYY patterns
        m = re.match(r'^(anachronistic|other_book)_(\d{4})s?$', at)
        if m:
            year = int(m.group(2))
            question['answer_types'][i] = _resolve_year_type(year)
            continue

        # Step 4b: check anachronistic_internet -> anachronistic_google
        if at == 'anachronistic_internet':
            question['answer_types'][i] = 'anachronistic_google'
            continue

        # Step 5: opposing_side / opposing_view -> same_book
        if at in ('opposing_side', 'opposing_view'):
            question['answer_types'][i] = 'same_book'
            continue

        # Step 6: known named sources
        at_lower = at.lower()
        if at_lower in KNOWN_ANSWER_TYPE_DATES:
            year = KNOWN_ANSWER_TYPE_DATES[at_lower]
            question['answer_types'][i] = _resolve_year_type(year)
            continue

        # Step 7: try barcode lookup
        date = retrieve_date(at)
        if date is not None:
            question['answer_types'][i] = _resolve_year_type(date)
            continue

        # Step 8: unresolved — ask user
        print(f"\nUnresolvable answer_type: '{at}'")
        display_question_info(question)
        replacement = prompt_with_quit(
            "Enter a valid answer type (or barcode to look up): ", None)
        # Try to look up what they typed as a barcode
        date = retrieve_date(replacement)
        if date is not None:
            question['answer_types'][i] = _resolve_year_type(date)
        else:
            question['answer_types'][i] = replacement


def infer_frame_type(reasoning_type):
    """Deterministic lookup of frame_type from reasoning_type."""
    return REASONING_TO_FRAME[reasoning_type]


def collect_questions(subfolder):
    """Glob and parse all question files for a subfolder.
    Returns list of (filepath, question_dict).
    """
    pattern = FILE_PATTERNS[subfolder]
    process_dir = os.path.join(SCRIPT_DIR, subfolder, 'process_files')
    full_pattern = os.path.join(process_dir, pattern)
    files = sorted(glob.glob(full_pattern))

    if not files:
        print(f"Warning: no files matching {full_pattern}")
        return []

    results = []
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    q = json.loads(line, strict=False)
                    results.append((fpath, q))
                except json.JSONDecodeError as e:
                    print(f"Warning: JSON parse error in {os.path.basename(fpath)}"
                          f" line {line_num}: {e}")
    return results


def write_question(outfile, question):
    """Write one JSON line and flush."""
    outfile.write(json.dumps(question, ensure_ascii=False) + '\n')
    outfile.flush()


def prompt_with_quit(prompt_text, valid_choices, default=None):
    """Prompt user. 'q' raises UserQuit. Re-prompts on invalid input.
    If valid_choices is None, accept any non-empty input.
    If default is set, empty input returns the default.
    """
    while True:
        response = input(prompt_text).strip()
        if not response and default is not None:
            return default
        if response.lower() == 'q':
            raise UserQuit()
        if valid_choices is None:
            if response:
                return response
            print("Please enter a value (or 'q' to quit).")
        elif response in valid_choices:
            return response
        else:
            print(f"Invalid. Choose from {valid_choices} or 'q' to quit.")


def ensure_required_fields(question):
    """Add missing required fields with empty defaults; warn about them."""
    missing = [f for f in REQUIRED_FIELDS if f not in question]
    if missing:
        print(f"  Warning: missing fields {missing} — adding empty defaults")
        for f in missing:
            if f in ('answer_strings', 'answer_types', 'answer_probabilities'):
                question[f] = []
            elif f == 'source_date':
                question[f] = None
            else:
                question[f] = ''


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_subfolder(subfolder):
    """After processing, check for duplicates and missing questions."""
    input_questions = collect_questions(subfolder)
    input_set = set()
    for _, q in input_questions:
        key = (q.get('source_htid', ''), q.get('main_question', ''))
        input_set.add(key)

    output_set = set()
    duplicates = 0
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    q = json.loads(line, strict=False)
                    key = (q.get('source_htid', ''), q.get('main_question', ''))
                    if key in input_set:
                        if key in output_set:
                            duplicates += 1
                        output_set.add(key)
                except json.JSONDecodeError:
                    pass

    processed = len(output_set)
    missing = input_set - output_set

    if duplicates == 0 and len(missing) == 0:
        print(f"Verification: {processed} processed, 0 duplicates, 0 missing")
    else:
        parts = [f"{processed} processed"]
        if duplicates > 0:
            parts.append(f"{duplicates} duplicates found")
        if missing:
            parts.append(f"{len(missing)} question(s) missing")
        print(f"WARNING: {', '.join(parts)}")


# ---------------------------------------------------------------------------
# Per-subfolder workflows
# ---------------------------------------------------------------------------

def process_connectors(start_line=0):
    _process_cloze('connectors', start_line)


def process_batchconnectors(start_line=0):
    _process_cloze('batchconnectors', start_line)


def _process_cloze(subfolder, start_line=0):
    """Shared workflow for connectors and batchconnectors."""
    questions = collect_questions(subfolder)
    print(f"Found {len(questions)} questions in {subfolder}/")

    count = 0
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as outfile:
        for idx, (fpath, q) in enumerate(questions):
            if idx < start_line:
                continue

            ensure_required_fields(q)

            # Determine reasoning_type from question_category
            cat = q.get('question_category', '')
            if cat.endswith('clause') or cat == 'contrastclause':
                q['reasoning_type'] = 'phrase_cloze'
            elif cat.endswith('sentence'):
                q['reasoning_type'] = 'sentence_cloze'
            else:
                # Fallback: check if 'clause' or 'sentence' appears
                if 'clause' in cat:
                    q['reasoning_type'] = 'phrase_cloze'
                elif 'sentence' in cat:
                    q['reasoning_type'] = 'sentence_cloze'
                else:
                    print(f"  Unexpected cloze category: '{cat}' in "
                          f"{os.path.basename(fpath)}")
                    q['reasoning_type'] = 'phrase_cloze'

            q['frame_type'] = infer_frame_type(q['reasoning_type'])
            q['answer_length'] = determine_answer_length(q)
            check_answer_types(q)

            write_question(outfile, q)
            count += 1
            if count % 10 == 0:
                print(f"  Processed {count} questions...")

    print(f"Done: {count} questions written from {subfolder}/")
    verify_subfolder(subfolder)


def process_character(start_line=0):
    """Character questions — mostly automatic."""
    questions = collect_questions('character')
    print(f"Found {len(questions)} questions in character/")

    count = 0
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as outfile:
        for idx, (fpath, q) in enumerate(questions):
            if idx < start_line:
                continue

            ensure_required_fields(q)

            # Fold character_modeling variants
            q['reasoning_type'] = 'character_modeling'
            q['frame_type'] = infer_frame_type('character_modeling')
            q['answer_length'] = determine_answer_length(q)
            check_answer_types(q)

            write_question(outfile, q)
            count += 1
            if count % 10 == 0:
                print(f"  Processed {count} questions...")

    print(f"Done: {count} questions written from character/")
    verify_subfolder('character')


def process_knowledge(start_line=0):
    """Knowledge questions — interactive (user assigns reasoning_type)."""
    questions = collect_questions('knowledge')
    print(f"Found {len(questions)} questions in knowledge/")

    count = 0
    try:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as outfile:
            for idx, (fpath, q) in enumerate(questions):
                if idx < start_line:
                    continue

                ensure_required_fields(q)

                # Override metadata_frame and author_profession
                q['metadata_frame'] = COLUMBIAN_FRAME
                q['author_profession'] = ''
                q['frame_type'] = 'world_context'
                q['answer_length'] = determine_answer_length(q)
                check_answer_types(q)

                # Add "I don't know" answer
                q['answer_strings'].append("I don't know")
                q['answer_types'].append('manual')
                q['answer_probabilities'].append(0.0)

                # Display and ask for reasoning_type
                display_question_info(q)
                print("Reasoning type?  (k)nowledge  (i)nference  (r)efusal")
                choice = prompt_with_quit("Choice [k/i/r]: ", {'k', 'i', 'r'})
                q['reasoning_type'] = {
                    'k': 'knowledge', 'i': 'inference', 'r': 'refusal'
                }[choice]

                write_question(outfile, q)
                count += 1
                print(f"  [{count}] saved as {q['reasoning_type']}")

    except UserQuit:
        print(f"\nUser quit. {count} questions saved before exit.")

    print(f"Done: {count} questions written from knowledge/")
    verify_subfolder('knowledge')


def process_poetry(start_line=0):
    """Poetry questions — mostly automatic."""
    questions = collect_questions('poetry')
    print(f"Found {len(questions)} questions in poetry/")

    count = 0
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as outfile:
        for idx, (fpath, q) in enumerate(questions):
            if idx < start_line:
                continue

            ensure_required_fields(q)

            cat = q.get('question_category', '')
            if cat == 'poetic_form':
                q['reasoning_type'] = 'inference'
            elif cat == 'poetry_generation':
                q['reasoning_type'] = 'constrained_generation'
            else:
                print(f"  Unexpected poetry category: '{cat}'")
                q['reasoning_type'] = 'inference'

            q['frame_type'] = infer_frame_type(q['reasoning_type'])
            q['answer_length'] = determine_answer_length(q)
            check_answer_types(q)

            write_question(outfile, q)
            count += 1
            if count % 10 == 0:
                print(f"  Processed {count} questions...")

    print(f"Done: {count} questions written from poetry/")
    verify_subfolder('poetry')


def process_summary(start_line=0):
    """Summary topic-sentence questions — fully automatic."""
    questions = collect_questions('summary')
    print(f"Found {len(questions)} questions in summary/")

    count = 0
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as outfile:
        for idx, (fpath, q) in enumerate(questions):
            if idx < start_line:
                continue

            ensure_required_fields(q)

            q['reasoning_type'] = 'topic_sentence'
            q['frame_type'] = infer_frame_type('topic_sentence')
            q['answer_length'] = 'sentence_plus'
            check_answer_types(q)

            write_question(outfile, q)
            count += 1
            if count % 10 == 0:
                print(f"  Processed {count} questions...")

    print(f"Done: {count} questions written from summary/")
    verify_subfolder('summary')


def process_manual(start_line=0):
    """Manual questions — mixed automatic and interactive."""
    questions = collect_questions('manual')
    print(f"Found {len(questions)} questions in manual/")

    count = 0
    try:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as outfile:
            for idx, (fpath, q) in enumerate(questions):
                if idx < start_line:
                    continue

                ensure_required_fields(q)

                cat = q.get('question_category', '')

                if cat in MANUAL_AUTO_MAP:
                    # Automatic assignment
                    q['reasoning_type'] = MANUAL_AUTO_MAP[cat]
                    q['frame_type'] = infer_frame_type(q['reasoning_type'])
                    q['answer_length'] = determine_answer_length(q)
                    check_answer_types(q)

                    write_question(outfile, q)
                    count += 1
                    if count % 10 == 0:
                        print(f"  Processed {count} questions...")

                elif cat in MANUAL_INTERACTIVE_CATS:
                    # Interactive assignment
                    q['answer_length'] = determine_answer_length(q)
                    check_answer_types(q)
                    display_question_info(q)

                    print("Reasoning type?  (k)nowledge  (i)nference  "
                          "(r)efusal  (c)onstrained_generation  "
                          "(t)opic_sentence  (p)hrase_cloze  (s)entence_cloze")
                    choice = prompt_with_quit("Choice [k/i/r/c/t/p/s]: ",
                                             {'k', 'i', 'r', 'c', 't', 'p', 's'})
                    q['reasoning_type'] = {
                        'k': 'knowledge', 'i': 'inference',
                        'r': 'refusal', 'c': 'constrained_generation',
                        't': 'topic_sentence', 'p': 'phrase_cloze',
                        's': 'sentence_cloze'
                    }[choice]
                    q['frame_type'] = infer_frame_type(q['reasoning_type'])

                    # Offer to edit metadata_frame
                    print(f"\nCurrent metadata_frame:")
                    print(textwrap.fill(q['metadata_frame'], width=80))
                    edit = prompt_with_quit("Edit metadata_frame? [y/N]: ",
                                           {'y', 'n'}, default='n')
                    if edit == 'y':
                        new_frame = prompt_with_quit(
                            "Enter new metadata_frame: ", None)
                        q['metadata_frame'] = new_frame

                    write_question(outfile, q)
                    count += 1
                    print(f"  [{count}] saved as {q['reasoning_type']}")

                else:
                    # Unknown category — treat as interactive
                    print(f"  Unknown manual category: '{cat}' — "
                          f"requesting interactive assignment")
                    q['answer_length'] = determine_answer_length(q)
                    check_answer_types(q)
                    display_question_info(q)

                    print("Reasoning type?  (k)nowledge  (i)nference  "
                          "(r)efusal  (c)onstrained_generation  "
                          "(t)opic_sentence  (p)hrase_cloze  (s)entence_cloze")
                    choice = prompt_with_quit("Choice [k/i/r/c/t/p/s]: ",
                                             {'k', 'i', 'r', 'c', 't', 'p', 's'})
                    q['reasoning_type'] = {
                        'k': 'knowledge', 'i': 'inference',
                        'r': 'refusal', 'c': 'constrained_generation',
                        't': 'topic_sentence', 'p': 'phrase_cloze',
                        's': 'sentence_cloze'
                    }[choice]
                    q['frame_type'] = infer_frame_type(q['reasoning_type'])

                    write_question(outfile, q)
                    count += 1
                    print(f"  [{count}] saved as {q['reasoning_type']}")

    except UserQuit:
        print(f"\nUser quit. {count} questions saved before exit.")

    print(f"Done: {count} questions written from manual/")
    verify_subfolder('manual')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SUBFOLDER_DISPATCH = {
    'connectors': process_connectors,
    'batchconnectors': process_batchconnectors,
    'character': process_character,
    'knowledge': process_knowledge,
    'manual': process_manual,
    'poetry': process_poetry,
    'summary': process_summary,
}


def main():
    parser = argparse.ArgumentParser(
        description='Categorize and aggregate benchmark questions.')
    parser.add_argument('subfolder', choices=SUBFOLDER_DISPATCH.keys(),
                        help='Which pipeline subfolder to process')
    parser.add_argument('--start-line', type=int, default=0,
                        help='Skip first N questions (for resuming)')
    args = parser.parse_args()

    load_metadata()
    print(f"Processing {args.subfolder}/ (start-line={args.start_line})")
    print(f"Output: {OUTPUT_FILE}\n")

    SUBFOLDER_DISPATCH[args.subfolder](start_line=args.start_line)


if __name__ == '__main__':
    main()
