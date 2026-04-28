"""
test_tag_explorer.py - Tests for the tag_explorer module
"""

import pytest
from src.tag_explorer import (
    _tokenize,
    build_tag_index,
    save_tag_index,
    load_tag_index,
    list_tags,
    explore_tag,
)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

# "change" is shared across both tags (lower IDF).
# "courage"/"wisdom" are unique to "inspirational" (higher IDF).
# "romance"/"heart" are unique to "love" (higher IDF).
PAGES = {
    "https://quotes.toscrape.com/": [
        {"text": "Courage wisdom change", "author": "A", "tags": ["inspirational"]},
        {"text": "Romance heart change",  "author": "B", "tags": ["love"]},
    ]
}


# ---------------------------------------------------------------------------
# _tokenize
# ---------------------------------------------------------------------------

def test_tokenize_lowercases_input():
    # tests if tokenize lowercases each word
    assert "hello" in _tokenize("Hello World")

def test_tokenize_strips_punctuation():
    # tests if punctuation is stripped
    tokens = _tokenize("life, “world!”")
    assert all(c.isalnum() or c == "_" for t in tokens for c in t)

def test_tokenize_removes_stopwords():
    # tests if stop words are removed
    tokens = _tokenize("the cat sat on the mat")
    assert "the" not in tokens
    assert "on" not in tokens

def test_tokenize_removes_single_character_tokens():
    # tests if single chars are removed
    tokens = _tokenize("a b c dog")
    assert all(len(t) > 1 for t in tokens)

def test_tokenize_returns_list():
    # tests if the string is converted to a list of substrings
    assert isinstance(_tokenize("some text"), list)


# ---------------------------------------------------------------------------
# build_tag_index
# ---------------------------------------------------------------------------

def test_build_tag_index_returns_empty_dict_for_empty_pages():
    # tests if an empty dict is returned for empty pages
    assert build_tag_index({}) == {}

def test_build_tag_index_creates_key_for_every_tag():
    # tests if a index key is created for each tag
    tag_index = build_tag_index(PAGES)
    assert "inspirational" in tag_index
    assert "love" in tag_index

def test_build_tag_index_creates_no_extra_tag_keys():
    # tests if tags are unique
    tag_index = build_tag_index(PAGES)
    assert set(tag_index.keys()) == {"inspirational", "love"}

def test_build_tag_index_sorts_words_by_score_descending():
    # tests if tags are sorted
    tag_index = build_tag_index(PAGES)
    for tag, entries in tag_index.items():
        scores = [score for _, score in entries]
        assert scores == sorted(scores, reverse=True), f"'{tag}' entries are not sorted"

def test_build_tag_index_ranks_unique_word_above_shared_word():
    # tests if a word unique to a certain tag is higher than a shared word
    tag_index = build_tag_index(PAGES)
    entries = dict(tag_index["inspirational"])
    assert entries["courage"] > entries["change"]

def test_build_tag_index_excludes_stopwords():
    # tests if stopwords are removed
    pages = {"https://quotes.toscrape.com/": [
        {"text": "the only way to do great work", "author": "A", "tags": ["work"]}
    ]}
    tag_index = build_tag_index(pages)
    words = {word for word, _ in tag_index.get("work", [])}
    assert "the" not in words
    assert "to" not in words

def test_build_tag_index_produces_positive_scores():
    # tests if tf-idf score are positive
    tag_index = build_tag_index(PAGES)
    for entries in tag_index.values():
        for _, score in entries:
            assert score > 0


# ---------------------------------------------------------------------------
# save_tag_index / load_tag_index
# ---------------------------------------------------------------------------

def test_save_and_load_tag_index_round_trip(tmp_path):
    # tests a full round trip of saving and loading the index
    tag_index = build_tag_index(PAGES)
    filepath = str(tmp_path / "tag_index.json")
    save_tag_index(tag_index, filepath)
    loaded = load_tag_index(filepath)
    assert loaded.keys() == tag_index.keys()
    for tag in tag_index:
        for (w1, s1), (w2, s2) in zip(tag_index[tag], loaded[tag]):
            assert w1 == w2
            assert abs(s1 - s2) < 1e-6

def test_load_tag_index_returns_empty_dict_when_file_missing(tmp_path):
    # tests if an empty dict is returned with missing index
    result = load_tag_index(str(tmp_path / "nonexistent.json"))
    assert result == {}


# ---------------------------------------------------------------------------
# list_tags / explore_tag
# ---------------------------------------------------------------------------

def test_list_tags_prints_not_loaded_message_for_empty_index(capsys):
    # tests if list works with no index loaded
    list_tags({})
    assert "No tag index loaded" in capsys.readouterr().out

def test_list_tags_prints_all_tag_names(capsys):
    # tests list tags with correctly loaded index
    list_tags(build_tag_index(PAGES))
    output = capsys.readouterr().out
    assert "inspirational" in output
    assert "love" in output

def test_explore_tag_prints_not_found_for_unknown_tag(capsys):
    # tests result if there is an unknown tag
    explore_tag(build_tag_index(PAGES), "nonexistent")
    assert "not found" in capsys.readouterr().out.lower()

def test_explore_tag_prints_not_loaded_message_for_empty_index(capsys):
    # tests explore tag for unloaded index
    explore_tag({}, "inspirational")
    assert "No tag index loaded" in capsys.readouterr().out

def test_explore_tag_prints_characteristic_words_for_valid_tag(capsys):
    # tests explore tag for correct usage
    explore_tag(build_tag_index(PAGES), "inspirational")
    output = capsys.readouterr().out
    assert "inspirational" in output
    assert "courage" in output or "wisdom" in output
