"""
tag_explorer.py - TF-IDF tag analysis for the search engine
"""

import re
import json
import math
import os
from collections import defaultdict

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "that", "this",
    "it", "its", "i", "you", "he", "she", "we", "they", "not", "no",
    "so", "if", "as", "up", "out", "about", "into", "than", "then",
    "there", "when", "who", "which", "what", "all", "your", "my", "our",
    "their", "his", "her", "s", "t", "don", "just", "only", "one", "two",
}


def _tokenize(text: str) -> list:
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    return [w for w in cleaned.split() if w not in STOPWORDS and len(w) > 1]


def build_tag_index(pages: dict) -> dict:
    """
    Compute TF-IDF scores for each tag.

    Treats each tag as a document (the concatenation of all quote texts
    with that tag). TF = word count in tag corpus / total words in tag corpus.
    IDF = log(total_tags / number_of_tags_containing_word).

    Returns {tag: [[word, score], ...]} sorted by score descending, top 20 per tag.
    """
    tag_words = defaultdict(list)
    for quotes in pages.values():
        for quote in quotes:
            tokens = _tokenize(quote["text"])
            for tag in quote["tags"]:
                tag_words[tag].extend(tokens)

    total_tags = len(tag_words)
    if total_tags == 0:
        return {}

    # How many tags each word appears in (document frequency)
    word_tag_df = defaultdict(int)
    for words in tag_words.values():
        for word in set(words):
            word_tag_df[word] += 1

    tag_index = {}
    for tag, words in tag_words.items():
        total_words = len(words)
        if total_words == 0:
            continue

        tf = defaultdict(int)
        for word in words:
            tf[word] += 1

        scores = {}
        for word, count in tf.items():
            term_freq = count / total_words
            # +1 smoothing on IDF avoids zero scores for words in all tags
            idf = math.log((1 + total_tags) / (1 + word_tag_df[word])) + 1
            scores[word] = term_freq * idf

        tag_index[tag] = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]

    return tag_index


def save_tag_index(tag_index: dict, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tag_index, f, indent=2)


def load_tag_index(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def list_tags(tag_index: dict) -> None:
    if not tag_index:
        print("No tag index loaded. Run 'build' or 'load' first.")
        return
    tags = sorted(tag_index.keys())
    print(f"\n{len(tags)} tag(s) available:\n")
    cols = 4
    for i in range(0, len(tags), cols):
        row = tags[i:i + cols]
        print("  " + "  ".join(f"{t:<22}" for t in row))
    print()


def explore_tag(tag_index: dict, tag: str, top_n: int = 10) -> None:
    if not tag_index:
        print("No tag index loaded. Run 'build' or 'load' first.")
        return
    if tag not in tag_index:
        print(f"Tag '{tag}' not found. Use 'tags' to see available tags.")
        return

    entries = tag_index[tag][:top_n]
    max_score = entries[0][1] if entries else 1.0

    print(f"\nCharacteristic words for tag '{tag}' (TF-IDF):\n")
    for word, score in entries:
        bar_len = int((score / max_score) * 30)
        bar = "█" * bar_len
        print(f"  {word:<20} {score:.4f}  {bar}")
    print()
