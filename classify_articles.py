"""Classify "Women in..." / "Men in..." articles by subject type.

Many articles with these prefixes are NOT about the social/cultural state
of men or women — they're films ("Men in Black"), songs, novels, video
games, etc. This script fetches the first sentence of each article from
the Wikipedia API and uses keyword rules to bucket them into categories:

    film, tv_series, music, book, play, poem, video_game, comic,
    artwork, organization, event, topic (default: about the real state
    of men/women)

Input  (from find_women_men_in.py + articles_only.py):
    output/starts_with_women_in_articles_only.csv
    output/starts_with_men_in_articles_only.csv

Output:
    output/starts_with_women_in_classified.csv
    output/starts_with_men_in_classified.csv
        columns: title, category, first_sentence

    output/starts_with_women_in_topic_only.csv
    output/starts_with_men_in_topic_only.csv
        -- same rows, but only category == "topic" (the real subject articles).
"""

from __future__ import annotations

import csv
import re
import time
from pathlib import Path

import requests

API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "WikipediaTitleAnalysis/1.0 (contact: you@example.com)"
EXTRACT_BATCH = 20  # prop=extracts caps multi-title at 20

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

OUT_DIR = Path("output")

# Ordered rules: first match wins. Patterns are applied to the lowercased
# first sentence. More-specific rules go first.
#
# Design notes:
#   - Many topic articles mention "film", "book", "song" in passing
#     (e.g. "Women have participated in radio broadcasting..."). To avoid
#     false positives we anchor most patterns on "is/was a [year]? [adj]* TYPE"
#     so we match the article's OWN description of itself, not incidental
#     mentions. A lookahead of up to ~60 chars between "is a" and the type
#     keyword lets adjectives/nationalities through without swallowing
#     entire sentences.
#   - "topic" is the default; anything unmatched falls through.

_IS_A = r"\b(?:is|was|are|were|refers to)\s+(?:a|an|the)\s+[^.]{0,80}?"
_THE  = r"\bthe\s+[^.]{0,80}?"

RULES: list[tuple[str, re.Pattern]] = [
    # Disambiguation pages: first sentence says "may/can refer to:"
    ("disambiguation", re.compile(r"\b(may|can) refer to\b")),

    # Theme park / attraction rides (check before film so "based on the film" doesn't match)
    ("attraction",  re.compile(_IS_A + r"\b(dark ride|theme park ride|amusement park ride|roller coaster|attraction at|ride at|ride located)\b")),

    # Film / short film / documentary / franchise
    ("film",        re.compile(_IS_A + r"\b(film|movie|motion picture|short subject|short film|feature film|film series|media franchise|franchise)\b")),
    ("film",        re.compile(_IS_A + r"\bdocumentary\b")),
    ("film",        re.compile(_IS_A + r"\bseries of\b[^.]{0,40}\bfilms\b")),
    ("film",        re.compile(r"\bdirected by\b[^.]{0,60}\b(film|movie)\b")),

    # Television
    ("tv_series",   re.compile(r"\b(television|tv)\s+(series|show|program|programme|miniseries|mini-series|drama|sitcom|special|film)\b")),
    ("tv_series",   re.compile(r"\b(web series|streaming series|anime series|animated series|cartoon series|drama series|comedy series|reality series|tvb)\b")),
    ("tv_series",   re.compile(_IS_A + r"\b(season|episode)\s+of\b")),

    # Music — specific self-descriptions only
    ("music",       re.compile(_IS_A + r"\b(song|single|album|ep|mixtape|soundtrack|studio album|live album|compilation album|extended play)\b")),
    ("music",       re.compile(_IS_A + r"\b(musical duo|musical group|music group|rock band|pop duo|folk duo|indie duo|vocal group|girl group|boy band|band)\b")),
    ("music",       re.compile(_IS_A + r"\b(opera|oratorio|symphony|concerto|sonata|ballet|cantata)\b")),

    # Books / written works
    ("book",        re.compile(_IS_A + r"\b(novel|novella|memoir|autobiography|biography|short story|anthology|children's book|picture book|textbook|career guide|self-help book|cookbook|non-fiction book|nonfiction book)\b")),
    ("book",        re.compile(_IS_A + r"\bbook (written|published|by|about|that|of)\b")),
    ("book",        re.compile(_IS_A + r"\b(book|guide)\s+(written|published|by)\b")),
    ("book",        re.compile(r"\bis a\s+\d{4}\b[^.]{0,40}\bbook\b")),  # "is a 2016 ... book"
    ("book",        re.compile(_IS_A + r"\b(comic book|graphic novel|manga|light novel)\b")),
    ("book",        re.compile(_IS_A + r"\b(translation|retelling|adaptation)\s+of\b")),  # literary work
    ("book",        re.compile(r"\bis a\b[^.]{0,40}\bbook of (poems|essays|short stories)\b")),

    # Theatre
    ("play",        re.compile(_IS_A + r"\b(stage play|theatrical production|musical theatre|one-act|two-act|three-act|broadway musical|off-broadway)\b")),
    ("play",        re.compile(_IS_A + r"\bplay\s+(written|by|that|which)\b")),
    ("play",        re.compile(r"\bis a\s+\d{4}\b[^.]{0,40}\bplay\b")),  # "is a 1998 play"

    # Poetry
    ("poem",        re.compile(_IS_A + r"\b(poem|sonnet|epic poem|poetry collection|book of poetry)\b")),

    # Games
    ("video_game",  re.compile(r"\b(video game|video-game|mobile game|arcade game|computer game|console game)\b")),
    ("video_game",  re.compile(_IS_A + r"\b(role-playing game|rpg|board game|card game|tabletop game)\b")),

    # Comics (non-book)
    ("comic",       re.compile(r"\b(comic strip|comic series|webcomic|comic book character)\b")),

    # Visual art
    ("artwork",     re.compile(_IS_A + r"\b(painting|sculpture|statue|photograph|photo series|art installation|artwork|mural|fresco|drawing|lithograph|etching|engraving)\b")),
    ("artwork",     re.compile(r"\boil on canvas\b")),
    ("artwork",     re.compile(_IS_A + r"\b(postage stamp|stamp series|commemorative stamp)\b")),

    # Organizations — require explicit self-description to avoid catching
    # articles like "Women in German history" that merely mention "organization"
    ("organization",re.compile(_IS_A + r"\b(organi[sz]ation|ngo|non-profit|nonprofit|charity|association|society|foundation|institute|network|coalition|advocacy group|trade union|union|federation|club|committee|caucus)\b")),
    ("organization",re.compile(_IS_A + r"\b(company|corporation|firm|media company|startup|agency|consultancy|publisher)\b")),
    ("organization",re.compile(_IS_A + r"\b(magazine|journal|newspaper|publication|periodical|blog|website|podcast|radio (show|program|programme)|television (show|channel|network))\b")),
    ("organization",re.compile(_IS_A + r"\b(distribution (centre|center)|art gallery|cultural (centre|center)|research (centre|center|institute))\b")),

    # Events / campaigns / awards
    ("event",       re.compile(_IS_A + r"\b(conference|festival|award|awards|awards ceremony|exhibition|campaign|protest|march|initiative)\b")),
    ("event",       re.compile(r"\b(is|are)\s+(a|an|the)?\s*(set of\s+)?\b(awards|honors|honours)\b")),  # "The X Awards are a set of awards..."
]


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


def fetch_first_sentences(titles: list[str]) -> dict[str, str]:
    """{title: first_sentence_plaintext}. Missing/empty => "" ."""
    out: dict[str, str] = {t: "" for t in titles}
    total_batches = (len(titles) + EXTRACT_BATCH - 1) // EXTRACT_BATCH

    for i, batch in enumerate(chunks(titles, EXTRACT_BATCH), start=1):
        data = api_get({
            "action": "query",
            "titles": "|".join(batch),
            "prop": "extracts",
            "exintro": "1",
            "explaintext": "1",
            "exsentences": "2",
            "redirects": "0",
        })
        q = data.get("query", {})

        # Build a map from normalised-back-to-original title.
        norm_to_orig: dict[str, str] = {t: t for t in batch}
        for norm in q.get("normalized", []):
            norm_to_orig[norm.get("to", "")] = norm.get("from", "")

        for page in q.get("pages", []):
            pg_title = page.get("title", "")
            orig = norm_to_orig.get(pg_title, pg_title)
            extract = (page.get("extract") or "").strip()
            # First sentence ~= up to first ". " that isn't mid-abbreviation.
            # For classification a rough cut works fine.
            out[orig] = extract

        if i % 5 == 0 or i == total_batches:
            print(f"  fetched {i}/{total_batches} batches ({len(titles)} titles)")

    return out


def classify(sentence: str) -> str:
    s = sentence.lower()
    for category, pat in RULES:
        if pat.search(s):
            return category
    return "topic"


def read_titles(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as f:
        return [row["title"] for row in csv.DictReader(f)]


def write_rows(path: Path, rows: list[tuple[str, str, str]], header: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path}")


def process(input_name: str, classified_name: str, topic_name: str) -> None:
    src = OUT_DIR / input_name
    if not src.exists():
        raise SystemExit(
            f"Missing {src}. Run find_women_men_in.py then articles_only.py first."
        )
    print(f"\n=== {input_name} ===")
    titles = read_titles(src)
    print(f"  {len(titles)} articles")
    sentences = fetch_first_sentences(titles)

    rows = [(t, classify(sentences[t]), sentences[t]) for t in titles]

    # Category breakdown.
    from collections import Counter
    counts = Counter(category for _, category, _ in rows)
    print("  breakdown:")
    for cat, n in counts.most_common():
        print(f"    {cat}: {n}")

    write_rows(OUT_DIR / classified_name, rows,
               header=("title", "category", "first_sentence"))
    topic_rows = [(t, c, s) for t, c, s in rows if c == "topic"]
    write_rows(OUT_DIR / topic_name, topic_rows,
               header=("title", "category", "first_sentence"))


def main() -> None:
    process(
        "starts_with_women_in_articles_only.csv",
        "starts_with_women_in_classified.csv",
        "starts_with_women_in_topic_only.csv",
    )
    process(
        "starts_with_men_in_articles_only.csv",
        "starts_with_men_in_classified.csv",
        "starts_with_men_in_topic_only.csv",
    )


if __name__ == "__main__":
    main()
