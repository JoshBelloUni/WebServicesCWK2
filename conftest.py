import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests against the real quotes.toscrape.com site",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: requires network access to quotes.toscrape.com")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-integration"):
        skip = pytest.mark.skip(reason="use --run-integration to run against the real site")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)


@pytest.fixture(scope="session")
def real_pages():
    # crawls the real quotes.toscrape.com once per test session; sleep mocked to skip politeness delay
    from src.crawler import crawl
    with patch("src.crawler.time.sleep"):
        return crawl("https://quotes.toscrape.com")


def pytest_runtest_logreport(report):
    if report.when == "call" and report.passed:
        print(f"  PASSED: {report.nodeid}", file=sys.__stdout__, flush=True)
