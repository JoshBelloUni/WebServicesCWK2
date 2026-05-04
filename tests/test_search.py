"""
test_search.py - Tests for the search module
"""

import time
import pytest
from src.search import find_pages, print_word
from src.indexer import build_index

# ---------------------------------------------------------------------------
# Example index
# ---------------------------------------------------------------------------

# "courage" is only on page 1
# "life"    is on both pages
# "love"    is only on page 2
INDEX = {
    "courage": {
        "https://quotes.toscrape.com/": {
            "frequency": 2,
            "positions": [{"quote_index": 0, "word_pos": 0}, {"quote_index": 0, "word_pos": 4}],
        }
    },
    "life": {
        "https://quotes.toscrape.com/": {
            "frequency": 1,
            "positions": [{"quote_index": 0, "word_pos": 1}],
        },
        "https://quotes.toscrape.com/page/2/": {
            "frequency": 3,
            "positions": [{"quote_index": 0, "word_pos": 0}, {"quote_index": 1, "word_pos": 2}, {"quote_index": 2, "word_pos": 1}],
        },
    },
    "love": {
        "https://quotes.toscrape.com/page/2/": {
            "frequency": 1,
            "positions": [{"quote_index": 0, "word_pos": 3}],
        }
    },
}


# ---------------------------------------------------------------------------
# find_pages
# ---------------------------------------------------------------------------

def test_find_pages_returns_urls_containing_query_word():
    # test if courage only exists in the first page
    results = find_pages(INDEX, "courage")
    assert results == ["https://quotes.toscrape.com/"]

def test_find_pages_returns_all_pages_when_word_spans_multiple_pages():
    # tests if life exists in both pages
    results = find_pages(INDEX, "life")
    assert "https://quotes.toscrape.com/" in results
    assert "https://quotes.toscrape.com/page/2/" in results

def test_find_pages_returns_intersection_for_multi_word_query():
    # tests the intersection of life and love - only on page 2
    # and not in page 1
    results = find_pages(INDEX, "life love")
    assert results == ["https://quotes.toscrape.com/page/2/"]
    assert "https://quotes.toscrape.com/" not in results

def test_find_pages_returns_empty_list_when_word_not_in_index():
    # tests if word is not in index, should return empty results
    results = find_pages(INDEX, "missing")
    assert results == []

def test_find_pages_returns_empty_list_for_blank_query():
    # tests if blank message = blank results
    results = find_pages(INDEX, "   ")
    assert results == []

def test_find_pages_returns_sorted_urls():
    # test that find returns the pages in order
    # uses new random example to test if it is not due to order in index
    index = {
        "life": {
            "https://quotes.toscrape.com/page/9/": {"frequency": 1, "positions": []},
            "https://quotes.toscrape.com/page/5/": {"frequency": 1, "positions": []},
            "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": []},
            "https://quotes.toscrape.com/":        {"frequency": 1, "positions": []},
        }
    }
    results = find_pages(index, "life")
    assert results == sorted(results)


# ---------------------------------------------------------------------------
# print_word
# ---------------------------------------------------------------------------

def test_print_word_outputs_frequency_and_url(capsys):
    # test if the print correctly prints the url and frequency
    print_word(INDEX, "courage")
    output = capsys.readouterr().out
    assert "https://quotes.toscrape.com/" in output
    assert "frequency : 2" in output

def test_print_word_outputs_not_found_for_missing_word(capsys):
    # tests if a word not in index is not found
    print_word(INDEX, "missing")
    output = capsys.readouterr().out
    assert "not found" in output.lower()

def test_print_word_normalises_input_before_lookup(capsys):
    # "Courage!" should match "courage" after stripping punctuation and lowercasing
    print_word(INDEX, "Courage!")
    output = capsys.readouterr().out
    assert "not found" not in output.lower()
    assert "https://quotes.toscrape.com/" in output


# ---------------------------------------------------------------------------
# Shared pages data for integration tests
# ---------------------------------------------------------------------------

INTEGRATION_PAGES = {
    "https://quotes.toscrape.com/": [
        {"text": "Stay hungry stay foolish", "author": "Steve Jobs", "tags": ["life"]},
        {"text": "Be the change you wish to see", "author": "Gandhi", "tags": ["change"]},
    ],
    "https://quotes.toscrape.com/page/2/": [
        {"text": "In the middle of difficulty lies opportunity", "author": "Einstein", "tags": ["wisdom"]},
    ],
}


# ---------------------------------------------------------------------------
# Cross-module tests
#
# Builds -> Finds
# ---------------------------------------------------------------------------

def test_find_pages_on_index_built_from_pages():
    # tests that find_pages works correctly on an index built from real page data
    index = build_index(INTEGRATION_PAGES)
    results = find_pages(index, "stay")
    assert "https://quotes.toscrape.com/" in results

def test_find_pages_multi_word_query_on_built_index():
    # tests multi-word intersection search on an index built from crawled pages
    index = build_index(INTEGRATION_PAGES)
    results = find_pages(index, "stay foolish")
    assert results == ["https://quotes.toscrape.com/"]
    assert "https://quotes.toscrape.com/page/2/" not in results

def test_find_pages_word_unique_to_second_page_on_built_index():
    # tests that a word only on page 2 is not returned for page 1
    index = build_index(INTEGRATION_PAGES)
    results = find_pages(index, "opportunity")
    assert results == ["https://quotes.toscrape.com/page/2/"]
    assert "https://quotes.toscrape.com/" not in results


# ---------------------------------------------------------------------------
# Helper to generate large synthetic index
#
# Generates 5000 words that occur in 50 pages with freq of 2 per page
# ---------------------------------------------------------------------------

def _make_large_index(n_words=5000, n_pages=50):
    """Generate a large synthetic index for performance testing."""
    index = {}
    for i in range(n_words):
        word = f"word{i}"
        index[word] = {
            f"https://quotes.toscrape.com/page/{j}/": {
                "frequency": 2,
                "positions": [{"quote_index": 0, "word_pos": i}],
            }
            for j in range(n_pages)
        }
    return index


# ---------------------------------------------------------------------------
# Performance tests
# ---------------------------------------------------------------------------

def test_find_pages_performance_single_word_large_index():
    # tests that a single-word search on a 5000-word x 50-page index completes within 0.5 seconds
    large_index = _make_large_index(5000, 50)
    start = time.time()
    results = find_pages(large_index, "word4999")
    elapsed = time.time() - start
    assert len(results) == 50
    assert elapsed < 0.5, f"find_pages on large index took {elapsed:.2f}s — too slow"

def test_find_pages_performance_multi_word_large_index():
    # tests that a three-word intersection search on a large index completes within 0.5 seconds
    large_index = _make_large_index(5000, 50)
    start = time.time()
    results = find_pages(large_index, "word4997 word4998 word4999")
    elapsed = time.time() - start
    assert len(results) == 50
    assert elapsed < 0.5, f"multi-word find_pages on large index took {elapsed:.2f}s — too slow"


# ---------------------------------------------------------------------------
# Integration tests (require --run-integration; hit the real site)
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_real_find_pages_returns_results_for_common_word(real_pages):
    # tests that searching a common word returns at least one page from the real index
    index = build_index(real_pages)
    results = find_pages(index, "life")
    assert isinstance(results, list)
    assert len(results) > 0

@pytest.mark.integration
def test_real_find_pages_multi_word_is_subset_of_single_word(real_pages):
    # tests that a two-word search returns no more pages than either word alone on real data
    index = build_index(real_pages)
    single = find_pages(index, "life")
    multi = find_pages(index, "life love")
    assert len(multi) <= len(single)

@pytest.mark.integration
def test_real_find_pages_missing_word_returns_empty(real_pages):
    # tests that a nonsense word returns an empty list on the real index
    index = build_index(real_pages)
    assert find_pages(index, "xyznonexistentword") == []

@pytest.mark.integration
def test_real_print_word_outputs_url_and_frequency(real_pages, capsys):
    # tests that print_word produces a URL and frequency line for a real word
    index = build_index(real_pages)
    word = next(iter(index))
    print_word(index, word)
    output = capsys.readouterr().out
    assert "frequency" in output
    assert "https://" in output
