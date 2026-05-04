"""
test_indexer.py - Tests for the indexer module
"""

import time
import pytest
from src.indexer import build_index, save_index, load_index
from src.search import find_pages

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


# ---------------------------------------------------------------------------
# Helper for large datasets
# ---------------------------------------------------------------------------

def _make_large_pages(n_pages=100, quotes_per_page=10):
    """Generate a large pages dict for performance testing."""
    vocab = ["wisdom", "courage", "life", "love", "change", "hope", "truth", "fear", "joy", "peace"]
    pages = {}
    for i in range(n_pages):
        url = f"https://quotes.toscrape.com/page/{i}/"
        pages[url] = [
            {"text": " ".join(vocab[(i + j) % len(vocab):] + vocab[:(i + j) % len(vocab)]),
             "author": f"Author {j}", "tags": [f"tag{j % 3}"]}
            for j in range(quotes_per_page)
        ]
    return pages


# ---------------------------------------------------------------------------
# Cross-module tests
# ---------------------------------------------------------------------------

def test_full_pipeline_build_save_load_search(tmp_path):
    # tests the full pipeline: build index, save to disk, load it back, then search
    index = build_index(PAGES)
    filepath = str(tmp_path / "index.json")
    save_index(index, filepath)
    loaded = load_index(filepath)
    results = find_pages(loaded, "stay")
    assert "https://quotes.toscrape.com/" in results

def test_search_results_identical_before_and_after_round_trip(tmp_path):
    # tests that a saved and reloaded index returns identical search results to the original
    index = build_index(PAGES)
    filepath = str(tmp_path / "index.json")
    save_index(index, filepath)
    loaded = load_index(filepath)
    assert find_pages(index, "change") == find_pages(loaded, "change")


# ---------------------------------------------------------------------------
# Performance tests
# ---------------------------------------------------------------------------

def test_build_index_performance_large_dataset():
    # tests that building an index from 100 pages x 10 quotes completes within 2 seconds
    pages = _make_large_pages(100, 10)
    start = time.time()
    index = build_index(pages)
    elapsed = time.time() - start
    assert len(index) > 0
    assert elapsed < 2.0, f"build_index on 1000 quotes took {elapsed:.2f}s — too slow"

def test_save_load_performance_large_index(tmp_path):
    # tests that saving and loading a large index each complete within 1 second
    index = build_index(_make_large_pages(100, 10))
    filepath = str(tmp_path / "index.json")
    start = time.time()
    save_index(index, filepath)
    save_time = time.time() - start
    start = time.time()
    load_index(filepath)
    load_time = time.time() - start
    assert save_time < 1.0, f"save_index took {save_time:.2f}s — too slow"
    assert load_time < 1.0, f"load_index took {load_time:.2f}s — too slow"


# ---------------------------------------------------------------------------
# Integration tests (require --run-integration; hit the real site)
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_real_build_index_contains_common_words(real_pages):
    # tests that indexing real crawled data produces entries for common quote words
    index = build_index(real_pages)
    assert "life" in index or "love" in index or "change" in index

@pytest.mark.integration
def test_real_index_word_entries_have_correct_structure(real_pages):
    # tests that every entry in the real index has a valid frequency and positions list
    index = build_index(real_pages)
    for pages in index.values():
        for stats in pages.values():
            assert "frequency" in stats and stats["frequency"] > 0
            assert "positions" in stats and isinstance(stats["positions"], list)

@pytest.mark.integration
def test_real_save_and_load_preserves_all_words(real_pages, tmp_path):
    # tests that saving and loading a built index produces identical word keys
    index = build_index(real_pages)
    filepath = str(tmp_path / "index.json")
    save_index(index, filepath)
    loaded = load_index(filepath)
    assert loaded.keys() == index.keys()
