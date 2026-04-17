"""
crawler.py - Web crawler for quotes.toscrape.com
"""

import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

POLITENESS_WINDOW = 6  # seconds between requests


def crawl(base_url: str) -> dict:
    """Crawl all pages of the target website and return raw page data."""
    pages = {}
    next_path = "/"

    with tqdm(desc="Crawling", unit=" pages") as pbar:
        while next_path:
            url = base_url.rstrip("/") + next_path
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            quotes = []
            for quote in soup.find_all("div", class_="quote"):
                text = quote.find("span", class_="text").get_text()
                author = quote.find("small", class_="author").get_text()
                tags = [tag.get_text() for tag in quote.find_all("a", class_="tag")]
                quotes.append({"text": text, "author": author, "tags": tags})

            pages[url] = quotes
            pbar.update(1)

            # follow the "Next" button if it exists
            next_btn = soup.find("li", class_="next")
            next_path = next_btn.find("a")["href"] if next_btn else None

            if next_path:
                time.sleep(POLITENESS_WINDOW)

    return pages
