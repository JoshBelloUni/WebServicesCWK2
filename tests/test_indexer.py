"""
test_indexer.py - Tests for the indexer module
"""

import pytest
from src.indexer import build_index, save_index, load_index

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

PAGES = {
    "https://quotes.toscrape.com/": [
        {"text": "Stay hungry stay foolish", "author": "Steve Jobs", "tags": ["life"]},
    ],
    "https://quotes.toscrape.com/page/2/": [
        {"text": "Be the change", "author": "Gandhi", "tags": ["change"]},
        {"text": "Stay strong stay humble", "author": "Unknown", "tags": ["life"]},
    ],
}


# ---------------------------------------------------------------------------
# build_index
# ---------------------------------------------------------------------------

def test_build_index_includes_words_from_quotes():
    # tests building the index, and if the words are correctly stored
    index = build_index(PAGES)
    assert "hungry" in index
    assert "change" in index

def test_build_index_lowercases_all_words():
    # tests if index stores text as lowercase
    pages = {"https://quotes.toscrape.com/": [
        {"text": "COURAGE Wisdom STRENGTH", "author": "A", "tags": []}
    ]}
    index = build_index(pages)
    assert "courage" in index
    assert "COURAGE" not in index
    assert "wisdom" in index
    assert "Wisdom" not in index
    assert "strength" in index
    assert "STRENGTH" not in index 

def test_build_index_strips_punctuation():
    # tests if index removes punctuation 
    pages = {"https://quotes.toscrape.com/": [
        {"text": "“Hello, world!”", "author": "A", "tags": []}
    ]}
    index = build_index(pages)
    assert "hello" in index
    assert "world" in index
    for word in index:
        assert word.isalnum() or "_" in word    # returns true if punctuation

def test_build_index_records_word_frequency():
    # "stay" appears in page 1 once and page 2 once — check one page
    index = build_index(PAGES)
    url = "https://quotes.toscrape.com/"
    assert index["stay"][url]["frequency"] == 2  # "Stay hungry stay foolish"

def test_build_index_records_quote_index_in_positions():
    # "stay" appears twice in quote index 1 ("Stay strong stay humble")
    index = build_index(PAGES)
    url = "https://quotes.toscrape.com/page/2/"
    positions = index["stay"][url]["positions"]
    quote_indices = [p["quote_index"] for p in positions]
    assert quote_indices.count(1) == 2  # both occurrences are in quote index 1

def test_build_index_records_word_position_within_quote():
    # test if position within quote is saved
    index = build_index(PAGES)
    url = "https://quotes.toscrape.com/"
    # "hungry" is word position 1 in "stay hungry stay foolish"
    positions = index["hungry"][url]["positions"]
    assert positions[0]["word_pos"] == 1

def test_build_index_maps_word_to_multiple_pages():
    # test if all pages per word are saved
    index = build_index(PAGES)
    # "stay" appears on both pages
    assert "https://quotes.toscrape.com/" in index["stay"]
    assert "https://quotes.toscrape.com/page/2/" in index["stay"]

def test_build_index_returns_empty_dict_for_no_pages():
    # tests if an empty dict is returned if an empty page is used
    assert build_index({}) == {}


# ---------------------------------------------------------------------------
# save_index / load_index
# ---------------------------------------------------------------------------

def test_save_index_creates_json_file(tmp_path):
    # tests if 'index.json' is created successfully
    filepath = str(tmp_path / "index.json")
    save_index({"hello": {}}, filepath)
    assert (tmp_path / "index.json").exists()

def test_load_index_returns_empty_dict_when_file_missing(tmp_path):
    # tests if loading a non existent json returns an empty dict
    result = load_index(str(tmp_path / "nonexistent.json"))
    assert result == {}

def test_load_index_restores_saved_data(tmp_path):
    # tests a full round trip of building, saving, then loading
    index = build_index(PAGES)
    filepath = str(tmp_path / "index.json")
    save_index(index, filepath)
    loaded = load_index(filepath)
    assert loaded.keys() == index.keys()
    assert loaded["stay"] == index["stay"]
