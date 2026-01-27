"""
AnswerAcceptor.py

Interactive script to review and accept validated questions for the knowledge benchmark.

Reads validated questions from a JSONL file and displays them one at a time for manual review.
Accepted questions are reformatted and written to an output file in the final benchmark format.

Commands:
    a - accept the question
    r or Enter - reject the question
    p - show the full passage
    answer(string) - replace the answer span with the provided string
    question(string) - replace the question with the provided string
    b - break and stop processing
"""

import json
import os
import sys
import argparse

def format_knowledge_question(obj, source="Columbian Cyclopedia, vol 23",
                              source_date=1897, source_htid="hvd.hn5bs8"):
    """
    Convert a validated question object to the final benchmark format.

    Args:
        obj: The question object from the validation pipeline
        source: Source publication name
        source_date: Year of publication
        source_htid: HathiTrust ID

    Returns:
        Dict in the final benchmark format
    """
    return {
        "question": obj["question"],
        "answer_strings": [obj["answer_span"]],
        "answer_probabilities": [1.0],
        "passage": obj["passage"],
        "source": source,
        "source_date": source_date,
        "source_htid": source_htid,
        "question_category": "knowledge",
        "question_process": "automatic",
        "question_prefix": f"In answering the following question, assume that it has been posed in {source_date}: "
    }


def review_questions(input_file, output_file, source="Columbian Cyclopedia, vol 23",
                     source_date=1897, source_htid="hvd.hn5bs8"):
    """
    Interactively review questions and accept/reject them.

    Args:
        input_file: Path to input JSONL with validated questions
        output_file: Path to output JSONL for accepted questions
        source: Source publication name
        source_date: Year of publication
        source_htid: HathiTrust ID
    """

    # Read all questions
    print(f"Loading questions from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        questions = [json.loads(line) for line in f]

    print(f"Loaded {len(questions)} questions")
    print("\nCommands:")
    print("  a - accept")
    print("  r or Enter - reject")
    print("  p - show passage")
    print("  answer(new_answer) - replace answer")
    print("  question(new_question) - replace question")
    print("  b - break and quit\n")

    accepted_count = 0

    # Process each question
    for i, obj in enumerate(questions):
        print(f"\n{'='*60}")
        print(f"Question {i+1} of {len(questions)}")
        print(f"{'='*60}")
        print(f"Question: {obj['question']}")
        print(f"Answer Span: {obj['answer_span']}")
        print(f"Extracted Answer: {obj.get('extracted_answer', 'N/A')}")
        print(f"Match Type: {obj.get('match_type', 'N/A')}")

        # Inner loop for handling commands on this question
        while True:
            response = input('\nResponse: ').strip()

            if response == 'a':
                # Accept the question - write in final format
                formatted = format_knowledge_question(obj, source, source_date, source_htid)
                with open(output_file, 'a', encoding='utf-8') as out_f:
                    out_f.write(json.dumps(formatted, ensure_ascii=False) + '\n')
                accepted_count += 1
                print(f'✓ Accepted and written to {output_file}')
                print(f'Total accepted: {accepted_count}')
                break  # Move to next question

            elif response == 'r' or response == '':
                print('✗ Rejected.')
                break  # Move to next question

            elif response == 'p':
                print('\n--- PASSAGE ---')
                print(obj['passage'])
                print('--- END PASSAGE ---')
                # Continue inner loop to get another command

            elif response.startswith('answer(') and response.endswith(')'):
                new_answer = response[7:-1]  # Extract content between parentheses
                obj['answer_span'] = new_answer
                print(f'Updated answer span to: {new_answer}')
                # Continue inner loop to get another command

            elif response.startswith('question(') and response.endswith(')'):
                new_question = response[9:-1]  # Extract content between parentheses
                obj['question'] = new_question
                print(f'Updated question to: {new_question}')
                # Continue inner loop to get another command

            elif response == 'b':
                print(f'\nStopping. Accepted {accepted_count} questions.')
                return accepted_count

            else:
                print('Unrecognized response. Please try again.')
                # Continue inner loop

    # Finished all questions
    print(f'\n{"="*60}')
    print(f'Finished! Accepted {accepted_count} of {len(questions)} questions.')
    print(f'{"="*60}')
    return accepted_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Interactively review and accept validated questions."
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input JSONL file with validated questions"
    )

    parser.add_argument(
        "output_file",
        type=str,
        help="Path to output JSONL file for accepted questions"
    )

    parser.add_argument(
        "--source",
        type=str,
        default="Columbian Cyclopedia, vol 23",
        help="Source publication name (default: 'Columbian Cyclopedia, vol 23')"
    )

    parser.add_argument(
        "--source-date",
        type=int,
        default=1897,
        help="Year of publication (default: 1897)"
    )

    parser.add_argument(
        "--source-htid",
        type=str,
        default="hvd.hn5bs8",
        help="HathiTrust ID (default: 'hvd.hn5bs8')"
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # Run the review process
    try:
        review_questions(
            args.input_file,
            args.output_file,
            args.source,
            args.source_date,
            args.source_htid
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
