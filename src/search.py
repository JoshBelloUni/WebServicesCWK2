"""
search.py - Search and retrieval logic
"""

import re


def print_word(index: dict, word: str) -> None:
    """Print the inverted index entry for a given word."""
    word = re.sub(r"[^\w\s]", "", word.lower())

    if word not in index:
        print(f"'{word}' not found in index.")
        return

    entries = index[word]
    print(f"\n'{word}' found on {len(entries)} page(s):\n")
    for url, stats in entries.items():
        print(f"  {url}")
        print(f"    frequency : {stats['frequency']}")
        print(f"    positions : {stats['positions']}\n")


def find_pages(index: dict, query: str) -> list:
    """Find all pages containing all words in the query."""
    words = [re.sub(r"[^\w\s]", "", w.lower()) for w in query.split()]
    words = [w for w in words if w]

    if not words:
        print("Empty query.")
        return []

    # get the set of URLs for each word, then intersect — page must contain all words
    matching_urls = None
    for word in words:
        if word not in index:
            print(f"'{word}' not found in index — no results.")
            return []
        urls = set(index[word].keys())
        matching_urls = urls if matching_urls is None else matching_urls & urls

    if not matching_urls:
        print(f"No pages found containing all of: {', '.join(words)}")
        return []

    results = sorted(matching_urls)
    print(f"\nFound {len(results)} page(s) containing '{query}':\n")
    for url in results:
        total_freq = sum(index[word][url]["frequency"] for word in words)
        print(f"  {url}  (total frequency: {total_freq})")
    print()

    return results
