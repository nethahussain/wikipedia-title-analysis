# What Wikipedia means when it says "Women in…"

If you spend any time clicking around English Wikipedia, you will sooner
or later land on an article titled "Women in *something*" — Women in
Bangladesh, Women in computing, Women in the Catholic Church, Women in
the 23rd Canadian Parliament. The convention is so established that most
readers probably don't notice it. But what happens if you try to count
the parallel case — articles titled "Men in *something*"?

That's the question this short study set out to answer, and the answer
turns out to be more interesting than I expected.

## How I counted

Rather than rely on Wikipedia's search bar, which caps results at 10,000
and would have quietly truncated the common words, I pulled the full
list of article titles from the
[page-title dump](https://dumps.wikimedia.org/enwiki/latest/) — a
gzipped text file listing every one of the roughly nineteen million
titles in the main namespace. From that list I extracted every title
starting (case-insensitively) with "Women in", "Men in", "Females in" or
"Males in", then used the MediaWiki API to separate real articles from
redirects, to fetch each article's first sentence, and to classify each
one by type — film, book, organization, or what I ended up calling a
"topic" article, meaning an article that is actually about the social
condition of women or men in some setting.

All the code and all the intermediate data are published in the
[companion repository](https://github.com/nethahussain/wikipedia-title-analysis).

## The number that stopped me

Once the redirects and the films and the novels were set aside, I was
left with **490 genuine "Women in…" topic articles and 7 "Men in…" topic
articles**. Seventy to one.

Before I say anything else about that ratio, it's worth lingering on
what's *not* in the Men-in count. Of the sixty live "Men in…" articles
that exist on Wikipedia, most are the names of films, television shows
and other cultural works. The *Men in Black* franchise alone accounts
for a substantial chunk: the 1997 blockbuster and its sequels, the
animated series, the theme-park ride, and — my favourite discovery — a
1934 Three Stooges short that predates the Will Smith film by six
decades and happens to share its name. Add in assorted novels (*Men in
the Off Hours*), a TVB drama series (*Men in Pain*), a handful of
disambiguation pages, and very little of the "Men in…" catalogue is
about men.

The seven articles that *are* about men are a useful list in themselves.
Three are about professional domains where men are statistically a
minority: **Men in early childhood education**, **Men in feminism**, and
**Men in nursing**. One — **Men In Hijab** — documents a 2016 Iranian
movement in which men wore the hijab in solidarity with their
female relatives. Two concern the *Men in Black* cultural myth (the UFO
conspiracy-theory figure, not the film). And one is **Men in
Middle-earth**, an article about Tolkien's fictional race of humans.

That's it. Across the whole of English Wikipedia, those are the
"Men in…" articles.

## "Women in…" tells a different story

The Women-in picture is almost exactly inverted. Of 587 live articles,
four in five are topic articles. The remainder split into feminist
organizations (*Women in Animation*, *Women in Aviation International*,
*Women in Trucking Association*), films — including a surprisingly
robust subgenre of 1970s "women in prison" exploitation cinema — a
handful of awards, and the expected assortment of novels and albums.
Nothing unusual.

What's more revealing is the shape of those 490 topic articles. The
biggest slice, by a wide margin, is geographic: about 175 of the 490 —
roughly thirty-six percent — are "Women in *[country or region]*"
articles. Afghanistan, Bangladesh, Bolivia, Burundi, Chad, Ecuador, all
the way through to Zimbabwe. This is a long-running convention on
English Wikipedia: the country-level "Women in X" article functions as
a hub for that country's gender history, economics, and legal status,
and WikiProjects have been steadily filling in the gaps for years.

After geography, politics and government is the next large cluster —
eighty-six articles about women in parliaments, congresses, suffrage
movements, and political parties. Canada is especially well-covered
here: twelve separate articles track women in successive Canadian
parliaments from the 14th to the 45th, one per parliament. Military
and police comes next with sixty-two articles, covering everything
from women in the Israel Defense Forces to women in ancient warfare.

Further down the list, there are forty-two articles on women in
specific historical events or eras (the Cuban Revolution, the Algerian
War, the California gold rush), forty-two on specific professions and
industries, twenty-six on arts and media, twenty-two on STEM fields,
eighteen on religions (Christianity and its denominations, Islam,
Hinduism, Buddhism), and — surprisingly to me — just three on sports.
Wikipedia's extensive coverage of women's athletics lives under
completely different title conventions like "Women's association
football", so the "Women in…" frame never caught on there.

## A small linguistic coda: "Females in…" and "Males in…"

Out of curiosity I ran the same pipeline on the prefixes "Females in"
and "Males in". I found twelve titles across the whole encyclopaedia
— eleven with "Females", one with "Males" — and every single one is a
redirect. *Females in Bahrain* redirects to *Women in Bahrain*;
*Females in combat* to *Women in combat*; *Males in nursing* to *Men in
nursing*. Editors have evidently settled on "women" and "men" as the
canonical social categories and reserved "female/male" for the
biological qualifier. It's a small thing, but it shows up consistently
across thousands of articles.

## Is 70-to-1 a gap?

On a first read, the 490-to-7 ratio sounds like a glaring imbalance —
another way in which Wikipedia, famously edited by a
male-skewed community, fails to cover men's experience. I don't think
that's the right reading.

The "Women in X" title exists because, for most values of X, the
generic article is already implicitly about men. "The history of the
Canadian Parliament" was, until women were allowed to sit in it,
entirely a history of men — and the article about it is not called
"Men in the Canadian Parliament". It's called "History of the Canadian
Parliament". Creating *Women in the 23rd Canadian Parliament* is a way
to surface a body of material that would otherwise be lost in the male
default. A symmetrical "Men in the 23rd Canadian Parliament" article
would, in the limit, be the whole parliament article with the
interesting bits removed.

This is exactly why the few Men-in articles that do exist are
clustered on professions where men are the minority: nursing, early
childhood education, feminism. In those domains, the generic article
("Nursing", "Early childhood education") is implicitly about women, and
the "Men in X" frame starts carrying the same informational weight
that "Women in X" carries everywhere else. The pattern is symmetrical
in its logic, even though the numbers are wildly asymmetrical.

## What I won't claim

I want to be honest about two things. Keyword-based classification is
imperfect — a sentence that says an article's subject "is a 1997
American comedy film" reliably goes in the film bucket, but a sentence
that says the subject "is an award established in 2019 by UN Women
Ukraine and the Ukrainian Institute" contains enough category words
that a rule-based classifier can misfire. I've left the first sentence
of each article in the published CSV so that anyone can audit the
labels directly.

And title prefixes are only one slice of Wikipedia's coverage of
gender. Articles like *Gender disparity in computing*, *Sexism in
science*, or *Female academics in early modern England* don't begin
with any of the six patterns I searched for, and aren't counted here.
What I've mapped is a linguistic convention, not a full content census.

That convention, once you see it, is harder to unsee. The "Women in…"
title isn't a content category — it's a structural repair. Wikipedia
is full of them.

---

*The full dataset, scripts, and intermediate files are at
[github.com/nethahussain/wikipedia-title-analysis](https://github.com/nethahussain/wikipedia-title-analysis).*
