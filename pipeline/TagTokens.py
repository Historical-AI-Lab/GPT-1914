# TagTokens.py
# Accepts a collection of book pages and returns
# tokenized text with metadata tags for inference.

# Optimized version that:
# 1. Can be called externally without command-line interface
# 2. Minimizes overhead by reusing tokenizer instances
# 3. Simplifies tokenization since no '[EOL]' mapping needed

"""
Returns:
    List[dict]: List of page dictionaries with structure:
        {
            'source_file': str,
            'page_number': int,
            'tokens': List[str],
            'metadata_tags': List[List[str]]  # Note: converted from sets to lists
        }
"""

import json
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
from collections import defaultdict
import statistics
from transformers import RobertaTokenizerFast


@dataclass
class ProcessedPage:
    """Container for processed page data"""
    tokens: List[str]
    metadata_tags: List[Set[str]]  # Sets of metadata tags for each token
    page_number: int
    source_file: str

    def to_dict(self) -> dict:
        return {
            'source_file': self.source_file,
            'page_number': self.page_number,
            'tokens': self.tokens,
            'metadata_tags': [list(tags) for tags in self.metadata_tags]
        }


class PageTagger:
    """
    Tokenizes book pages and adds metadata tags for inference.
    Optimized for repeated calls with minimal overhead.
    """
    
    def __init__(self, model_name: str = "roberta-large"):
        # Load tokenizer once and reuse
        self.tokenizer = RobertaTokenizerFast.from_pretrained(model_name)
        # Instance variables that get reset per batch
        self.pages_by_book: Dict[str, List[Dict]] = defaultdict(list)
        self.book_stats: Dict[str, Dict] = {}
        self.top_lines_cache: Dict[Tuple[str, int], List[str]] = {}
    
    def _reset_batch_state(self):
        """Reset state for a new batch of pages"""
        self.pages_by_book.clear()
        self.book_stats.clear()
        self.top_lines_cache.clear()
    
    def _group_pages_by_book(self, data: List[Dict]) -> None:
        """Group pages by source book and sort by page number"""
        for page in data:
            source_file = page['meta']['source_file']
            self.pages_by_book[source_file].append(page)
        
        # Sort pages by page number within each book
        for source_file in self.pages_by_book:
            self.pages_by_book[source_file].sort(
                key=lambda x: x['meta']['page_number']
            )
    
    def _calculate_book_statistics(self) -> None:
        """Calculate statistics for each book (mean line length, etc.)"""
        for source_file, pages in self.pages_by_book.items():
            all_line_lengths = []
            
            for page in pages:
                text = page['text']
                lines = text.split('\n')  # Simple split since no '[EOL]' markers
                line_lengths = [len(line.strip()) for line in lines if line.strip()]
                all_line_lengths.extend(line_lengths)
            
            mean_line_length = statistics.mean(all_line_lengths) if all_line_lengths else 0
            self.book_stats[source_file] = {
                'mean_line_length': mean_line_length
            }
    
    def _get_top_lines(self, text: str, num_lines: int = 5) -> List[str]:
        """Get the first num_lines lines that have >4 characters"""
        lines = text.split('\n')
        top_lines = []
        
        for line in lines:
            clean_line = line.strip()
            if len(clean_line) > 4:
                top_lines.append(clean_line)
                if len(top_lines) >= num_lines:
                    break
        
        return top_lines
    
    def _get_top_lines_cached(self, source_file: str, page_idx: int, num_lines: int = 5) -> List[str]:
        """Get top lines with caching to avoid recomputation"""
        cache_key = (source_file, page_idx)
        
        if cache_key not in self.top_lines_cache:
            page_text = self.pages_by_book[source_file][page_idx]['text']
            self.top_lines_cache[cache_key] = self._get_top_lines(page_text, num_lines)
        
        return self.top_lines_cache[cache_key]
    
    def _find_repeated_lines(self, current_page_idx: int, source_file: str) -> Set[str]:
        """Find repeated lines by comparing with nearby pages"""
        pages = self.pages_by_book[source_file]
        current_top_lines = self._get_top_lines_cached(source_file, current_page_idx)
        
        repeated_lines = set()
        
        # Check pages i-2, i-1, i+1, i+2
        for offset in [-2, -1, 1, 2]:
            compare_idx = current_page_idx + offset
            if 0 <= compare_idx < len(pages):
                compare_top_lines = self._get_top_lines_cached(source_file, compare_idx)
                
                # Compare each current top line with each compare top line
                for current_line in current_top_lines:
                    for compare_line in compare_top_lines:
                        similarity = SequenceMatcher(None, current_line, compare_line).real_quick_ratio()
                        if similarity > 0.5:
                            similarity = SequenceMatcher(None, current_line, compare_line).ratio()
                            if similarity > 0.8:  # Adjust threshold as needed
                                repeated_lines.add(current_line)
        
        return repeated_lines
    
    def _get_metadata_tags(self, word: str, word_start_char: int, word_end_char: int, 
                          text: str, line: str, repeated_lines: Set[str], 
                          mean_line_length: float) -> Set[str]:
        """Generate metadata tags for a word"""
        tags = set()
        linest = line.strip()
        
        # Tag 1: Short line (below mean length)
        if len(linest) < mean_line_length - 4:  # Allow some tolerance
            tags.add("short_line")
    
        # Tag 2: First 5%
        text_length = len(text)
        if word_start_char < 0.05 * text_length:
            tags.add("first05")
        
        # Tag 3: Last 10% and Last 15%
        if word_end_char > 0.9 * text_length:
            # Tag 5: Footnote (line in last 10% starts with footnote starter)
            footnote_starters = ['1', '2', '3', '4', '*', '†', '¹', '²', '³', '⁴']  
            if any(linest.startswith(starter) for starter in footnote_starters):
                tags.add("footnote")
            
            if word_end_char > 0.95 * text_length:
                tags.add("last15")

        # Tag 4: Header (repeated line in first 10% of text)
        if word_start_char < 0.10 * text_length and len(linest) > 1 and linest in repeated_lines:
            tags.add("header")
        
        # Tag 6: Capitalized
        if word and word[0].isupper():
            tags.add("capitalized")
        
        # Tag 7: All uppercase
        if word.isupper() and len(word) > 1:
            tags.add("uppercase")
        
        # Tag 8: Non-alphabetic line
        if len(linest) > 1 and not any(c.isalpha() for c in linest):
            tags.add("nonalphabetic")
        
        return tags

    def _process_single_page(self, page: Dict, page_idx: int, source_file: str) -> ProcessedPage:
        """
        Tokenize text and align with metadata tags.
        Simplified since no character position mapping needed.
        """
        text = page['text']
        repeated_lines = self._find_repeated_lines(page_idx, source_file)
        mean_line_length = self.book_stats[source_file]['mean_line_length']
        
        # Tokenize with offset mapping - no position mapping needed!
        encoding = self.tokenizer(
            text, 
            return_offsets_mapping=True, 
            add_special_tokens=False,
            return_tensors=None
        )
        
        tokens = self.tokenizer.convert_ids_to_tokens(encoding['input_ids'])
        offset_mapping = encoding['offset_mapping']
        
        # Process each token
        final_tokens = []
        final_metadata_tags = []
        
        # Split text into lines for metadata analysis - simple since linebreaks are '\n'
        lines = text.split('\n')
        
        for token, (start_char, end_char) in zip(tokens, offset_mapping):
            # Find which line this token belongs to
            current_pos = 0
            token_line = ""
            line_start_pos = 0
            
            for line in lines:
                line_end_pos = current_pos + len(line)
                if start_char >= current_pos and start_char < line_end_pos:
                    token_line = line.strip()
                    line_start_pos = current_pos
                    break
                current_pos += len(line) + 1  # +1 for '\n'
            
            # Find the word this token belongs to for metadata analysis
            word_start = start_char
            word_end = end_char
            
            # Expand backwards to start of word
            while word_start > 0 and (text[word_start - 1].isalnum() or text[word_start - 1] in "'-"):
                word_start -= 1
            
            # Expand forwards to end of word  
            while word_end < len(text) and (text[word_end].isalnum() or text[word_end] in "'-"):
                word_end += 1
            
            # Extract the word
            token_word = text[word_start:word_end].strip()
            if not token_word:  # For space/punctuation tokens, use the token itself
                token_word = text[start_char:end_char]
            
            # Use line midpoint for position-based metadata tags
            line_midpoint = line_start_pos + len(token_line) // 2
            
            # Get metadata tags for this token
            metadata_tags = self._get_metadata_tags(
                token_word, line_midpoint, line_midpoint, text, token_line, 
                repeated_lines, mean_line_length
            )
            
            final_tokens.append(token)
            final_metadata_tags.append(metadata_tags)
        
        return ProcessedPage(
            tokens=final_tokens,
            metadata_tags=final_metadata_tags,
            page_number=page['meta']['page_number'],
            source_file=source_file
        )
    
    def process_pages(self, data: List[Dict]) -> List[ProcessedPage]:
        """
        Process all pages and return processed data.
        Main entry point for external calls.
        """
        # Reset state for this batch
        self._reset_batch_state()
        
        # Group pages and calculate statistics
        self._group_pages_by_book(data)
        self._calculate_book_statistics()
        
        processed_pages = []
        
        for source_file, pages in self.pages_by_book.items():
            for page_idx, page in enumerate(pages):
                processed_page = self._process_single_page(page, page_idx, source_file)
                processed_pages.append(processed_page)
        
        # While we use the ProcessedPage dataclass internally in this module,
        # we convert it to a dictionary format for external use
        # so as not to introduce dependencies on the dataclass structure.  
        
        return [page.to_dict() for page in processed_pages]
    
    def get_statistics(self, processed_pages: List[ProcessedPage]) -> Dict:
        """Get processing statistics as a dictionary"""
        total_tokens = sum(len(page.tokens) for page in processed_pages)
        
        # Count metadata tag usage
        tag_counts = defaultdict(int)
        for page in processed_pages:
            for tags in page.metadata_tags:
                for tag in tags:
                    tag_counts[tag] += 1
        
        stats = {
            'total_pages': len(processed_pages),
            'total_tokens': total_tokens,
            'tag_usage': dict(tag_counts),
            'tag_percentages': {tag: count/total_tokens*100 for tag, count in tag_counts.items()},
            'books': {}
        }
        
        # Add book-level statistics
        for source_file, book_stats in self.book_stats.items():
            book_pages = [p for p in processed_pages if p.source_file == source_file]
            stats['books'][source_file] = {
                'pages': len(book_pages),
                'mean_line_length': book_stats['mean_line_length']
            }
        
        return stats


# Global instance for reuse to minimize overhead
_tagger_instance: Optional[PageTagger] = None

def get_tagger_instance(model_name: str = "roberta-large") -> PageTagger:
    """Get or create a PageTagger instance to reuse tokenizer"""
    global _tagger_instance
    if _tagger_instance is None:
        _tagger_instance = PageTagger(model_name)
    return _tagger_instance

def tokenize_books(data: List[Dict], model_name: str = "roberta-large") -> List[ProcessedPage]:
    """
    Main function to be called from outside the script to process a list of book pages.
    
    The argument `data` is a list of dictionaries, each containing:
    - 'text': the text of the page (with regular '\n' linebreaks)
    - 'meta': a dictionary with metadata including 'source_file' and 'page_number'

    The function returns a list of ProcessedPage objects, each containing:
    - tokens: the tokenized text 
    - metadata_tags: a list of sets containing metadata tags for each token
    - page_number: the page number
    - source_file: the source file name
    """
    
    # Get reusable tagger instance to minimize overhead
    tagger = get_tagger_instance(model_name)
    
    # Process all pages
    processed_pages = tagger.process_pages(data)
    
    return processed_pages

def tokenize_books_with_stats(data: List[Dict], model_name: str = "roberta-large") -> Tuple[List[ProcessedPage], Dict]:
    """
    Same as tokenize_books but also returns processing statistics.
    """
    tagger = get_tagger_instance(model_name)
    processed_pages = tagger.process_pages(data)
    stats = tagger.get_statistics(processed_pages)
    
    return processed_pages, stats


# Example usage for testing
if __name__ == "__main__":
    # Example data structure
    sample_data = [
        {
            'text': 'This is line 1\nThis is line 2\nThis is line 3',
            'meta': {'source_file': 'book1.txt', 'page_number': 1}
        },
        {
            'text': 'Another page\nWith different content\nAnd more lines',
            'meta': {'source_file': 'book1.txt', 'page_number': 2}
        }
    ]
    
    # Process the data
    processed_pages = tokenize_books(sample_data)
    
    # Print results
    for page in processed_pages:
        print(f"Page {page.page_number} from {page.source_file}:")
        print(f"  Tokens: {page.tokens[:10]}...")  # First 10 tokens
        print(f"  Tags: {page.metadata_tags[:10]}...")  # First 10 tag sets