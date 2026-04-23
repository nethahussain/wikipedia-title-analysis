# "Women in…", "Men in…": what Wikipedia's title patterns reveal

*A quick census of English Wikipedia articles whose titles begin with
"Women in" or "Men in" — what they are, what they aren't, and what the
imbalance between them tells us.*

---

## Why look at titles?

Article titles are one of the most compact signals of what Wikipedia
chooses to treat as a *topic*. When a community writes an article called
"Women in Bangladesh", it is asserting that the role, status and history
of women in that country is an encyclopaedic subject in its own right —
distinct from "Bangladesh" or from "Women".

Earlier work on Wikipedia's gender gap has focused mostly on **biographies** —
what fraction of articles about people are about women (around 19% in
English Wikipedia as of 2024). This short study instead looks at the
*thematic* surface of the encyclopaedia, by asking a much smaller
question: **how many articles start with "Women in…" versus "Men in…", and
what are they actually about?**

The answer is striking, and the gap is not in the direction you might
expect.

## Method, briefly

All of English Wikipedia's article titles in the main namespace
(~19 million, including redirects) were pulled from the
[`enwiki-latest-all-titles-in-ns0`][dump] dump. We then:

1. Filtered to titles beginning (case-insensitively) with "Women in " or
   "Men in ".
2. Queried the MediaWiki API to separate live articles from redirects.
3. Fetched the first 1–2 sentences of each live article.
4. Classified each article into a type (film, book, TV series, organization,
   topic, etc.) using keyword rules applied to that opening sentence.
5. Sub-classified the "topic" articles — i.e. those that are actually
   *about* the state of women or men — into thematic areas (geography,
   politics, military, religion, STEM, and so on).

All code and output CSVs are published in the [accompanying repository][repo].

[dump]: https://dumps.wikimedia.org/enwiki/latest/
[repo]: #

## The headline numbers

|                                | Women in… | Men in… |
| ------------------------------ | --------: | ------: |
| All titles matching prefix     |     1,283 |     170 |
| Redirects                      |       696 |     110 |
| Live articles                  |   **587** |  **60** |
| Of which: real topic articles  |   **490** |   **7** |

That final row is the one worth pausing on.

**For every "Men in…" topic article that actually describes the condition
of men as a social subject, there are 70 equivalent articles about women.**
The two genders are not being treated symmetrically in this corner of the
encyclopaedia — and the asymmetry is intentional: the "Women in…" framing
is itself a long-standing editorial convention on Wikipedia, used to
document areas where women's participation, history or status has been
historically under-covered.

## Most "Men in…" titles aren't about men

Of the 60 live "Men in…" articles, a plurality are films:

| Category       | Count |
| -------------- | ----: |
| film           |    28 |
| tv_series      |     8 |
| **topic**      | **7** |
| book           |     4 |
| disambiguation |     4 |
| organization   |     2 |
| music          |     2 |
| video_game     |     2 |
| artwork        |     1 |
| attraction     |     1 |
| play           |     1 |

The *Men in Black* franchise alone — the 1997 film, its sequels, the
cartoon, the ride, the 1934 Three Stooges short of the same name —
accounts for a meaningful slice. The whole category is dominated by
titles of creative works that happen to start with "Men in". The seven
articles about men as a social subject are:

- Men in early childhood education
- Men in feminism
- Men in nursing
- Men In Hijab (a 2016 Iranian solidarity movement)
- Men in Middle-earth (the Tolkien concept)
- Men in Black / Men in black (the UFO conspiracy-theory figure)

Only three of these — **early childhood education, feminism, and nursing** —
are genuine "state of men in society" articles. The rest describe a
historical movement, a fictional race, and a cultural myth.

## "Women in…" is overwhelmingly topic articles

The picture for "Women in…" is the opposite. Out of 587 live articles,
**490 (84%)** are real topic articles:

| Category       | Count |
| -------------- | ----: |
| **topic**      | **490** |
| organization   |    36 |
| film           |    27 |
| disambiguation |    10 |
| book           |     7 |
| event          |     5 |
| tv_series      |     5 |
| music          |     4 |
| artwork        |     3 |

The non-topic entries are exactly what you'd expect: feminist
organizations ("Women in Animation", "Women in Aviation International"),
films with "Women in Prison" in the title, a handful of awards, and a
few novels.

## What are the "Women in…" topic articles actually about?

Sub-classifying the 490 Women-in topic articles by thematic area:

| Theme                     | Count |
| ------------------------- | ----: |
| Geography (by country/region) | 175 |
| Politics & government     |    84 |
| Military & police         |    62 |
| Historical era / event    |    42 |
| Professions & workforce   |    40 |
| Arts & media              |    25 |
| STEM & science            |    22 |
| Society / other           |    20 |
| Religion                  |    17 |
| Sports                    |     3 |

A few things stand out:

- **Geography dominates.** 175 articles are "Women in *[country or region]*" —
  Afghanistan, Bahrain, Bangladesh, Bolivia, and so on through the alphabet.
  This is a long-running WikiProject pattern: the country-level "Women in
  X" article is treated as a hub for that country's gender history.
- **Politics and military are huge.** Together, 146 articles (30% of the
  topic total) cover legislatures, cabinets, suffrage, armed forces, and
  police. Twelve articles alone cover women in successive Canadian
  parliaments — one per parliament.
- **Professions come up repeatedly, often in duplicate.** "Women in law",
  "Women in computing", "Women in engineering", "Women in nursing",
  "Women in agriculture" — these are frequently the only "Women in X
  profession" articles on the encyclopaedia, and cross-linking between
  them is uneven.
- **Religion is smaller than politics.** 17 articles — mostly the major
  world religions and some Catholic-specific subtopics.
- **Sports is startlingly thin** at just 3 articles starting with "Women
  in…", even though Wikipedia has extensive coverage of women's sports
  under other title conventions (e.g. "Women's association football").
  The "Women in…" pattern isn't used for sports.

## Is this asymmetry a problem?

Not necessarily. The 490-to-7 gap is a feature, not a gap in coverage.
The "Women in X" framing exists because, historically and currently,
"X" is often implicitly about men — "the history of Parliament", "the
military", "computing" are rarely written as male histories, because the
male subject is assumed. Creating "Women in Parliament" is a way to
surface material that would otherwise be buried in the generic article.

A corresponding "Men in Parliament" article would be essentially the
whole article without the modifier, which is why so few exist. The seven
"Men in…" topic articles that do exist — nursing, early childhood
education, feminism, and so on — are precisely the domains where men are
a *minority*, so the "men in X" framing carries the same informational
weight that "women in X" does elsewhere.

## "Females in…" / "Males in…" barely exist

A sanity check on language: only **12 titles total** across the whole
encyclopaedia begin with "Females in…" or "Males in…" — and **every single
one of them is a redirect** to the "Women in…" / "Men in…" equivalent.

| Source title                              | Redirects to                         |
| ----------------------------------------- | ------------------------------------ |
| Females in Bahrain                        | Women in Bahrain                     |
| Females in combat                         | Women in combat                      |
| Females in the Israel Defense Forces      | Women in the Israel Defense Forces   |
| Males in nursing                          | Men in nursing                       |
| *(and so on)*                             |                                      |

Wikipedia's editors have clearly settled on "women" and "men" as the
canonical social categories, and "female/male" as the biological
qualifier — a distinction worth noting because it shows up consistently
across thousands of articles, not just in the titles counted here.

## Limitations

Two honest caveats:

1. **Keyword classification is imperfect.** Our type rules handle clear
   cases ("is a 1997 American comedy film" → film) but can stumble on
   ambiguous sentences. A handful of mislabels are likely in any bucket;
   the raw `first_sentence` column in the classified CSVs lets anyone
   re-audit.
2. **Title prefixes are only one slice.** Articles like "Female
   academics", "Gender disparity in computing", or
   "Sexism in science" don't start with any of our six patterns and
   aren't counted here. The numbers describe a linguistic *convention*
   more than a content census.

## Data

The full dataset — every title, its redirect status, its type, its
thematic sub-category and its first sentence — is published as CSV in
the repository alongside this article. The scripts are a few hundred
lines of Python each and can be re-run against any newer dump.
