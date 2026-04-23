"""Find every Wikipedia article starting with "Women in" or "Men in".

Steps:
  1. Download the Wikipedia page-title dump (~108 MB, cached after first run).
  2. Scan all ~19 million main-namespace titles for case-insensitive matches
     on the prefixes "Women in " and "Men in " — this includes stylised
     variants like "Men In Black".
  3. Query the MediaWiki API in batches of 50 to determine which matches
     are redirects and what they point to.
  4. Write two CSVs:
        output/starts_with_women_in.csv
        output/starts_with_men_in.csv
     Each has three columns: title, is_redirect (yes/no), redirect_target.

Usage:
    pip3 install requests
    python3 find_women_men_in.py

Re-runs are fast because the 108 MB dump is cached in the current directory.
Delete `enwiki-latest-all-titles-in-ns0.gz` to force a fresh download.
"""

from __future__ import annotations

import csv
import gzip
import shutil
import time
import urllib.request
from pathlib import Path
from typing import Iterable

import requests

DUMP_URL = "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz"
DUMP_PATH = Path("enwiki-latest-all-titles-in-ns0.gz")
OUT_DIR = Path("output")

API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "WikipediaTitleAnalysis/1.0 (contact: you@example.com)"
BATCH_SIZE = 50  # API caps titles= at 50 for unprivileged users

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


# --- 1. Download the dump ---------------------------------------------------

def download_dump() -> Path:
    if DUMP_PATH.exists() and DUMP_PATH.stat().st_size > 1_000_000:
        print(f"Using cached dump: {DUMP_PATH} ({DUMP_PATH.stat().st_size / 1e6:.1f} MB)")
        return DUMP_PATH
    print(f"Downloading {DUMP_URL} ...")
    with urllib.request.urlopen(DUMP_URL) as resp, DUMP_PATH.open("wb") as out:
        shutil.copyfileobj(resp, out)
    print(f"  downloaded {DUMP_PATH.stat().st_size / 1e6:.1f} MB")
    return DUMP_PATH


# --- 2. Scan dump for prefix matches ---------------------------------------

def collect_prefix_matches(prefix: str) -> list[str]:
    """Every main-ns title whose lowercase form starts with `prefix`."""
    prefix = prefix.lower()
    matches: list[str] = []
    with gzip.open(DUMP_PATH, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline()
        if not header.startswith("page_title"):
            f.seek(0)  # older dumps have no header
        for line in f:
            title = line.rstrip("\n").replace("_", " ")
            if title.lower().startswith(prefix):
                matches.append(title)
    return sorted(matches)


# --- 3. Resolve redirects via API ------------------------------------------

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


def chunks(xs: list[str], n: int):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def resolve_redirects(titles: list[str]) -> dict[str, tuple[bool, str]]:
    """Return {title: (is_redirect, target_or_empty)}.

    Uses action=query&redirects=1 — the response's `redirects` array lists
    every title that was a redirect plus its target. Titles absent from
    that array are live pages (or missing/invalid).
    """
    result: dict[str, tuple[bool, str]] = {t: (False, "") for t in titles}
    total_batches = (len(titles) + BATCH_SIZE - 1) // BATCH_SIZE

    for i, batch in enumerate(chunks(titles, BATCH_SIZE), start=1):
        data = api_get({
            "action": "query",
            "titles": "|".join(batch),
            "redirects": "1",
            "prop": "info",
        })
        q = data.get("query", {})

        # Direct redirect mapping.
        for red in q.get("redirects", []):
            src, dst = red.get("from", ""), red.get("to", "")
            if src in result:
                result[src] = (True, dst)

        # The API may normalise casing (e.g. "MEN IN X" -> "Men in X") before
        # checking redirects. Walk normalization map to propagate correctly.
        for norm in q.get("normalized", []):
            orig, new = norm.get("from", ""), norm.get("to", "")
            if orig in result:
                for red in q.get("redirects", []):
                    if red.get("from") == new:
                        result[orig] = (True, red.get("to", ""))
                        break

        if i % 5 == 0 or i == total_batches:
            print(f"  resolved {i}/{total_batches} batches")

    return result


# --- 4. Write CSVs ---------------------------------------------------------

def write_csv(path: Path, rows: Iterable[tuple[str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("title", "is_redirect", "redirect_target"))
        w.writerows(rows)
    print(f"  wrote {path}")


def process(prefix: str, out_name: str) -> None:
    print(f"\n=== prefix: {prefix!r} ===")
    titles = collect_prefix_matches(prefix)
    print(f"  {len(titles)} titles in dump (case-insensitive)")
    redirs = resolve_redirects(titles)
    rows = [
        (t, "yes" if redirs[t][0] else "no", redirs[t][1])
        for t in titles
    ]
    n_red = sum(1 for t in titles if redirs[t][0])
    print(f"  {n_red} redirects / {len(titles) - n_red} live articles")
    write_csv(OUT_DIR / out_name, rows)


def main() -> None:
    download_dump()
    process("women in ", "starts_with_women_in.csv")
    process("men in ",   "starts_with_men_in.csv")


if __name__ == "__main__":
    main()
