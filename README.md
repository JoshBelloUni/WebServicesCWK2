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
# Unit, cross-module, and performance tests
python -m pytest tests/

# Include integration tests (hits the real site — takes ~60s)
python -m pytest tests/ --run-integration
```

---

### test_crawler.py

#### Unit
| Test | Description |
|------|-------------|
| `test_crawl_returns_dict_of_urls_to_quotes` | Returns a dict mapping URLs to lists of quotes |
| `test_crawl_extracts_text_from_quote_spans` | Extracts quote text from `<span class="text">` |
| `test_crawl_extracts_author_from_small_tags` | Extracts author from `<small class="author">` |
| `test_crawl_extracts_tags_from_anchor_tags` | Extracts tags from `<a class="tag">` |
| `test_crawl_follows_next_page_link` | Follows the Next button to subsequent pages |
| `test_crawl_stops_when_no_next_button_present` | Stops crawling when no Next button is found |
| `test_crawl_applies_politeness_delay_between_pages` | Applies a sleep delay between page requests |
| `test_crawl_handles_page_with_no_quotes` | Returns an empty list for pages with no quotes |

#### Cross-module
| Test | Description |
|------|-------------|
| `test_crawl_all_quotes_have_required_fields` | Every quote across all pages has text, author, and tags |
| `test_crawl_output_feeds_into_build_index` | Crawl output passes directly into `build_index` without errors |
| `test_crawl_multi_page_quote_counts_are_correct` | Quote count per page matches what was in the HTML |

#### Performance
| Test | Description |
|------|-------------|
| `test_crawl_full_site_performance` | Full crawl of the real site completes within 120s (includes network and politeness delay) |

#### Integration
| Test | Description |
|------|-------------|
| `test_real_crawl_returns_multiple_pages` | Real site returns more than one page of quotes |
| `test_real_crawl_all_quotes_have_required_fields` | All real quotes contain text, author, and tags |
| `test_real_crawl_quotes_have_non_empty_text_and_author` | Real text and author fields are non-empty strings |
| `test_real_crawl_tags_are_lists_of_strings` | Real tags field is a list of strings |

---

### test_indexer.py

#### Unit
| Test | Description |
|------|-------------|
| `test_build_index_includes_words_from_quotes` | Words from quotes appear as keys in the index |
| `test_build_index_lowercases_all_words` | All words stored in lowercase |
| `test_build_index_strips_punctuation` | Punctuation removed before indexing |
| `test_build_index_records_word_frequency` | Word frequency per page is counted correctly |
| `test_build_index_records_quote_index_in_positions` | Quote index is recorded in each position entry |
| `test_build_index_records_word_position_within_quote` | Word position within the quote is recorded |
| `test_build_index_maps_word_to_multiple_pages` | Words on multiple pages are mapped to all of them |
| `test_build_index_returns_empty_dict_for_no_pages` | Empty input returns an empty dict |
| `test_save_index_creates_json_file` | `save_index` creates a JSON file on disk |
| `test_load_index_returns_empty_dict_when_file_missing` | Returns empty dict when file does not exist |
| `test_load_index_restores_saved_data` | Loaded index matches the original saved index |

#### Cross-module
| Test | Description |
|------|-------------|
| `test_full_pipeline_build_save_load_search` | Build → save → load → search returns correct results |
| `test_search_results_identical_before_and_after_round_trip` | Search results are identical before and after save/load |

#### Performance
| Test | Description |
|------|-------------|
| `test_build_index_performance_large_dataset` | Indexes 1000 quotes in under 2 seconds |
| `test_save_load_performance_large_index` | Saves and loads a large index each in under 1 second |

#### Integration
| Test | Description |
|------|-------------|
| `test_real_build_index_contains_common_words` | Real crawl data produces entries for common quote words |
| `test_real_index_word_entries_have_correct_structure` | Every real index entry has a valid frequency and positions list |
| `test_real_save_and_load_preserves_all_words` | Save/load preserves all word keys from real crawled data |

---

### test_search.py

#### Unit
| Test | Description |
|------|-------------|
| `test_find_pages_returns_urls_containing_query_word` | Returns URLs where the query word appears |
| `test_find_pages_returns_all_pages_when_word_spans_multiple_pages` | Returns all pages containing the word |
| `test_find_pages_returns_intersection_for_multi_word_query` | Multi-word query returns only pages containing all words |
| `test_find_pages_returns_empty_list_when_word_not_in_index` | Missing word returns an empty list |
| `test_find_pages_returns_empty_list_for_blank_query` | Blank query returns an empty list |
| `test_find_pages_returns_sorted_urls` | Results are returned in sorted order |
| `test_print_word_outputs_frequency_and_url` | Prints URL and frequency for a found word |
| `test_print_word_outputs_not_found_for_missing_word` | Prints "not found" for a word not in the index |
| `test_print_word_normalises_input_before_lookup` | Strips punctuation and lowercases input before lookup |

#### Cross-module
| Test | Description |
|------|-------------|
| `test_find_pages_on_index_built_from_pages` | `find_pages` works on an index built from real page data |
| `test_find_pages_multi_word_query_on_built_index` | Multi-word intersection search works on a built index |
| `test_find_pages_word_unique_to_second_page_on_built_index` | Words unique to one page only return that page |

#### Performance
| Test | Description |
|------|-------------|
| `test_find_pages_performance_single_word_large_index` | Single-word search on a 5000-word × 50-page index in under 0.5s |
| `test_find_pages_performance_multi_word_large_index` | Three-word intersection search on a large index in under 0.5s |

#### Integration
| Test | Description |
|------|-------------|
| `test_real_find_pages_returns_results_for_common_word` | Common word search returns results from the real index |
| `test_real_find_pages_multi_word_is_subset_of_single_word` | Multi-word results are a subset of single-word results |
| `test_real_find_pages_missing_word_returns_empty` | Nonsense word returns an empty list on the real index |
| `test_real_print_word_outputs_url_and_frequency` | `print_word` outputs a URL and frequency for a real word |

---

### test_tag_explorer.py

#### Unit
| Test | Description |
|------|-------------|
| `test_tokenize_lowercases_input` | Input text is lowercased |
| `test_tokenize_strips_punctuation` | Punctuation is removed from tokens |
| `test_tokenize_removes_stopwords` | Common stopwords are excluded |
| `test_tokenize_removes_single_character_tokens` | Single-character tokens are removed |
| `test_tokenize_returns_list` | Returns a list of strings |
| `test_build_tag_index_returns_empty_dict_for_empty_pages` | Empty pages input returns an empty dict |
| `test_build_tag_index_creates_key_for_every_tag` | Every tag from the pages gets an index key |
| `test_build_tag_index_creates_no_extra_tag_keys` | No duplicate or extra tag keys are created |
| `test_build_tag_index_sorts_words_by_score_descending` | Words within each tag are sorted by TF-IDF score descending |
| `test_build_tag_index_ranks_unique_word_above_shared_word` | Words unique to a tag score higher than words shared across tags |
| `test_build_tag_index_excludes_stopwords` | Stopwords are not included in the tag index |
| `test_build_tag_index_produces_positive_scores` | All TF-IDF scores are positive |
| `test_save_and_load_tag_index_round_trip` | Saved and loaded tag index matches the original |
| `test_load_tag_index_returns_empty_dict_when_file_missing` | Returns empty dict when file does not exist |
| `test_list_tags_prints_not_loaded_message_for_empty_index` | Prints a "not loaded" message when given an empty index |
| `test_list_tags_prints_all_tag_names` | All tag names are printed |
| `test_explore_tag_prints_not_found_for_unknown_tag` | Prints "not found" for an unknown tag |
| `test_explore_tag_prints_not_loaded_message_for_empty_index` | Prints a "not loaded" message for an empty index |
| `test_explore_tag_prints_characteristic_words_for_valid_tag` | Prints characteristic words for a valid tag |

#### Cross-module
| Test | Description |
|------|-------------|
| `test_full_tag_pipeline_build_save_load_explore` | Build → save → load → explore a tag produces correct output |
| `test_full_tag_pipeline_list_tags_after_load` | Tags listed after a save/load round trip match the original |
| `test_loaded_tag_index_scores_match_original` | TF-IDF scores in a reloaded index are numerically identical |

#### Performance
| Test | Description |
|------|-------------|
| `test_build_tag_index_performance_large_dataset` | Builds a tag index from 1000 quotes in under 2 seconds |
| `test_explore_tag_performance_large_index` | Explores a tag in a large index in under 0.5 seconds |

#### Integration
| Test | Description |
|------|-------------|
| `test_real_build_tag_index_contains_tags` | Real site produces a non-empty tag index |
| `test_real_tag_index_entries_are_sorted_by_score` | Real tag index entries are sorted by score descending |
| `test_real_list_tags_prints_all_tag_names` | `list_tags` prints every tag name from the real index |
| `test_real_explore_tag_prints_characteristic_words` | `explore_tag` prints the tag name and its top word |

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
