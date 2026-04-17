"""
indexer.py - Builds and manages the inverted index
"""

import re


def build_index(pages: dict) -> dict:
    """Build an inverted index from crawled page data."""

    index = {}
    for url, quotes in pages.items():
        for quote_index, quote in enumerate(quotes):
            cleaned = re.sub(r"[^\w\s]", "", quote["text"].lower())
            words = cleaned.split()
            
            for position, word in enumerate(words):
                if word not in index:
                    index[word] = {}
                if url not in index[word]:
                    index[word][url] = {"frequency": 0, "positions": []}

                index[word][url]["positions"].append({
                "quote_index": quote_index,
                "word_pos": position
                })

                index[word][url]["frequency"] += 1

    return index


def save_index(index: dict, filepath: str) -> None:
    """Save the inverted index to a file."""
    pass


def load_index(filepath: str) -> dict:
    """Load the inverted index from a file."""
    pass
