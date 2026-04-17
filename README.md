# COMP3011 Coursework 2 - Search Engine Tool

A command-line search engine that crawls quotes.toscrape.com, builds an inverted index, and supports querying.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

### Commands

| Command | Description |
|---------|-------------|
| `build` | Crawl the website, build the index, and save to file |
| `load` | Load a previously built index from file |
| `print <word>` | Print the inverted index entry for a word |
| `find <query>` | Find all pages containing the query term(s) |

### Examples

```
> build
> load
> print nonsense
> find indifference
> find good friends
```

## Testing

```bash
python -m pytest tests/
```

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
