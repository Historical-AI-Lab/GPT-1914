"""
edit_jsonl.py — Question Divider and Interactive Reviewer

Usage:
    python edit_jsonl.py <filename>           # interactive review
    python edit_jsonl.py <filename> --divide  # divide into 7 parts
"""

import json
import argparse
import os
import math
import textwrap


def divide_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]

    total = len(lines)
    n_parts = 7
    base_size = total // n_parts
    remainder = total % n_parts

    stem = filepath
    if stem.endswith('.jsonl'):
        stem = stem[:-6]

    start = 0
    for i in range(1, n_parts + 1):
        part_size = base_size + (1 if i <= remainder else 0)
        part_lines = lines[start:start + part_size]
        start += part_size
        out_path = f"{stem}-pt{i}.jsonl"
        with open(out_path, 'w', encoding='utf-8') as f:
            for line in part_lines:
                f.write(line + '\n')
        print(f"  {out_path}: {len(part_lines)} questions")

    print(f"\nTotal: {total} questions split into {n_parts} files.")


def truncate(text, max_len=120):
    if len(text) > max_len:
        return text[:max_len] + '...'
    return text


def input_multiline():
    print("Enter text (end with a line containing only '.'):")
    lines = []
    while True:
        line = input()
        if line == '.':
            break
        lines.append(line)
    return '\n'.join(lines)


def maybe_multiline(value):
    if value == 'multiline':
        return input_multiline()
    return value


def review_file(filepath):
    # Derive changes file path
    base = filepath
    if base.endswith('.jsonl'):
        base = base[:-6]
    changes_path = base + '-changes.jsonl'

    # Load questions
    with open(filepath, 'r', encoding='utf-8') as f:
        questions = [json.loads(line) for line in f if line.strip()]

    total = len(questions)

    # Load already-reviewed question numbers
    reviewed = set()
    if os.path.exists(changes_path):
        with open(changes_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    reviewed.add(entry['question_number'])

    already_done = len(reviewed)
    remaining = total - already_done

    filename_display = os.path.basename(filepath)
    print(f"\nReviewing {filename_display} ({total} questions, {already_done} already reviewed, {remaining} remaining)")
    print("Press 'q' to quit. Re-running on the same file will resume where you left off.\n")

    with open(changes_path, 'a', encoding='utf-8') as out:
        for q in questions:
            qnum = q.get('question_number')
            if qnum in reviewed:
                continue

            # Display question
            print(f"{'='*60}")
            print(f"Question number: {qnum}")
            print(f"Reasoning type:  {q.get('reasoning_type', '')}")

            def wrap_field(label, text, width=70):
                indent = ' ' * len(label)
                lines = textwrap.wrap(text, width=width)
                if not lines:
                    return
                print(label + lines[0])
                for line in lines[1:]:
                    print(indent + line)

            wrap_field("Metadata frame:  ", q.get('metadata_frame', ''))
            main_q = q.get('main_question', '')
            if main_q:
                wrap_field("Main question:   ", main_q)

            answer_strings = q.get('answer_strings', [])
            answer_types = q.get('answer_types', [])
            answer_probs = q.get('answer_probabilities', [])

            print("Answers:")
            for idx, ans in enumerate(answer_strings):
                prob = answer_probs[idx] if idx < len(answer_probs) else 0.0
                atype = answer_types[idx] if idx < len(answer_types) else ''
                marker = '*' if prob > 0 else ' '
                print(f"  {marker} {truncate(ans, 80):<83} [{atype}]")

            print()
            response = input("Confirm [a]s-is (default), or [c]omment/change? ").strip().lower()

            if response == 'q':
                print("Quitting.")
                break

            if response == 'c':
                new_metadata = maybe_multiline(input("New metadata frame (enter to skip): ").strip())
                new_question = maybe_multiline(input("New main question (enter to skip): ").strip())
                comments = maybe_multiline(input("Other comments (enter to skip): ").strip())
            else:
                new_metadata = ''
                new_question = ''
                comments = ''

            entry = {
                'question_number': qnum,
                'metadata_frame': new_metadata,
                'main_question': new_question,
                'comments': comments
            }
            out.write(json.dumps(entry) + '\n')
            out.flush()
            reviewed.add(qnum)
            print()


def main():
    parser = argparse.ArgumentParser(description='Divide or review a benchmark JSONL file.')
    parser.add_argument('filename', help='Path to .jsonl file')
    parser.add_argument('--divide', action='store_true', help='Divide into 7 equal parts')
    args = parser.parse_args()

    if args.divide:
        divide_file(args.filename)
    else:
        review_file(args.filename)


if __name__ == '__main__':
    main()
