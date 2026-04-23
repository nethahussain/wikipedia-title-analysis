"""Sub-classify the ~497 Women/Men topic articles by thematic area.

Input:
    output/topic_articles_combined.csv  (from combine_topic_articles.py)

Output:
    output/topic_articles_subclassified.csv
    Columns: group, title, subcategory, tail, first_sentence
    (`tail` = the part of the title after "Women in " / "Men in ")

Subcategory rules run in order; first match wins. If nothing matches we
fall back to `geography` when the tail looks like a place name, else
`society_other`.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

IN_PATH  = Path("output/topic_articles_combined.csv")
OUT_PATH = Path("output/topic_articles_subclassified.csv")

# A non-exhaustive but broad list of country/territory/region names that
# appear after "Women in ...". Captured in lowercase for cheap matching.
# Built from the actual titles we saw in the dump.
PLACE_WORDS = {
    # continents & regions
    "africa", "asia", "europe", "americas", "caribbean", "latin america",
    "middle east", "oceania", "north america", "south america", "southeast asia",
    "central asia", "south asia", "east asia", "west africa", "east africa",
    "north africa", "sub-saharan africa", "the americas", "arab world",
    "scandinavia", "balkans", "baltic states",
    # common country/territory tails we saw
    "afghanistan", "albania", "algeria", "argentina", "armenia", "australia",
    "austria", "azerbaijan", "bahrain", "bangladesh", "belarus", "belgium",
    "bolivia", "bosnia", "brazil", "bulgaria", "burkina faso", "cambodia",
    "cameroon", "canada", "chile", "china", "colombia", "comoros", "congo",
    "cote d'ivoire", "croatia", "cuba", "cyprus", "czech republic", "denmark",
    "djibouti", "dominican republic", "ecuador", "egypt", "el salvador",
    "eritrea", "estonia", "ethiopia", "fiji", "finland", "france", "gabon",
    "gambia", "georgia", "germany", "ghana", "greece", "guatemala", "guinea",
    "haiti", "honduras", "hong kong", "hungary", "iceland", "india", "indonesia",
    "iran", "iraq", "ireland", "israel", "italy", "jamaica", "japan", "jordan",
    "kazakhstan", "kenya", "kosovo", "kuwait", "kyrgyzstan", "laos", "latvia",
    "lebanon", "lesotho", "liberia", "libya", "lithuania", "luxembourg",
    "macau", "madagascar", "malawi", "malaysia", "maldives", "mali", "malta",
    "mauritania", "mauritius", "mexico", "moldova", "mongolia", "montenegro",
    "morocco", "mozambique", "myanmar", "namibia", "nepal", "netherlands",
    "new zealand", "nicaragua", "niger", "nigeria", "north korea", "norway",
    "oman", "pakistan", "palestine", "panama", "papua new guinea", "paraguay",
    "peru", "philippines", "poland", "portugal", "qatar", "romania", "russia",
    "rwanda", "saudi arabia", "senegal", "serbia", "sierra leone", "singapore",
    "slovakia", "slovenia", "somalia", "south africa", "south korea", "spain",
    "sri lanka", "sudan", "suriname", "sweden", "switzerland", "syria",
    "taiwan", "tajikistan", "tanzania", "thailand", "togo", "tunisia", "turkey",
    "turkmenistan", "uganda", "ukraine", "united arab emirates", "united kingdom",
    "united states", "uruguay", "uzbekistan", "venezuela", "vietnam", "yemen",
    "zambia", "zimbabwe",
    # extra countries/territories that were missed above
    "bermuda", "bhutan", "brunei", "burundi", "chad", "england",
    "french guiana", "ivory coast", "joseon", "kiribati",
    "north macedonia", "northern ireland", "south sudan", "taiwan",
    "equatorial guinea", "guinea-bissau", "guyana", "liechtenstein",
    "saint lucia", "saint vincent", "san marino", "sao tome", "seychelles",
    "solomon islands", "swaziland", "eswatini", "vatican city",
    "trinidad and tobago", "vanuatu", "andorra", "antigua", "barbados",
    "belize", "dominica", "grenada", "nauru", "marshall islands",
    "samoa", "east timor", "south ossetia",
    # subnational / specific areas from our dump
    "abkhazia", "aceh", "alabama", "alaska", "arizona", "arkansas",
    "british virgin islands", "byzantine empire", "christmas island",
    "cocos (keeling) islands", "cook islands", "faroe islands",
    "francoist spain", "franco-era spain", "gibraltar", "greenland",
    "guam", "hawaii", "isle of man", "kashmir", "kurdistan", "kyrgyz republic",
    "maya society", "maya culture", "medieval europe", "micronesia", "monaco",
    "niue", "ottoman empire", "palau", "puerto rico", "rhodesia",
    "scotland", "soviet union", "tibet", "timor-leste", "tokelau", "tonga",
    "transnistria", "tuvalu", "wales", "west bank", "western sahara",
    "yugoslavia", "zanzibar", "northern cyprus", "amish society",
    "punjab", "punjab, india", "opus dei", "antarctica",
    # Canadian provinces etc.
    "alberta", "british columbia", "manitoba", "ontario", "quebec",
    "new brunswick", "newfoundland", "nova scotia", "saskatchewan",
}

# Historical events / movements — separate category.
HISTORY_EVENT_RX = re.compile(
    r"\b("
    r"revolution|civil war|gold rush|decolonisation|decolonization|"
    r"arab spring|spring uprising|language movement|uprising|"
    r"independence movement|liberation (war|movement)|partition|"
    r"pre-islamic|pre-colonial"
    r")\b"
)

# Ordered rules: (subcategory, regex on LOWERCASED tail)
TAIL_RULES: list[tuple[str, re.Pattern]] = [
    # Politics & government — parliaments, congresses, political parties, suffrage
    ("politics_government", re.compile(
        r"\b("
        r"parliament|parliaments|congress|senate|legislature|legislative|cabinet|"
        r"government|politics|political|elections?|suffrage|voting|democracy|"
        r"parti(do|t)|labour party|communist party|socialist party|nationalist party|"
        r"dewan (negara|rakyat)|house of representatives|national assembly|"
        r"bundestag|knesset|diet|duma|majlis"
        r")\b")),

    # Military, police, warfare
    ("military_police", re.compile(
        r"\b("
        r"military|armed forces|army|navy|air force|marines|combat|warfare|"
        r"war|wartime|police|policing|defense|defence|"
        r"idf|wehrmacht|crusades|intelligence"
        r")\b")),

    # Religion
    ("religion", re.compile(
        r"\b("
        r"christianity|catholic|catholicism|protestantism|mormon(ism)?|"
        r"islam|muslim|sharia|hijab|"
        r"hinduism|hindu|buddhism|buddhist|"
        r"judaism|jewish|orthodox (judaism|church)|"
        r"sikhism|sikh|"
        r"church|mosque|synagogue|temple|bible|quran|torah|"
        r"religion|religious"
        r")\b")),

    # STEM & academia
    ("stem_science", re.compile(
        r"\b("
        r"science|sciences|stem|"
        r"technology|computing|computer science|information technology|"
        r"engineering|mathematics|math|statistics|"
        r"astronomy|astrophysics|space|"
        r"physics|chemistry|biology|geology|ecology|"
        r"medicine|health sciences|"
        r"research|academia"
        r")\b")),

    # Specific professions / workforce — check after politics so "the workforce" etc. doesn't
    # pre-empt "parliament"
    ("professions_workforce", re.compile(
        r"\b("
        r"nursing|dentistry|veterinary|pharmacy|surgery|psychiatry|"
        r"law\b|legal profession|judiciary|courts?|"
        r"teaching|education|academia|academic|"
        r"journalism|"
        r"agriculture|farming|fishing|mining|"
        r"business|entrepreneurship|management|"
        r"workforce|labour|labor|employment|industry|industries|"
        r"trucking|aviation|maritime|shipping|transportation|"
        r"architecture|construction"
        r")\b")),

    # Arts, media, culture as industry
    ("arts_media", re.compile(
        r"\b("
        r"art|arts|painting|sculpture|design|fashion|"
        r"film|cinema|filmmaking|television|tv|radio|"
        r"music|jazz|opera|hip[- ]hop|rock|classical music|folk music|"
        r"literature|poetry|fiction|"
        r"dance|ballet|theatre|theater|"
        r"comedy|cartoon|animation|"
        r"journalism|media"
        r")\b")),

    # Sports
    ("sports", re.compile(
        r"\b("
        r"sports?|athletics|olympic|chess|cycling|football|soccer|baseball|"
        r"basketball|cricket|hockey|tennis|golf|rugby|boxing|wrestling|"
        r"swimming|gymnastics|athletics"
        r")\b")),

    # Historical era / period
    ("history_era", re.compile(
        r"\b("
        r"ancient|classical\s+(greece|rome|antiquity)|antiquity|"
        r"medieval|middle ages|renaissance|enlightenment|"
        r"\d{2}(st|nd|rd|th)[- ]century|"
        r"\d{4}s|"
        r"victorian|edwardian|georgian era|"
        r"world war"
        r")\b")),
]


def load_rows() -> list[dict]:
    with IN_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tail_of(title: str) -> str:
    for prefix in ("Women in ", "Women In ", "Men in ", "Men In "):
        if title.startswith(prefix):
            return title[len(prefix):]
    return title


def subclassify(tail: str, sentence: str) -> str:
    t = tail.lower()

    # Apply keyword rules to tail first.
    for cat, pat in TAIL_RULES:
        if pat.search(t):
            return cat

    # Historical events / social movements before geography so
    # "the Cuban Revolution" doesn't get swallowed as "cuba".
    if HISTORY_EVENT_RX.search(t):
        return "history_era"

    # Falls through: is the tail a place?
    # Strip a leading "the " for comparison against place list.
    candidate = t
    if candidate.startswith("the "):
        candidate = candidate[4:]
    # Try exact match, then first 1-3 words against place set.
    if candidate in PLACE_WORDS:
        return "geography"
    parts = candidate.split()
    for k in (4, 3, 2, 1):
        if len(parts) >= k and " ".join(parts[:k]) in PLACE_WORDS:
            return "geography"

    # Also apply rules against the first sentence as a last chance.
    s = sentence.lower()
    for cat, pat in TAIL_RULES:
        if pat.search(s):
            return cat

    return "society_other"


def main() -> None:
    if not IN_PATH.exists():
        raise SystemExit(f"Missing {IN_PATH}. Run combine_topic_articles.py first.")

    rows_in = load_rows()
    rows_out: list[tuple[str, str, str, str, str]] = []
    for r in rows_in:
        tail = tail_of(r["title"])
        sub = subclassify(tail, r.get("first_sentence", ""))
        rows_out.append((r["group"], r["title"], sub, tail, r.get("first_sentence", "")))

    # Write CSV.
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("group", "title", "subcategory", "tail", "first_sentence"))
        w.writerows(rows_out)
    print(f"wrote {OUT_PATH}: {len(rows_out)} rows")

    # Print breakdowns.
    print("\nSubcategory counts (all groups combined):")
    counts = Counter(r[2] for r in rows_out)
    for cat, n in counts.most_common():
        print(f"  {cat}: {n}")

    print("\nBreakdown by group:")
    for group in ("women", "men"):
        sub_counts = Counter(r[2] for r in rows_out if r[0] == group)
        print(f"  {group} ({sum(sub_counts.values())} articles):")
        for cat, n in sub_counts.most_common():
            print(f"    {cat}: {n}")


if __name__ == "__main__":
    main()
