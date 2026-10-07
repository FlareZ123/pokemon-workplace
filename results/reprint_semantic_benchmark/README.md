# Official reprint semantic benchmark

## Question

How can a semantic reprint resolver be tested against official evidence instead of judging wording similarity by intuition?

## Benchmark design

This result adds `tools/reprint_semantic_benchmark.py`, a source-backed benchmark with two complementary evidence types.

First, the official **2012 Modified-Legal Reprint List** identifies older printings that could be used because a legal reprint existed. The list separately marks whether the player needed a reference copy with updated wording. This benchmark takes the historical Trainer rows marked **Reference Required: No**, then restricts them to names that still have an effectively legal print in the repository's current Expanded pool.

Second, the Play! Pokémon Tournament Handbook supplies a current positive and negative boundary pair:

- **Copycat** `ex7-83` / `sm7-127`: functionally identical despite different wording.
- **Rainbow Energy** `base5-17` / `sm7-151`: not functionally identical because doing 10 damage and placing 1 damage counter are distinct mechanics.

The historical list is used as evaluation evidence rather than as a present-day legality overlay. Tournament policy changed after 2012, and some old entries that once required a reference would not satisfy the current functional-identity rule.

## Snapshot result

The historical positive set contains **76 Trainer printings across 15 names**.

Under the repository's current resolver:

- **26** are already captured by the official name-wide errata layer;
- **50** remain in `semantic_review`.

Those 50 cases form a concrete positive target set for the next semantic normalizer.

The 76 historical positives by name are:

| Name | Prints |
| --- | ---: |
| Potion | 12 |
| Switch | 10 |
| Poké Ball | 9 |
| Energy Search | 7 |
| Energy Switch | 7 |
| Super Scoop Up | 6 |
| PlusPower | 5 |
| Rare Candy | 5 |
| Great Ball | 4 |
| Copycat | 3 |
| Life Herb | 3 |
| Pokédex | 2 |
| Fisherman | 1 |
| Full Heal | 1 |
| Recycle | 1 |

The errata resolver already absorbs the Potion, PlusPower, Great Ball, and Rare Candy cases that are covered by current official name-wide errata, leaving wording-normalization work concentrated in the other families.

## Why this is useful

Raw text equality is known to produce false negatives. Copycat is the explicit current-handbook example.

Name equality is also unsafe. Rainbow Energy is the explicit current-handbook counterexample.

The benchmark therefore gives a semantic compiler both kinds of guardrail:

- source-backed positive cases it should eventually recognize;
- a source-backed same-name negative case it must keep separate.

The benchmark also exposes coverage numerically. A semantic normalizer can report how many of the 50 unresolved historical positives it recovers, while regression tests ensure it does not collapse the Rainbow Energy negative boundary.

## Evidence classes

**Historical official evidence.** The 2012 list says older cards could be used when reprinted in the then-current Modified format and marks these 76 Trainer printings as requiring no updated reference wording.

**Current tournament-policy evidence.** The Tournament Handbook explicitly calls Copycat functionally identical and Rainbow Energy non-identical.

**Repository computation.** The 76-print benchmark intersects the official historical rows with the current bundled card database and current legal same-name Expanded targets.

**Methodological judgment.** Historical “No reference required” rows are suitable positive training and regression evidence. They are not sufficient by themselves to grant current Expanded legality because the governing reprint rule and later card text may have changed.

## Official sources

- 2012 Modified-Legal Reprint List: https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/2012_modified_legal_reprints.pdf
- Play! Pokémon TCG Tournament Handbook: https://www.pokemon.com/static-assets/content-assets/cms2/pdf/play-pokemon/rules/play-pokemon-tournament-rules-handbook-10062023-en.pdf

## Reproduction

Run:

`python results/reprint_semantic_benchmark/reproduce.py`

The reproducer asserts the 76 / 15 benchmark size, the 26 / 50 current-resolver split, the per-name counts, and the current Copycat / Rainbow Energy boundary pairs.

## Limitations

The 2012 document is historical. It cannot replace the current Tournament Handbook.

This first benchmark also covers only Trainer rows explicitly transcribed from the 2012 list with `Reference Required: No`. It intentionally excludes historical rows marked `Yes`, because the old policy allowed reference-card handling for materially updated text.

The current positive and negative boundary set is tiny. Future benchmark growth should prioritize additional official reprint lists, errata, rulings, and handbook examples over model-generated equivalence labels.

## Next work

Build an auditable Trainer semantic normalizer and score it against the 50 unresolved historical positives. Start with mechanically narrow families such as Switch, Energy Search, Energy Switch, Super Scoop Up, Recycle, and Copycat, then add more grammar only when each transformation has a rules-grounded justification.
