# What Wikipedia means when it says "Women in…"

Anyone who spends time browsing English Wikipedia will sooner or later
land on an article titled "Women in *something*" — Women in Bangladesh,
Women in computing, Women in the Catholic Church, Women in the 23rd
Canadian Parliament. The convention is so established that it is
often passed over without a second thought. A simpler question is
rarely asked: how many articles on the parallel side exist — that is,
articles titled "Men in *something*"?

When that question is put to the data, the answer turns out to be more
interesting than might be expected.

## How the counting was done

Rather than relying on Wikipedia's search bar, which caps results at
10,000 and would have quietly truncated the common words, the full list
of article titles was pulled from the
[page-title dump](https://dumps.wikimedia.org/enwiki/latest/) — a
gzipped text file listing every one of the roughly nineteen million
titles in the main namespace. From that list, every title starting
(case-insensitively) with "Women in", "Men in", "Females in" or
"Males in" was extracted. The MediaWiki API was then used to separate
real articles from redirects, to fetch each article's first sentence,
and to classify each one by type — film, book, organization, or what
has been called here a "topic" article, meaning an article that is
actually about the social condition of women or men in some setting.

The code and the intermediate data are published in the
[companion repository](https://github.com/nethahussain/wikipedia-title-analysis).

## The number that stands out

Once the redirects and the films and the novels had been set aside,
**490 genuine "Women in…" topic articles and 7 "Men in…" topic articles**
were left. Seventy to one.

Before anything else is said about that ratio, it is worth dwelling on
what is *not* counted in the Men-in total. Of the sixty live "Men in…"
articles that exist on Wikipedia, most are the names of films,
television shows and other cultural works. The *Men in Black* franchise
alone accounts for a substantial chunk: the 1997 blockbuster and its
sequels, the animated series, the theme-park ride, and — notably — a
1934 Three Stooges short that predates the Will Smith film by six
decades and happens to share its name. Assorted novels (*Men in the Off
Hours*), a TVB drama series (*Men in Pain*), a handful of disambiguation
pages, and very little of the "Men in…" catalogue can be said to be
about men.

The seven articles that *are* about men are a useful list in
themselves. Three concern professional domains where men are
statistically a minority: **Men in early childhood education**,
**Men in feminism**, and **Men in nursing**. One —  **Men In Hijab**
— documents a 2016 Iranian movement in which men wore the hijab in
solidarity with their female relatives. Two concern the *Men in Black*
cultural myth (the UFO conspiracy-theory figure, not the film). And one
is **Men in Middle-earth**, an article on Tolkien's fictional race of
humans.

That is the full list. Across the whole of English Wikipedia, those
are the "Men in…" articles.

## The picture on the Women-in side

The Women-in picture is almost exactly inverted. Of 587 live articles,
four in five are topic articles. The remainder break down into feminist
organizations (*Women in Animation*, *Women in Aviation International*,
*Women in Trucking Association*), films — including a surprisingly
robust subgenre of 1970s "women in prison" exploitation cinema — a
handful of awards, and the expected assortment of novels and albums.
Nothing unusual.

More revealing is the shape of those 490 topic articles. The biggest
slice, by a wide margin, is geographic: roughly 175 of the 490 — about
thirty-six percent — are "Women in *[country or region]*" articles.
Afghanistan, Bangladesh, Bolivia, Burundi, Chad, Ecuador, all the way
through to Zimbabwe. This is a long-running convention on English
Wikipedia: the country-level "Women in X" article is treated as a hub
for that country's gender history, economics, and legal status, and
WikiProjects have been steadily filling in the gaps for years.

After geography, politics and government is the next large cluster —
eighty-six articles on women in parliaments, congresses, suffrage
movements, and political parties. Canada is especially well-covered
here: twelve separate articles track women in successive Canadian
parliaments from the 14th to the 45th, one per parliament. Military
and police come next with sixty-two articles, covering topics from
women in the Israel Defense Forces to women in ancient warfare.

Further down the list are forty-two articles on women in specific
historical events or eras (the Cuban Revolution, the Algerian War, the
California gold rush), forty-two on specific professions and
industries, twenty-six on arts and media, twenty-two on STEM fields,
eighteen on religions (Christianity and its denominations, Islam,
Hinduism, Buddhism), and — perhaps unexpectedly — only three on sports.
Wikipedia's extensive coverage of women's athletics lives under
different title conventions such as "Women's association football", so
the "Women in…" frame never caught on in that area.

## A small linguistic coda: "Females in…" and "Males in…"

The same pipeline was run on the prefixes "Females in" and "Males in".
Twelve titles were found across the whole encyclopaedia — eleven with
"Females", one with "Males" — and every single one is a redirect.
*Females in Bahrain* redirects to *Women in Bahrain*; *Females in
combat* to *Women in combat*; *Males in nursing* to *Men in nursing*.
"Women" and "men" have evidently been settled upon as the canonical
social categories on Wikipedia, with "female" and "male" reserved for
the biological qualifier. It is a small thing, but it is applied
consistently across thousands of articles.

## Is 70-to-1 a gap?

On a first read, the 490-to-7 ratio can sound like a glaring
imbalance — one more way in which Wikipedia, famously edited by a
male-skewed community, is said to fall short of covering men's
experience. That reading may not be the right one.

The "Women in X" title exists because, for most values of X, the
generic article is already implicitly about men. "The history of the
Canadian Parliament" was, until women were allowed to sit in it,
entirely a history of men — yet the article about it is not called
"Men in the Canadian Parliament". It is called "History of the Canadian
Parliament". Creating *Women in the 23rd Canadian Parliament* is a way
of surfacing a body of material that would otherwise be lost in the
male default. A symmetrical "Men in the 23rd Canadian Parliament"
article would, in the limit, be the whole parliament article with the
interesting bits removed.

This is precisely why the few Men-in articles that do exist are
clustered on professions where men are the minority: nursing, early
childhood education, feminism. In those domains, the generic article
("Nursing", "Early childhood education") is implicitly about women, and
the "Men in X" frame takes on the same informational weight that
"Women in X" carries elsewhere. The pattern is symmetrical in its
logic, even though the numbers are wildly asymmetrical.

## Two honest caveats

Keyword-based classification is imperfect. A sentence that says an
article's subject "is a 1997 American comedy film" will reliably be
bucketed as a film, but a sentence that says the subject "is an award
established in 2019 by UN Women Ukraine and the Ukrainian Institute"
contains enough category words that a rule-based classifier can
misfire. The first sentence of each article has been retained in the
published CSV so that any reader can audit the labels directly.

Title prefixes are also only one slice of Wikipedia's coverage of
gender. Articles such as *Gender disparity in computing*, *Sexism in
science*, or *Female academics in early modern England* do not begin
with any of the six patterns searched for here, and are not counted.
What has been mapped is a linguistic convention, not a full content
census.

That convention, once noticed, is hard to unsee. The "Women in…" title
is not so much a content category as a structural repair. Wikipedia is
full of them.

---

*The full dataset, scripts, and intermediate files are available at
[github.com/nethahussain/wikipedia-title-analysis](https://github.com/nethahussain/wikipedia-title-analysis).*
