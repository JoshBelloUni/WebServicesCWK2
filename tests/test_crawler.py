"""
test_crawler.py - Tests for the crawler module
"""

import pytest
from unittest.mock import patch, MagicMock
from src.crawler import crawl

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


def _response(html):
    """Return a mock requests.Response with the given HTML as content."""
    mock = MagicMock()
    mock.content = html.encode("utf-8")
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
