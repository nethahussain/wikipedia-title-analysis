"""Combine the "topic" articles for Women in... and Men in... into one CSV.

Reads:
    output/starts_with_women_in_topic_only.csv
    output/starts_with_men_in_topic_only.csv
Writes:
    output/topic_articles_combined.csv
        columns: group (women/men), title, first_sentence

Run after classify_articles.py.
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path("output")
SOURCES = [
    ("women", OUT_DIR / "starts_with_women_in_topic_only.csv"),
    ("men",   OUT_DIR / "starts_with_men_in_topic_only.csv"),
]
DEST = OUT_DIR / "topic_articles_combined.csv"


def main() -> None:
    rows: list[tuple[str, str, str]] = []
    for group, src in SOURCES:
        if not src.exists():
            raise SystemExit(f"Missing {src}. Run classify_articles.py first.")
        with src.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append((group, row["title"], row.get("first_sentence", "")))

    # Stable sort: group first, then alphabetical title.
    rows.sort(key=lambda r: (r[0], r[1].lower()))

    with DEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("group", "title", "first_sentence"))
        w.writerows(rows)

    n_women = sum(1 for g, _, _ in rows if g == "women")
    n_men   = sum(1 for g, _, _ in rows if g == "men")
    print(f"wrote {DEST}: {len(rows)} rows ({n_women} women, {n_men} men)")


if __name__ == "__main__":
    main()
