# Wikipedia title analysis: "Women in…" / "Men in…"

Code and data for an analysis of English Wikipedia articles whose titles
begin with "Women in", "Men in", "Females in", or "Males in".

The analysis is written up in [`REPORT.md`](REPORT.md).

## What's here

### Scripts (run in this order)

| Script                          | Purpose |
| ------------------------------- | ------- |
| `fetch_gender_titles_dump.py`   | Download the ~108 MB Wikipedia page-title dump and count broad "contains women/men/female/male" matches. |
| `find_women_men_in.py`          | Extract titles starting with "Women in"/"Men in" (case-insensitive) and flag redirects via the MediaWiki API. |
| `articles_only.py`              | Filter the above to live articles (no redirects). |
| `classify_articles.py`          | Fetch each article's first sentence and classify it by type (topic, film, book, organization, …). |
| `combine_topic_articles.py`     | Merge women+men "topic" articles into one CSV. |
| `subclassify_topics.py`         | Sub-classify topic articles by theme (geography, politics, military, religion, STEM, …). |
| `find_males_females_in.py`      | Same pipeline for "Females in"/"Males in" prefixes. |

An older API-only prototype (`fetch_gender_titles.py`) is kept for
reference but is superseded by the dump-based scripts — the search API
caps results at 10,000 per query, which truncated common words.

### Data (`output/`)

- `all_matches.csv`, `unique_titles.csv` — broad "contains…" matches.
- `contains_women.csv`, `contains_men.csv`, `contains_female.csv`,
  `contains_male.csv` — per-word results.
- `starts_with_women_in.csv`, `starts_with_men_in.csv` — titles +
  redirect flag + redirect target.
- `starts_with_women_in_articles_only.csv`,
  `starts_with_men_in_articles_only.csv` — redirects removed.
- `starts_with_women_in_classified.csv`,
  `starts_with_men_in_classified.csv` — adds `category` + `first_sentence`.
- `starts_with_women_in_topic_only.csv`,
  `starts_with_men_in_topic_only.csv` — just the real topic articles.
- `topic_articles_combined.csv` — women + men topic articles in one file.
- `topic_articles_subclassified.csv` — adds thematic `subcategory`.
- `starts_with_females_in.csv`, `starts_with_males_in.csv` — all 12
  "Females/Males in" titles (every one is a redirect).

## Reproducing the analysis

```bash
pip3 install requests
python3 fetch_gender_titles_dump.py        # downloads the 108 MB dump
python3 find_women_men_in.py
python3 articles_only.py
python3 classify_articles.py
python3 combine_topic_articles.py
python3 subclassify_topics.py
python3 find_males_females_in.py
```

The dump file (`enwiki-latest-all-titles-in-ns0.gz`) is gitignored. It is
re-downloaded on first run and cached thereafter.

## Caveats

Keyword-based classification is not perfect; the `first_sentence` column
in each `*_classified.csv` is included so that any reader can spot-check
the labels and re-bucket if needed. The script `classify_articles.py`
uses ordered regex rules — see the top of that file for the rule list.
