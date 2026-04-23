"""Exhaustive version: scan the Wikipedia page-title dump for gender terms.

The MediaWiki search API caps results at 10,000, which truncates common
words like "women" and "men". This script instead downloads the official
dump of *every* article title in the main namespace and scans it locally,
which is both faster and fully comprehensive.

Source: https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz
Format: one title per line, spaces encoded as underscores, UTF-8.

Outputs (in ./output/):
  - starts_with_women_in.csv / starts_with_men_in.csv
  - contains_women.csv / contains_men.csv / contains_female.csv / contains_male.csv
  - all_matches.csv      (title, pattern)
  - unique_titles.csv    (deduplicated across all buckets)
"""

from __future__ import annotations

import csv
import gzip
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Iterable

DUMP_URL = "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz"
DUMP_PATH = Path("enwiki-latest-all-titles-in-ns0.gz")

# Dump titles use underscores for spaces, so we match on underscores/start/end
# as word boundaries. \b works on underscores (they're "word" chars), so we
# need to normalise: convert underscores to spaces before regex matching.
WORD_PATTERNS = {
    "women": re.compile(r"\bwomen\b", re.IGNORECASE),
    "men":   re.compile(r"\bmen\b",   re.IGNORECASE),
    "female": re.compile(r"\bfemale\b", re.IGNORECASE),
    "male":   re.compile(r"\bmale\b",   re.IGNORECASE),
}


def download_dump(path: Path = DUMP_PATH) -> Path:
    if path.exists() and path.stat().st_size > 1_000_000:
        print(f"Using cached dump: {path} ({path.stat().st_size / 1e6:.1f} MB)")
        return path
    print(f"Downloading {DUMP_URL} ...")
    with urllib.request.urlopen(DUMP_URL) as resp, path.open("wb") as out:
        shutil.copyfileobj(resp, out)
    print(f"  downloaded {path.stat().st_size / 1e6:.1f} MB")
    return path


def iter_titles(path: Path):
    """Yield every main-namespace article title from the dump.

    The first line is a header ("page_title"); skip it. Underscores are
    converted to spaces so titles match what users see on Wikipedia.
    """
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline()  # skip "page_title" header
        if not header.startswith("page_title"):
            # Older dumps may not have a header; rewind.
            f.seek(0)
        for line in f:
            title = line.rstrip("\n").replace("_", " ")
            if title:
                yield title


def scan(path: Path) -> dict[str, set[str]]:
    buckets: dict[str, set[str]] = {
        "starts_with_women_in": set(),
        "starts_with_men_in":   set(),
        "contains_women":       set(),
        "contains_men":         set(),
        "contains_female":      set(),
        "contains_male":        set(),
    }

    women_re  = WORD_PATTERNS["women"]
    men_re    = WORD_PATTERNS["men"]
    female_re = WORD_PATTERNS["female"]
    male_re   = WORD_PATTERNS["male"]

    total = 0
    for title in iter_titles(path):
        total += 1
        if total % 1_000_000 == 0:
            print(f"  scanned {total:,} titles ...")

        # Exact prefix checks (case-sensitive to match article-title convention).
        if title.startswith("Women in "):
            buckets["starts_with_women_in"].add(title)
        if title.startswith("Men in "):
            buckets["starts_with_men_in"].add(title)

        # Word-boundary containment checks (case-insensitive).
        # Fast-path: only run regex if the lowercase substring is present.
        lower = title.lower()
        if "women" in lower and women_re.search(title):
            buckets["contains_women"].add(title)
        # "men" is also a substring of "women", "omen", etc. — regex handles that.
        if "men" in lower and men_re.search(title):
            buckets["contains_men"].add(title)
        if "female" in lower and female_re.search(title):
            buckets["contains_female"].add(title)
        # "male" is a substring of "female" — regex \bmale\b rejects that.
        if "male" in lower and male_re.search(title):
            buckets["contains_male"].add(title)

    print(f"  scanned {total:,} titles total")
    return buckets


def write_csv(path: Path, rows: Iterable[tuple[str, ...]], header: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path}")


def main(out_dir: Path = Path("output")) -> None:
    dump = download_dump()
    print("Scanning dump ...")
    buckets = scan(dump)

    print("\nCounts:")
    for name, titles in buckets.items():
        print(f"  {name}: {len(titles):,}")

    for name, titles in buckets.items():
        write_csv(
            out_dir / f"{name}.csv",
            ((t,) for t in sorted(titles)),
            header=("title",),
        )

    combined = sorted(
        {(title, name) for name, titles in buckets.items() for title in titles}
    )
    write_csv(out_dir / "all_matches.csv", combined, header=("title", "pattern"))

    all_titles = set().union(*buckets.values())
    write_csv(
        out_dir / "unique_titles.csv",
        ((t,) for t in sorted(all_titles)),
        header=("title",),
    )
    print(f"\nTotal unique titles across all patterns: {len(all_titles):,}")


if __name__ == "__main__":
    sys.exit(main())
