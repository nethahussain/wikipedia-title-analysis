"""Fetch Wikipedia article titles matching gender-related patterns.

Patterns collected:
  1. Titles starting with "Women in ..." or "Men in ..."
  2. Titles containing the word "women" or "men"
  3. Titles containing the word "female" or "male"

Uses the MediaWiki API. Results are deduplicated and written to CSV files
(one per pattern) plus a combined CSV with a "pattern" column.
"""

from __future__ import annotations

import csv
import re
import time
from pathlib import Path
from typing import Iterable, Iterator

import requests

API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "WikipediaTitleAnalysis/1.0 (contact: user@example.com)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

# Word-boundary regexes applied to the title when filtering "contains" searches.
# This excludes false positives like "Amendment" (contains "men") or "Women"
# when we only want "men", etc.
WORD_PATTERNS = {
    "women": re.compile(r"\bwomen\b", re.IGNORECASE),
    "men":   re.compile(r"\bmen\b",   re.IGNORECASE),
    "female": re.compile(r"\bfemale\b", re.IGNORECASE),
    "male":   re.compile(r"\bmale\b",   re.IGNORECASE),
}


def api_get(params: dict) -> dict:
    """GET the MediaWiki API with basic retry."""
    params = {"format": "json", "formatversion": "2", **params}
    for attempt in range(5):
        try:
            r = SESSION.get(API_URL, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            wait = 2 ** attempt
            print(f"  request failed ({e}); retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError("API request failed after 5 attempts")


def iter_allpages(prefix: str) -> Iterator[str]:
    """Yield every article title in namespace 0 starting with `prefix`.

    Uses list=allpages with apprefix, which is exact prefix matching and
    returns results paginated in batches of 500.
    """
    apcontinue: str | None = None
    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "apprefix": prefix,
            "apnamespace": 0,
            "apfilterredir": "nonredirects",
            "aplimit": "max",
        }
        if apcontinue:
            params["apcontinue"] = apcontinue
        data = api_get(params)
        for page in data.get("query", {}).get("allpages", []):
            yield page["title"]
        cont = data.get("continue")
        if not cont:
            return
        apcontinue = cont.get("apcontinue")
        if not apcontinue:
            return


def iter_search(query: str) -> Iterator[str]:
    """Yield every article title matching a full-text search query.

    Uses list=search with srnamespace=0. We request srwhat=text so the
    engine searches titles and content; we filter to titles matching the
    target word afterwards. srlimit=500 is the max for unprivileged users.
    """
    sroffset = 0
    while True:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 0,
            "srlimit": "max",
            "sroffset": sroffset,
            "srinfo": "",
            "srprop": "",
        }
        data = api_get(params)
        hits = data.get("query", {}).get("search", [])
        if not hits:
            return
        for hit in hits:
            yield hit["title"]
        cont = data.get("continue")
        if not cont or "sroffset" not in cont:
            return
        sroffset = cont["sroffset"]
        # Wikipedia caps offset at 10000; stop gracefully.
        if sroffset >= 10000:
            print(f"  reached 10000-result cap for query: {query!r}")
            return


def collect_prefix(prefix: str) -> set[str]:
    print(f"Fetching titles starting with {prefix!r} ...")
    titles = set(iter_allpages(prefix))
    print(f"  -> {len(titles)} titles")
    return titles


def collect_word_in_title(word: str) -> set[str]:
    """Titles containing `word` as a whole word.

    Strategy: use `intitle:` search then post-filter with a word-boundary
    regex to drop substring matches (e.g. "Amendment" for "men").
    """
    print(f"Fetching titles containing the word {word!r} ...")
    pat = WORD_PATTERNS[word]
    titles: set[str] = set()
    for title in iter_search(f"intitle:{word}"):
        if pat.search(title):
            titles.add(title)
    print(f"  -> {len(titles)} titles after word-boundary filter")
    return titles


def write_csv(path: Path, rows: Iterable[tuple[str, ...]], header: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path}")


def main(out_dir: Path = Path("output")) -> None:
    buckets: dict[str, set[str]] = {
        "starts_with_women_in": collect_prefix("Women in "),
        "starts_with_men_in":   collect_prefix("Men in "),
        "contains_women":       collect_word_in_title("women"),
        "contains_men":         collect_word_in_title("men"),
        "contains_female":      collect_word_in_title("female"),
        "contains_male":        collect_word_in_title("male"),
    }

    # Per-pattern CSVs.
    for name, titles in buckets.items():
        write_csv(
            out_dir / f"{name}.csv",
            ((t,) for t in sorted(titles)),
            header=("title",),
        )

    # Combined CSV: one row per (title, pattern) pair so a title appearing
    # in multiple buckets is represented once per bucket.
    combined_rows = sorted(
        {(title, name) for name, titles in buckets.items() for title in titles}
    )
    write_csv(
        out_dir / "all_matches.csv",
        combined_rows,
        header=("title", "pattern"),
    )

    # Unique-title summary.
    all_titles = set().union(*buckets.values())
    write_csv(
        out_dir / "unique_titles.csv",
        ((t,) for t in sorted(all_titles)),
        header=("title",),
    )
    print(f"\nTotal unique titles across all patterns: {len(all_titles)}")


if __name__ == "__main__":
    main()
