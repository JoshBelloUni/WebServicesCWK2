"""
crawler.py - Web crawler for quotes.toscrape.com
"""

import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

POLITENESS_WINDOW = 6  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 2        # seconds between retry attempts
REQUEST_TIMEOUT = 10   # seconds before a request times out


def _fetch_with_retry(url: str) -> requests.Response:
    """Fetch a URL, retrying up to MAX_RETRIES times on any error."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(
                    f"Crawler failed due to connection error after {MAX_RETRIES} attempts: {url}"
                )


def crawl(base_url: str) -> dict:
    """Crawl all pages of the target website and return raw page data."""
    pages = {}
    next_path = "/"

    with tqdm(desc="Crawling", unit=" pages") as pbar:
        while next_path:
            url = base_url.rstrip("/") + next_path
            response = _fetch_with_retry(url)
            soup = BeautifulSoup(response.content, "html.parser")

            quotes = []
            for quote in soup.find_all("div", class_="quote"):
                text = quote.find("span", class_="text").get_text()
                author = quote.find("small", class_="author").get_text()
                tags = [tag.get_text() for tag in quote.find_all("a", class_="tag")]
                quotes.append({"text": text, "author": author, "tags": tags})

            pages[url] = quotes
            pbar.update(1)

            # follow the "Next" button
            next_btn = soup.find("li", class_="next")
            next_path = next_btn.find("a")["href"] if next_btn else None

            if next_path:
                time.sleep(POLITENESS_WINDOW)

    return pages
