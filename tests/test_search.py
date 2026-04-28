"""
test_search.py - Tests for the search module
"""

import pytest
from src.search import find_pages, print_word

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
