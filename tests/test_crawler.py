"""
test_crawler.py - Tests for the crawler module
"""

import time
import pytest
import requests
from unittest.mock import patch, MagicMock
from src.crawler import crawl
from src.indexer import build_index

# ---------------------------------------------------------------------------
# Fake HTML pages that mirror the structure of quotes.toscrape.com
# ---------------------------------------------------------------------------

PAGE_1_HTML = """
<html><body>
  <div class="quote">
    <span class="text">Stay hungry stay foolish</span>
    <small class="author">Steve Jobs</small>
    <a class="tag">inspirational</a>
    <a class="tag">life</a>
  </div>
  <ul class="pager"><li class="next"><a href="/page/2/">Next</a></li></ul>
</body></html>
"""

PAGE_2_HTML = """
<html><body>
  <div class="quote">
    <span class="text">Be the change you wish to see</span>
    <small class="author">Gandhi</small>
    <a class="tag">change</a>
  </div>
</body></html>
"""
# empty page
PAGE_NO_QUOTES_HTML = """
<html><body></body></html>
"""

# PAGE_1_HTML has a Next button so the crawler always requests a second page.
# These tests only care about content extraction from a single page, so they
# pass PAGE_1_HTML then PAGE_2_HTML (which has no Next button) and inspect page 1.
PAGE_1_URL = "https://quotes.toscrape.com/"


def _response(html, status_code=200):
    """Return a mock requests.Response with the given HTML as content."""
    mock = MagicMock()
    mock.content = html.encode("utf-8")
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError(str(status_code))
    else:
        mock.raise_for_status.return_value = None
    return mock


def _crawl(*pages_html):
    """Run crawl() against a sequence of fake HTML pages, suppressing I/O."""
    responses = [_response(html) for html in pages_html] + [_response(PAGE_NO_QUOTES_HTML)]
    with patch("src.crawler.requests.get", side_effect=responses), \
         patch("src.crawler.time.sleep"), \
         patch("src.crawler.tqdm", return_value=MagicMock()):
        return crawl("https://quotes.toscrape.com")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_crawl_returns_dict_of_urls_to_quotes():
    # tests if crawling returns a dict of urls and quotes
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    assert isinstance(pages, dict)
    assert PAGE_1_URL in pages
    assert isinstance(pages[PAGE_1_URL], list)

def test_crawl_extracts_text_from_quote_spans():
    # tests if crawl ectracts a quote
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    quote = pages[PAGE_1_URL][0]
    assert quote["text"] == "Stay hungry stay foolish"

def test_crawl_extracts_author_from_small_tags():
    # tests if crawl extracts authour
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    quote = pages[PAGE_1_URL][0]
    assert quote["author"] == "Steve Jobs"

def test_crawl_extracts_tags_from_anchor_tags():
    # tests if crawl extracts tags
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    quote = pages[PAGE_1_URL][0]
    assert quote["tags"] == ["inspirational", "life"]

def test_crawl_follows_next_page_link():
    # tests if crawl follows the next page button
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    assert "https://quotes.toscrape.com/" in pages
    assert "https://quotes.toscrape.com/page/2/" in pages

def test_crawl_stops_when_no_next_button_present():
    # tests if crawl stops when there is no next page
    last_page = _crawl(PAGE_2_HTML)
    all_pages = _crawl(PAGE_1_HTML)
    assert len(last_page) == 1
    assert len(all_pages) == 2

def test_crawl_applies_politeness_delay_between_pages():
    # test if the politeness timeout is applied
    with patch("src.crawler.requests.get", side_effect=[_response(PAGE_1_HTML), _response(PAGE_2_HTML)]), \
         patch("src.crawler.time.sleep") as mock_sleep, \
         patch("src.crawler.tqdm", return_value=MagicMock()):
        crawl("https://quotes.toscrape.com")
    # sleep must be called once — between page 1 and page 2, but not after the last page
    mock_sleep.assert_called_once()

def test_crawl_handles_page_with_no_quotes():
    # test if a page with no quotes is empty
    pages = _crawl(PAGE_NO_QUOTES_HTML)
    assert pages["https://quotes.toscrape.com/"] == []

def test_crawl_retries_on_error_then_succeeds():
    # first attempt raises a connection error, second attempt succeeds
    side_effects = [
        requests.exceptions.ConnectionError("transient error"),
        _response(PAGE_1_HTML),
        _response(PAGE_2_HTML),
    ]
    with patch("src.crawler.requests.get", side_effect=side_effects), \
         patch("src.crawler.time.sleep"), \
         patch("src.crawler.tqdm", return_value=MagicMock()):
        pages = crawl("https://quotes.toscrape.com")
    assert PAGE_1_URL in pages

def test_crawl_raises_after_max_retries():
    # all attempts raise a connection error — expect RuntimeError with message
    with patch("src.crawler.requests.get", side_effect=requests.exceptions.ConnectionError("down")), \
         patch("src.crawler.time.sleep"), \
         patch("src.crawler.tqdm", return_value=MagicMock()):
        with pytest.raises(RuntimeError, match="Crawler failed due to connection error"):
            crawl("https://quotes.toscrape.com")

def test_crawl_raises_on_404_after_max_retries():
    # all attempts return 404 — expect RuntimeError with message
    with patch("src.crawler.requests.get", return_value=_response(PAGE_NO_QUOTES_HTML, status_code=404)), \
         patch("src.crawler.time.sleep"), \
         patch("src.crawler.tqdm", return_value=MagicMock()):
        with pytest.raises(RuntimeError, match="Crawler failed due to connection error"):
            crawl("https://quotes.toscrape.com")


# ---------------------------------------------------------------------------
# Cross-module tests
# ---------------------------------------------------------------------------

def test_crawl_all_quotes_have_required_fields():
    # tests that every quote on every page has text, author, and tags fields
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    for quotes in pages.values():
        for quote in quotes:
            assert "text" in quote and "author" in quote and "tags" in quote

def test_crawl_output_feeds_into_build_index():
    # tests that crawl output can be passed directly to build_index without errors
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    index = build_index(pages)
    assert isinstance(index, dict)
    assert len(index) > 0

def test_crawl_multi_page_quote_counts_are_correct():
    # tests that the number of quotes per page matches what was in the HTML
    pages = _crawl(PAGE_1_HTML, PAGE_2_HTML)
    assert len(pages["https://quotes.toscrape.com/"]) == 1
    assert len(pages["https://quotes.toscrape.com/page/2/"]) == 1


# ---------------------------------------------------------------------------
# Performance tests
# ---------------------------------------------------------------------------

def test_crawl_full_site_performance():
    # tests that a full crawl of the real site completes within 120 seconds;
    # includes genuine network latency and the 6-second politeness delay between pages
    start = time.time()
    result = crawl("https://quotes.toscrape.com")
    elapsed = time.time() - start
    assert len(result) > 0
    assert elapsed < 120.0, f"full site crawl took {elapsed:.2f}s — too slow"


# ---------------------------------------------------------------------------
# Integration tests (require --run-integration; hit the real site)
#
# These tests use 'real_pages' which are real pages crawled using the crawler
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_real_crawl_returns_multiple_pages(real_pages):
    # tests that the real site returns more than one page of quotes
    assert len(real_pages) > 1

@pytest.mark.integration
def test_real_crawl_all_quotes_have_required_fields(real_pages):
    # tests that every quote from the real site contains text, author, and tags
    for quotes in real_pages.values():
        for quote in quotes:
            assert "text" in quote and "author" in quote and "tags" in quote

@pytest.mark.integration
def test_real_crawl_quotes_have_non_empty_text_and_author(real_pages):
    # tests that text and author from the real site are non-empty strings
    for quotes in real_pages.values():
        for quote in quotes:
            assert len(quote["text"]) > 0
            assert len(quote["author"]) > 0

@pytest.mark.integration
def test_real_crawl_tags_are_lists_of_strings(real_pages):
    # tests that every tags field from the real site is a list of strings
    for quotes in real_pages.values():
        for quote in quotes:
            assert isinstance(quote["tags"], list)
            assert all(isinstance(t, str) for t in quote["tags"])
