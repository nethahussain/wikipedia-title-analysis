"""Filter the find_women_men_in.py output down to live articles only.

Reads:
    output/starts_with_women_in.csv
    output/starts_with_men_in.csv
Writes (only rows where is_redirect == "no"):
    output/starts_with_women_in_articles_only.csv
    output/starts_with_men_in_articles_only.csv

Each output file has a single column: title.

Run `python3 find_women_men_in.py` first to produce the input files.
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path("output")

PAIRS = [
    ("starts_with_women_in.csv", "starts_with_women_in_articles_only.csv"),
    ("starts_with_men_in.csv",   "starts_with_men_in_articles_only.csv"),
]


def filter_articles(src: Path, dst: Path) -> None:
    if not src.exists():
        raise SystemExit(f"Missing {src}. Run find_women_men_in.py first.")
    kept = 0
    with src.open(newline="", encoding="utf-8") as fin, \
         dst.open("w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout)
        writer.writerow(("title",))
        for row in reader:
            if row["is_redirect"].strip().lower() == "no":
                writer.writerow((row["title"],))
                kept += 1
    print(f"  {src.name} -> {dst.name}: {kept} articles")


def main() -> None:
    for src_name, dst_name in PAIRS:
        filter_articles(OUT_DIR / src_name, OUT_DIR / dst_name)


if __name__ == "__main__":
    main()
