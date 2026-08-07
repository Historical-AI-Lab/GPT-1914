#!/usr/bin/env python3
"""
Character Question Formation Script

Generates benchmark questions by combining character descriptions and dialogue
from the previous two scripts in the pipeline.

Anachronistic distractors come from API-hosted Qwen and Gemma via OpenRouter,
reusing the shared client in modelasjudge/openrouter_client.py that the cloze and
summary pipelines also use. The two extraction stages still run on local Ollama.

Usage:
    python character/form_character_questions.py DESCRIPTIONS_FILE DIALOGUE_FILE OUTPUT_FILE [OPTIONS]
"""

import json
import os
import sys
import argparse
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

import nltk
from nltk import sent_tokenize

# Download punkt tokenizer if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Reuse the OpenRouter client shared by the modelasjudge and summary pipelines
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "modelasjudge"))
from openrouter_client import make_openrouter_client, call_openrouter_chat

# Constants
PRIMARY_MODEL = "qwen/qwen3-30b-a3b-instruct-2507"
SECONDARY_MODEL = "google/gemma-4-31b-it"
MAX_TOKENS = 400
MAX_DESCRIPTION_WORDS = 150
MIN_DESCRIPTION_WORDS = 10
MIN_DIALOGUE_WORDS = 10  # Minimum words for ground truth dialogue

METADATA_FRAME_TEMPLATE = """This question asks you to provide dialogue for a character in a book. The book in this case is a {genre} published in {source_date} by {source_author}, a {author_nationality} writer born in {author_birth}."""

CHARACTER_PORTION_TEMPLATE = """The character in question here is {longest_character_name}, who is described this way in the book:
{character_description}
"""

NO_SUMMARY_TEMPLATE = """
Write a short passage of dialogue (1-3 sentences) that we might expect from {longest_character_name}:"""

WITH_SUMMARY_TEMPLATE = """
At one moment in the book, {summary} Write a short passage of dialogue (1-3 sentences) that {longest_character_name} might speak in this situation:"""

ANACHRONISTIC_PROMPT_TEMPLATE = """Answer the following question with a short passage of dialogue (approximately {target_words} words, 1-3 sentences):

{question_text}

Write only the dialogue, without quotation marks:"""


class Character:
    """
    Represents a character with paired descriptions and dialogue.

    Attributes:
        names: List[str] - All name variants
        longest_name: str - Longest name for display
        descriptions: List[Tuple[int, str]] - (chunk_index, description_text)
        dialogue_passages: List[Dict] - Dialogue entries with chunk, dialogue, summary, passage
        used_dialogue_indices: Set[int] - Indices of dialogue passages already used
    """

    def __init__(self, names: List[str], descriptions: List[Tuple[int, str]],
                 dialogue_passages: List[Dict]):
        self.names = names
        self.longest_name = max(names, key=len)
        self.descriptions = sorted(descriptions, key=lambda x: x[0])  # Sort by chunk
        self.dialogue_passages = dialogue_passages
        self.used_dialogue_indices = set()
        self._cached_description = None

    def get_unused_dialogue_indices(self) -> List[int]:
        """Return indices of dialogue passages not yet used."""
        return [i for i in range(len(self.dialogue_passages))
                if i not in self.used_dialogue_indices]

    def mark_dialogue_used(self, index: int):
        """Mark a dialogue passage as used."""
        self.used_dialogue_indices.add(index)

    def build_character_description(self, max_words: int = MAX_DESCRIPTION_WORDS) -> Optional[str]:
        """
        Build prose description from description chunks.

        Rules:
        - Enclose each description (from different chunks) in quotes
        - Separate with commas
        - Add sentences in chunk order until next would exceed max_words
        - Truncate at sentence boundaries
        - Final description must be 10-150 words

        Returns:
            Character description string or None if constraints not met
        """
        if self._cached_description is not None:
            return self._cached_description

        if not self.descriptions:
            return None

        chunk_texts = []
        total_words = 0

        for chunk_idx, desc_text in self.descriptions:
            # Split description into sentences
            sentences = sent_tokenize(desc_text)
            chunk_sentences = []
            chunk_words = 0

            for sentence in sentences:
                sentence_words = len(sentence.split())
                if total_words + chunk_words + sentence_words > max_words:
                    # Would exceed limit
                    if chunk_sentences:
                        # Keep what we have from this chunk
                        break
                    elif not chunk_texts:
                        # First chunk, first sentence - include even if over limit
                        chunk_sentences.append(sentence)
                        chunk_words += sentence_words
                        break
                    else:
                        # We have previous chunks, stop here
                        break
                else:
                    chunk_sentences.append(sentence)
                    chunk_words += sentence_words

            if chunk_sentences:
                chunk_text = ' '.join(chunk_sentences)
                chunk_texts.append(f'"{chunk_text}"')
                total_words += chunk_words

            if total_words >= max_words:
                break

        if not chunk_texts:
            return None

        # Join chunks with commas
        description = ', '.join(chunk_texts)

        # Check length constraints
        word_count = len(description.split())
        if word_count < MIN_DESCRIPTION_WORDS or word_count > max_words:
            return None

        self._cached_description = description
        return description


def model_slug(model_id: str) -> str:
    """
    Strip the OpenRouter provider prefix for use in answer_type strings.

    "qwen/qwen3-30b-a3b-instruct-2507" -> "qwen3-30b-a3b-instruct-2507"
    """
    return model_id.split('/')[-1]


_CLIENT = None


def get_client():
    """Return a cached OpenRouter client, creating it on first use."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = make_openrouter_client()
    return _CLIENT


def call_openrouter_model(prompt: str, model: str = PRIMARY_MODEL,
                          max_tokens: int = MAX_TOKENS,
                          debug: bool = False) -> Dict[str, Any]:
    """
    Generate text via OpenRouter.

    Wraps call_openrouter_chat, which raises after exhausting its own retries,
    in the status-dict contract the rest of this module expects.

    Args:
        prompt: The prompt to send to the model
        model: OpenRouter model identifier (default: PRIMARY_MODEL)
        max_tokens: Maximum tokens in the visible answer
        debug: Print the request and full response

    Returns:
        Dict with 'status' and either 'response' or 'reason'
    """
    try:
        text = call_openrouter_chat(
            get_client(), model, prompt, max_tokens=max_tokens, debug=debug
        )
        return {"status": "success", "response": (text or "").strip()}
    except Exception as e:
        return {"status": "error", "reason": f"{type(e).__name__}: {str(e)}"}


def load_metadata(metadata_file: Optional[str]) -> Dict[str, Any]:
    """
    Load metadata from file or prompt user interactively.

    Args:
        metadata_file: Path to JSON metadata file, or None to prompt user

    Returns:
        Dict with metadata fields
    """
    if metadata_file:
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Validate required fields
            required_fields = ['source_title', 'source_author', 'source_date',
                             'source_htid', 'author_nationality', 'genre', 'author_birth']
            for field in required_fields:
                if field not in metadata:
                    print(f"Error: Missing required field '{field}' in metadata file")
                    sys.exit(1)

            return metadata
        except FileNotFoundError:
            print(f"Warning: Metadata file not found: {metadata_file}")
            print("Prompting for metadata interactively...\n")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in metadata file: {e}")
            sys.exit(1)

    # Prompt user for metadata
    print("Please provide book metadata:")
    metadata = {}
    metadata['source_title'] = input("  Title: ").strip()
    metadata['source_author'] = input("  Author: ").strip()
    metadata['source_date'] = int(input("  Publication year: ").strip())
    metadata['source_htid'] = input("  HathiTrust ID: ").strip()
    metadata['author_nationality'] = input("  Author nationality: ").strip()
    metadata['genre'] = input("  Genre [novel]: ").strip() or "novel"
    metadata['author_birth'] = int(input("  Author birth year: ").strip())

    print()
    return metadata


def build_metadata_frame(metadata: Dict) -> str:
    """
    Build metadata frame for questions.

    Args:
        metadata: Metadata dict

    Returns:
        Formatted metadata frame string
    """
    return METADATA_FRAME_TEMPLATE.format(
        genre=metadata['genre'],
        source_date=metadata['source_date'],
        source_author=metadata['source_author'],
        author_nationality=metadata['author_nationality'],
        author_birth=metadata['author_birth']
    )


def load_common_words_set(dictionary_file: str, max_words: int = 10000) -> Set[str]:
    """
    Load common words from frequency-ordered dictionary.

    Args:
        dictionary_file: Path to dictionary file (one word per line, frequency ordered)
        max_words: Maximum number of words to load

    Returns:
        Set of common words (lowercase)
    """
    common_words = set()

    try:
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_words:
                    break
                word = line.strip().lower()
                if word:
                    common_words.add(word)
        print(f"Loaded {len(common_words)} common words from {dictionary_file}")
    except FileNotFoundError:
        print(f"Warning: Dictionary file not found: {dictionary_file}")
        print("Summary capitalization will be preserved as-is.")
        return set()

    return common_words


def preprocess_summary(summary: str, common_words: Set[str]) -> str:
    """
    Lowercase first word of summary if it's a common word (not a proper noun).

    Args:
        summary: Original summary text
        common_words: Set of common words from dictionary

    Returns:
        Summary with potentially lowercased first word
    """
    words = summary.split()
    if not words:
        return summary

    first_word = words[0]

    # Check if first word (lowercase) is in common words set
    if first_word.lower() in common_words:
        # It's a common word, lowercase it
        words[0] = first_word.lower()
        return ' '.join(words)
    else:
        # Likely a proper noun, keep as-is
        return summary


def load_characters(descriptions_file: str, dialogue_file: str) -> List[Character]:
    """
    Load character descriptions and dialogue, pairing them into Character objects.

    Args:
        descriptions_file: Path to character descriptions JSONL
        dialogue_file: Path to character dialogue JSONL

    Returns:
        List of Character objects
    """
    # Load descriptions
    descriptions_map = {}
    try:
        with open(descriptions_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                names = tuple(sorted(entry['character_names']))
                descriptions = [tuple(d) for d in entry['descriptions']]
                descriptions_map[names] = descriptions
    except FileNotFoundError:
        print(f"Error: Descriptions file not found: {descriptions_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in descriptions file: {e}")
        sys.exit(1)

    # Load dialogue
    dialogue_map = {}
    try:
        with open(dialogue_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                names = tuple(sorted(entry['character_names']))
                dialogue = entry.get('character_dialogue', [])
                dialogue_map[names] = dialogue
    except FileNotFoundError:
        print(f"Error: Dialogue file not found: {dialogue_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in dialogue file: {e}")
        sys.exit(1)

    # Pair descriptions with dialogue
    characters = []
    matched_dialogue = set()

    for names, descriptions in descriptions_map.items():
        # Find matching dialogue (any name overlap)
        dialogue = None
        for dialogue_names, dialogue_passages in dialogue_map.items():
            # Check for any name overlap
            if set(names) & set(dialogue_names):
                dialogue = dialogue_passages
                matched_dialogue.add(dialogue_names)
                break

        if dialogue:
            character = Character(list(names), descriptions, dialogue)

            # Check if character has valid description
            desc = character.build_character_description()
            if desc:
                characters.append(character)
            else:
                print(f"Warning: Skipping character {names[0]} - description too short/long")
        else:
            print(f"Warning: No dialogue found for character: {names[0]}")

    # Warn about unmatched dialogue
    for names in dialogue_map:
        if names not in matched_dialogue:
            print(f"Warning: No descriptions found for character: {names[0]}")

    if not characters:
        print("Error: No matching characters found with both descriptions and dialogue")
        sys.exit(1)

    print(f"\nLoaded {len(characters)} characters with paired descriptions and dialogue")
    return characters


def strip_surrounding_quotes(text: str) -> str:
    """
    Strip quotation marks from text while preserving apostrophes.

    - Removes all double quotes (regular and fancy) throughout the text
    - Removes single quotes (regular and fancy) only at start/end of string

    Args:
        text: Text to process

    Returns:
        Text with quotation marks removed but apostrophes preserved
    """
    # Strip double quotation marks throughout (regular and fancy)
    text = text.replace('"', '').replace('"', '').replace('"', '')

    # Strip single quotes only at start/end of string (regular and fancy)
    single_quotes = "'''"
    while text and text[0] in single_quotes:
        text = text[1:]
    while text and text[-1] in single_quotes:
        text = text[:-1]

    return text


def truncate_to_sentences(text: str, max_sentences: int) -> str:
    """
    Truncate text to maximum number of sentences and strip quotation marks.

    Args:
        text: Text to truncate
        max_sentences: Maximum number of sentences

    Returns:
        Truncated text without quotation marks
    """
    sentences = sent_tokenize(text)
    truncated = ' '.join(sentences[:max_sentences])

    return strip_surrounding_quotes(truncated)


def truncate_to_word_target(text: str, target_words: int) -> str:
    """
    Truncate text to get as close to target word count as possible.

    Rules:
    - Only trim at sentence boundaries
    - Always keep at least one sentence
    - Add next sentence only if it gets us closer to target

    Args:
        text: Text to truncate
        target_words: Target word count

    Returns:
        Truncated text (quotes stripped)
    """
    # Strip quotation marks first (preserving apostrophes)
    text = strip_surrounding_quotes(text)

    sentences = sent_tokenize(text)
    if not sentences:
        return text

    # Always include first sentence
    result_sentences = [sentences[0]]
    current_words = len(sentences[0].split())

    # Try adding more sentences if they get us closer to target
    for sentence in sentences[1:]:
        sentence_words = len(sentence.split())
        new_total = current_words + sentence_words

        # Calculate distance from target
        current_distance = abs(target_words - current_words)
        new_distance = abs(target_words - new_total)

        # Only add if it gets us closer (or equal) to target
        if new_distance <= current_distance:
            result_sentences.append(sentence)
            current_words = new_total
        else:
            # Adding this sentence moves us further from target, stop
            break

    return ' '.join(result_sentences)


def generate_question(character: Character, dialogue_index: int, metadata_frame: str,
                     use_summary: bool, common_words: Set[str]) -> Dict:
    """
    Generate question dict from character and dialogue.

    Args:
        character: Character object
        dialogue_index: Index of dialogue passage to use
        metadata_frame: Metadata frame string
        use_summary: Whether to include summary in question
        common_words: Set of common words for summary preprocessing

    Returns:
        Question dict
    """
    dialogue_passage = character.dialogue_passages[dialogue_index]

    # Build character description
    character_description = character.build_character_description()

    # Build character portion
    character_portion = CHARACTER_PORTION_TEMPLATE.format(
        longest_character_name=character.longest_name,
        character_description=character_description
    )

    # Build question text
    if use_summary:
        # Preprocess summary to potentially lowercase first word
        summary = preprocess_summary(dialogue_passage['summary'], common_words)
        question_text = WITH_SUMMARY_TEMPLATE.format(
            summary=summary,
            longest_character_name=character.longest_name
        )
    else:
        question_text = NO_SUMMARY_TEMPLATE.format(
            longest_character_name=character.longest_name
        )

    # Truncate ground truth to 3 sentences
    ground_truth = truncate_to_sentences(dialogue_passage['dialogue'], 3)

    return {
        'metadata_frame': metadata_frame,
        'character_portion': character_portion,
        'question_text': question_text,
        'ground_truth': ground_truth,
        'dialogue_chunk_index': dialogue_passage['chunk'],
        'passage': dialogue_passage['passage'],
        'character': character,
        'dialogue_index': dialogue_index,
        'use_summary': use_summary
    }


def select_distractors(characters: List[Character], question_char: Character,
                      dialogue_idx: int, use_summary: bool,
                      target_words: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Select distractor answers from character dialogue.

    Args:
        characters: List of all Character objects
        question_char: The character for the question
        dialogue_idx: Index of the ground truth dialogue
        use_summary: Whether question uses summary
        target_words: Target word count to match ground truth length

    Returns:
        For WITH_SUMMARY: (same_character_distractor, other_character_distractor)
        For NO_SUMMARY: (other_character_distractor_1, other_character_distractor_2)
    """
    ground_truth_chunk = question_char.dialogue_passages[dialogue_idx]["chunk"]
    distractor_1 = None
    distractor_2 = None

    # Collect all candidates from other characters
    other_chars = [c for c in characters if c != question_char]
    other_char_candidates = []
    if other_chars:
        for char in other_chars:
            for i, passage in enumerate(char.dialogue_passages):
                distance = abs(passage["chunk"] - ground_truth_chunk)
                other_char_candidates.append((distance, char, i, passage["dialogue"]))

    if use_summary:
        # WITH_SUMMARY: Get one from same character, one from other characters
        unused = question_char.get_unused_dialogue_indices()
        if dialogue_idx in unused:
            unused_copy = [i for i in unused if i != dialogue_idx]
        else:
            unused_copy = list(unused)

        if unused_copy:
            # Find closest by chunk number
            closest = min(unused_copy, key=lambda i: abs(
                question_char.dialogue_passages[i]["chunk"] - ground_truth_chunk
            ))
            distractor_1 = truncate_to_word_target(
                question_char.dialogue_passages[closest]["dialogue"], target_words
            )

        # Get one from other characters
        if other_char_candidates:
            other_char_candidates.sort(key=lambda x: x[0])
            min_distance = other_char_candidates[0][0]
            closest_candidates = [c for c in other_char_candidates if c[0] == min_distance]
            selected = random.choice(closest_candidates)
            distractor_2 = truncate_to_word_target(selected[3], target_words)

    else:
        # NO_SUMMARY: Get TWO from other characters
        if other_char_candidates:
            other_char_candidates.sort(key=lambda x: x[0])

            # Select first distractor (closest by chunk)
            min_distance = other_char_candidates[0][0]
            closest_candidates = [c for c in other_char_candidates if c[0] == min_distance]
            selected_1 = random.choice(closest_candidates)
            distractor_1 = truncate_to_word_target(selected_1[3], target_words)

            # Remove the selected candidate and select second distractor
            other_char_candidates.remove(selected_1)
            if other_char_candidates:
                # Select from remaining candidates (prefer close to ground truth)
                min_distance = other_char_candidates[0][0]
                closest_candidates = [c for c in other_char_candidates if c[0] == min_distance]
                selected_2 = random.choice(closest_candidates)
                distractor_2 = truncate_to_word_target(selected_2[3], target_words)

    return distractor_1, distractor_2


def generate_anachronistic_distractor(question_text: str, target_words: int,
                                     model: str = PRIMARY_MODEL,
                                     max_attempts: int = 2,
                                     debug: bool = False) -> Optional[str]:
    """
    Generate anachronistic distractor using specified model.

    Args:
        question_text: Full question text
        target_words: Target word count to match ground truth length
        model: OpenRouter model identifier (default: PRIMARY_MODEL)
        max_attempts: Maximum number of attempts
        debug: Print debug information

    Returns:
        Anachronistic distractor string or None if all attempts failed
    """
    prompt = ANACHRONISTIC_PROMPT_TEMPLATE.format(
        question_text=question_text,
        target_words=target_words
    )

    for attempt in range(max_attempts):
        if attempt > 0:
            print(f"\n  Retrying anachronistic distractor (attempt {attempt + 1}/{max_attempts})...")

        result = call_openrouter_model(prompt, model=model, max_tokens=MAX_TOKENS, debug=debug)

        if result['status'] != 'success':
            print(f"  Error generating anachronistic distractor: {result['reason']}")
            continue

        # Truncate to target word count using smart truncation
        distractor = truncate_to_word_target(result['response'], target_words)

        # Present for approval
        print(f"\n  Anachronistic distractor: {distractor}")
        approval = input("  Accept this distractor? (y/n) [y]: ").strip().lower()

        if approval in ['y', 'yes', '']:
            return distractor
        else:
            print("  Distractor rejected.")

    return None


def prompt_for_manual_distractors(target_words: int) -> List[str]:
    """
    Collect any number of hand-written distractors, blank line ends the loop.

    Every entry is typed anachronistic_manual with probability 0.0 by the caller.

    Args:
        target_words: Ground truth length, shown as guidance

    Returns:
        List of distractor strings, possibly empty
    """
    print(f"\n  Manual distractors (ground truth is {target_words} words).")
    manual = []
    while True:
        entry = input("  Add a manual distractor (blank line = done): ").strip()
        if not entry:
            break
        manual.append(entry)
        print(f"    Added ({len(entry.split())} words).")
    return manual


def prompt_for_context_judged() -> bool:
    """
    Ask whether this question is open to judgment about fit with the target context.

    Only context-judged questions carry reject_reasons. Default is no: character
    questions ask for plausible dialogue, which is not usually scored on period fit.

    Returns True if context_judged.
    """
    response = input(
        "\nIs this question open to judgment on context fit (context_judged)? "
        "(y = yes, enter/n = no): "
    ).strip().lower()
    return response in ('y', 'yes')


def prompt_for_reject_reason() -> str:
    """
    Prompt user for the reason a non-ground_truth answer should be rejected.

    Required, non-blank: the ideal phrasing begins with a verb, completing
    "Reason for rejection is that the answer ...".
    """
    while True:
        reason = input("Reason for rejection is that the answer ...: ").strip()
        if reason:
            return reason
        print("  Reason cannot be blank")


def collect_reject_reasons(answer_strings: List[str],
                           answer_types: List[str]) -> List[str]:
    """
    Collect one rejection rationale per answer, parallel to answer_strings.

    Index 0 is the ground truth and always gets "". Must be called only after the
    answer list is final, so the arrays stay aligned.

    Args:
        answer_strings: Final answer list, ground truth at index 0
        answer_types: Final answer type list, same length

    Returns:
        List of reasons, same length as answer_strings
    """
    print("\n" + "-" * 60)
    print("Rejection reasons (one per distractor)")
    print("-" * 60)

    reasons = [""]
    for i, (answer, atype) in enumerate(zip(answer_strings[1:], answer_types[1:]), 1):
        print(f"\n  Answer {i + 1} ({atype}): {answer}")
        reasons.append(prompt_for_reject_reason())

    return reasons


def present_question_for_approval(question_dict: Dict, distractors: List[str],
                                  question_num: int) -> str:
    """
    Present question to user for approval.

    Args:
        question_dict: Question dictionary
        distractors: List of distractor strings
        question_num: Question number for display

    Returns:
        "accept", "reject", or "stop"
    """
    print("\n" + "=" * 60)
    print(f"QUESTION #{question_num}")
    print("=" * 60)
    print()
    print(question_dict['metadata_frame'])
    print()
    print(question_dict['character_portion'])
    print(question_dict['question_text'])
    print()
    print("Ground Truth:")
    print(f"  {question_dict['ground_truth']}")
    print()
    print("Distractors:")
    for i, distractor in enumerate(distractors, 1):
        print(f"  {i}. {distractor}")
    print()
    print("=" * 60)

    while True:
        response = input("Accept (y/n)? [Enter = n] Commands: y, n, p (show passage), stop: ").strip().lower()

        if response in ['y', 'yes']:
            return "accept"
        elif response in ['n', 'no', '']:
            return "reject"
        elif response == 'p':
            print("\n--- Original Passage ---")
            print(question_dict['passage'])
            print("--- End Passage ---\n")
        elif response == 'stop':
            return "stop"
        else:
            print("Invalid command. Use: y (accept), n (reject), p (show passage), stop")


def format_question(question_dict: Dict, metadata: Dict, distractors: List[str],
                   distractor_types: List[str], use_summary: bool,
                   context_judged: bool = False,
                   reject_reasons: Optional[List[str]] = None) -> Dict:
    """
    Format final question for output.

    Args:
        question_dict: Question dictionary
        metadata: Metadata dictionary
        distractors: List of distractor strings
        distractor_types: Answer type per distractor, parallel to distractors
        use_summary: Whether question uses summary
        context_judged: Whether the question is judged on fit with its context
        reject_reasons: One rationale per answer when context_judged, else None

    Returns:
        Formatted question dict for JSONL output
    """
    answer_strings = [question_dict["ground_truth"]] + distractors
    answer_types = ["ground_truth"] + distractor_types

    record = {
        "metadata_frame": question_dict["metadata_frame"],
        "main_question": question_dict["character_portion"] + question_dict["question_text"],
        "source_title": metadata["source_title"],
        "source_author": metadata["source_author"],
        "source_date": metadata["source_date"],
        "author_nationality": metadata["author_nationality"],
        "source_genre": metadata["genre"],
        "author_birth": metadata["author_birth"],
        "source_htid": metadata["source_htid"],
        "question_category": ("character_modeling_with_summary" if use_summary
                            else "character_modeling_without_summary"),
        "question_process": "automatic",
        "answer_types": answer_types,
        "answer_strings": answer_strings,
        "answer_probabilities": [1.0] + [0.0] * (len(answer_strings) - 1),
        "reject_reasons": reject_reasons,
        "context_judged": 1 if context_judged else 0,
        "passage": question_dict["passage"]
    }

    # Invariant shared with the manual/ and summary/ writers: reject_reasons
    # exists only on context_judged questions.
    if not context_judged:
        del record["reject_reasons"]

    return record


def process_questions(characters: List[Character], metadata: Dict, output_file: str,
                     common_words: Set[str], start_from: int = 0,
                     debug: bool = False) -> None:
    """
    Main question generation loop.

    Args:
        characters: List of Character objects
        metadata: Metadata dictionary
        output_file: Path to output JSONL file
        common_words: Set of common words for summary preprocessing
        start_from: Resume from question N
        debug: Print debug information
    """
    # Build metadata frame once
    metadata_frame = build_metadata_frame(metadata)

    # Track progress
    questions_generated = 0
    questions_accepted = 0

    print("\n" + "=" * 60)
    print("Starting question generation...")
    print("=" * 60)

    # Main loop - continues until no characters have unused dialogue
    while True:
        # Filter characters with unused dialogue
        available_chars = [c for c in characters
                          if len(c.get_unused_dialogue_indices()) > 0]

        if not available_chars:
            print("\nNo more characters with unused dialogue.")
            break

        # Randomly select character
        character = random.choice(available_chars)

        # Randomly select unused dialogue
        unused_indices = character.get_unused_dialogue_indices()
        dialogue_idx = random.choice(unused_indices)

        # Determine if we can use no_summary (only if description > 100 words)
        character_description = character.build_character_description()
        if character_description is None:
            # Skip this character if description is invalid
            print(f"Skipping {character.longest_name} - invalid description")
            character.mark_dialogue_used(dialogue_idx)
            continue

        description_word_count = len(character_description.split())

        # Random choice: with or without summary (75% with_summary, 25% no_summary)
        # But only allow no_summary if description > 100 words
        if description_word_count > 100:
            use_summary = random.random() < 0.75  # 75% chance of with_summary
        else:
            use_summary = True  # Always use summary for short descriptions

        # Generate question (with summary preprocessing if needed)
        question_dict = generate_question(
            character, dialogue_idx, metadata_frame, use_summary, common_words
        )

        # Check ground truth meets minimum length
        target_words = len(question_dict['ground_truth'].split())
        if target_words < MIN_DIALOGUE_WORDS:
            print(f"Ground truth too short ({target_words} words), skipping...")
            character.mark_dialogue_used(dialogue_idx)
            continue

        # Select distractors from book
        # Returns: (same_char, other_char) for WITH_SUMMARY or (other_char_1, other_char_2) for NO_SUMMARY
        distractor_1, distractor_2 = select_distractors(
            characters, character, dialogue_idx, use_summary, target_words
        )

        # Build distractor list, typing each as it is added. With a summary the
        # first slot comes from the same character; otherwise both are other
        # characters in the same book.
        distractors = []
        distractor_types = []
        if distractor_1:
            distractors.append(distractor_1)
            distractor_types.append("same_character" if use_summary else "same_book")
        if distractor_2:
            distractors.append(distractor_2)
            distractor_types.append("same_book")

        # Need at least 2 book distractors
        if len(distractors) < 2:
            print(f"Not enough distractors available for {character.longest_name}, skipping...")
            character.mark_dialogue_used(dialogue_idx)
            continue

        # Present question with book distractors for approval FIRST
        questions_generated += 1
        if questions_generated < start_from:
            character.mark_dialogue_used(dialogue_idx)
            continue

        try:
            decision = present_question_for_approval(question_dict, distractors,
                                                    questions_generated)
        except KeyboardInterrupt:
            print("\n\nStopped by user (Ctrl+C).")
            break

        if decision == "stop":
            print("\nStopped by user.")
            break

        # If question rejected, mark dialogue as used and continue
        if decision != "accept":
            character.mark_dialogue_used(dialogue_idx)
            print("✗ Question rejected.")
            continue

        # Question accepted - now generate anachronistic distractors, one per model
        full_question = (question_dict["metadata_frame"] + "\n\n" +
                        question_dict["character_portion"] +
                        question_dict["question_text"])

        for anachronistic_model in (PRIMARY_MODEL, SECONDARY_MODEL):
            print(f"\nGenerating anachronistic distractor for {character.longest_name} "
                  f"using {anachronistic_model}...")
            anachronistic = generate_anachronistic_distractor(
                full_question, target_words=target_words,
                model=anachronistic_model, debug=debug
            )
            if anachronistic is None:
                print(f"  No usable distractor from {anachronistic_model}; continuing.")
                continue
            distractors.append(anachronistic)
            distractor_types.append(f"anachronistic_{model_slug(anachronistic_model)}")

        # Mark dialogue as used regardless of whether anachronistic generation succeeds
        character.mark_dialogue_used(dialogue_idx)

        # Hand-written distractors, as many as the user cares to type
        for manual in prompt_for_manual_distractors(target_words):
            distractors.append(manual)
            distractor_types.append("anachronistic_manual")

        # Only the two book distractors survived: nothing tests anachronism here
        if len(distractors) < 3:
            print("✗ Question not saved (no anachronistic distractor).")
            continue

        # Reasons must be collected last, so they stay parallel to answer_strings
        context_judged = prompt_for_context_judged()
        reject_reasons = None
        if context_judged:
            reject_reasons = collect_reject_reasons(
                [question_dict["ground_truth"]] + distractors,
                ["ground_truth"] + distractor_types
            )

        # Format and write to output
        formatted = format_question(
            question_dict, metadata, distractors, distractor_types, use_summary,
            context_judged=context_judged, reject_reasons=reject_reasons
        )
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(formatted, ensure_ascii=False) + '\n')

        questions_accepted += 1
        print(f"✓ Question accepted and saved. ({questions_accepted} accepted so far)")

    # Final summary
    print(f"\n{'=' * 60}")
    print("=== Summary ===")
    print(f"Questions generated: {questions_generated}")
    print(f"Questions accepted: {questions_accepted}")
    print(f"Output: {output_file}")
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate character modeling questions from descriptions and dialogue"
    )

    parser.add_argument("descriptions_file",
                       help="Path to character descriptions JSONL file")
    parser.add_argument("dialogue_file",
                       help="Path to character dialogue JSONL file")
    parser.add_argument("output_file",
                       help="Path to output questions JSONL file")
    parser.add_argument("--metadata",
                       help="Path to JSON file with book metadata")
    parser.add_argument("--dictionary", default="../MainDictionary.txt",
                       help="Path to word frequency dictionary (default: ../MainDictionary.txt)")
    parser.add_argument("--start-from", type=int, default=0,
                       help="Resume from question N (default: 0)")
    parser.add_argument("--debug", action="store_true",
                       help="Print debug information")

    args = parser.parse_args()

    # Load metadata
    print("Loading metadata...")
    metadata = load_metadata(args.metadata)

    # Load common words dictionary
    print("\nLoading common words dictionary...")
    common_words = load_common_words_set(args.dictionary)

    # Load characters
    print(f"\nLoading characters from:")
    print(f"  Descriptions: {args.descriptions_file}")
    print(f"  Dialogue: {args.dialogue_file}")
    characters = load_characters(args.descriptions_file, args.dialogue_file)

    print(f"\nUsing {PRIMARY_MODEL} and {SECONDARY_MODEL} "
          "for anachronistic distractors")

    # Process questions
    process_questions(characters, metadata, args.output_file, common_words,
                     args.start_from, args.debug)


if __name__ == "__main__":
    main()
