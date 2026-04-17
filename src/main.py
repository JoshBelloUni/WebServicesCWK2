"""
main.py - Command-line interface for the search engine tool

Commands:
  build        - Crawl the website, build and save the index
  load         - Load the index from file
  print <word> - Print index entry for a word
  find <query> - Find pages containing query terms
"""

import os
from crawler import crawl
from indexer import build_index, save_index, load_index
from search import print_word, find_pages

BASE_URL = "https://quotes.toscrape.com/"
INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "index.json")


def main():
    """Run the search engine shell."""
    index = {}
    print("Search Engine Tool — type 'help' for commands, 'quit' to exit.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue

        parts = user_input.split()
        command = parts[0].lower()

        if command == "build":
            print("Crawling website...")
            pages = crawl(BASE_URL)
            print(f"Crawled {len(pages)} pages. Building index...")
            index = build_index(pages)
            save_index(index, INDEX_PATH)
            print(f"Index built and saved to {INDEX_PATH}.")

        elif command == "load":
            index = load_index(INDEX_PATH)
            if index:
                print(f"Index loaded from {INDEX_PATH}.")
            else:
                print("No index found. Run 'build' first.")

        elif command == "print":
            if len(parts) < 2:
                print("Usage: print <word>")
            elif not index:
                print("No index loaded. Run 'build' or 'load' first.")
            else:
                print_word(index, parts[1])

        elif command == "find":
            if len(parts) < 2:
                print("Usage: find <word> [word ...]")
            elif not index:
                print("No index loaded. Run 'build' or 'load' first.")
            else:
                query = " ".join(parts[1:])
                find_pages(index, query)

        elif command == "help":
            print("Commands:")
            print("  build        - Crawl the website and build the index")
            print("  load         - Load the index from file")
            print("  print <word> - Print index entry for a word")
            print("  find <query> - Find pages containing query terms")
            print("  quit         - Exit the tool")

        elif command in ("quit", "exit"):
            print("Exiting.")
            break

        else:
            print(f"Unknown command: '{command}'. Type 'help' for commands.")


if __name__ == "__main__":
    main()
