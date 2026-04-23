"""Same pipeline as find_women_men_in.py + classify_articles.py, but for the
prefixes "Females in" and "Males in".

Because the match sets are tiny (12 titles total), the whole pipeline fits
in one script:

  1. Scan the cached page-title dump for case-insensitive prefix matches.
  2. Query the MediaWiki API to flag redirects.
  3. Fetch the first sentence of each live article.
  4. Apply the same keyword rules used in classify_articles.py.
  5. Write three CSVs per prefix:
        output/starts_with_<prefix>.csv              (title, is_redirect, redirect_target)
        output/starts_with_<prefix>_classified.csv   (title, category, first_sentence) [articles only]
        output/starts_with_<prefix>_topic_only.csv   (subset: category == "topic")

Assumes enwiki-latest-all-titles-in-ns0.gz is already cached in the cwd
(it was downloaded by fetch_gender_titles_dump.py / find_women_men_in.py).
"""

from __future__ import annotations

import csv
import gzip
import time
from pathlib import Path

import requests

# Re-use the RULES list from classify_articles.py rather than duplicating.
from classify_articles import RULES, classify, fetch_first_sentences  # type: ignore

DUMP_PATH = Path("enwiki-latest-all-titles-in-ns0.gz")
OUT_DIR = Path("output")

API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "WikipediaTitleAnalysis/1.0 (contact: you@example.com)"
BATCH_SIZE = 50

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def collect_prefix_matches(prefix: str) -> list[str]:
    prefix = prefix.lower()
    matches: list[str] = []
    with gzip.open(DUMP_PATH, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline()
        if not header.startswith("page_title"):
            f.seek(0)
        for line in f:
            title = line.rstrip("\n").replace("_", " ")
            if title.lower().startswith(prefix):
                matches.append(title)
    return sorted(matches)


def api_get(params: dict) -> dict:
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


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def resolve_redirects(titles: list[str]) -> dict[str, tuple[bool, str]]:
    result: dict[str, tuple[bool, str]] = {t: (False, "") for t in titles}
    for batch in chunks(titles, BATCH_SIZE):
        data = api_get({
            "action": "query",
            "titles": "|".join(batch),
            "redirects": "1",
            "prop": "info",
        })
        q = data.get("query", {})
        for red in q.get("redirects", []):
            src, dst = red.get("from", ""), red.get("to", "")
            if src in result:
                result[src] = (True, dst)
        for norm in q.get("normalized", []):
            orig, new = norm.get("from", ""), norm.get("to", "")
            if orig in result:
                for red in q.get("redirects", []):
                    if red.get("from") == new:
                        result[orig] = (True, red.get("to", ""))
                        break
    return result


def write_csv(path: Path, rows: list[tuple], header: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path}")


def process(prefix: str, slug: str) -> None:
    print(f"\n=== prefix: {prefix!r} ===")
    titles = collect_prefix_matches(prefix)
    print(f"  {len(titles)} titles in dump")
    if not titles:
        print("  (nothing to do)")
        return

    # Step 1: redirect flags
    redirs = resolve_redirects(titles)
    rows_all = [
        (t, "yes" if redirs[t][0] else "no", redirs[t][1])
        for t in titles
    ]
    n_red = sum(1 for t in titles if redirs[t][0])
    print(f"  {n_red} redirects / {len(titles) - n_red} live articles")
    write_csv(
        OUT_DIR / f"starts_with_{slug}.csv",
        rows_all,
        header=("title", "is_redirect", "redirect_target"),
    )

    # Step 2: classify the live articles
    live = [t for t in titles if not redirs[t][0]]
    if not live:
        print("  no live articles to classify")
        return
    sentences = fetch_first_sentences(live)

    classified = [
        (t, classify(sentences[t]), sentences[t])
        for t in live
    ]
    write_csv(
        OUT_DIR / f"starts_with_{slug}_classified.csv",
        classified,
        header=("title", "category", "first_sentence"),
    )

    topic = [row for row in classified if row[1] == "topic"]
    write_csv(
        OUT_DIR / f"starts_with_{slug}_topic_only.csv",
        topic,
        header=("title", "category", "first_sentence"),
    )

    from collections import Counter
    counts = Counter(c for _, c, _ in classified)
    print("  category breakdown:")
    for c, n in counts.most_common():
        print(f"    {c}: {n}")


def main() -> None:
    if not DUMP_PATH.exists():
        raise SystemExit(
            f"Missing {DUMP_PATH}. Run fetch_gender_titles_dump.py first."
        )
    process("females in ", "females_in")
    process("males in ",   "males_in")


if __name__ == "__main__":
    main()
