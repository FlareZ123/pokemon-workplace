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

- **41** resolve through the narrow historical bridge whose Black & White-onward counterpart already existed by the 2012 evidence date;
- **26** resolve through current name-wide errata;
- **3** Copycat prints resolve through the current Tournament Handbook's explicit semantic example;
- **2** Life Herb prints are now known non-equivalent in current Expanded because their Pokémon-ex target exclusion is reachable again;
- **4** remain in `semantic_review`.

This partition is why the 76 rows are best treated as historical compatibility evidence rather than unconditional current positives.

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

The resolver now covers most benchmark rows through dated historical bridges, current errata, and the official Copycat example. The remaining four semantic-review rows are Fisherman, two Pokédex printings, and the no-exclusion Life Herb `pl1-108`. The two excluded-target Life Herb printings are current negative witnesses rather than unresolved positives.

## Why this is useful

Raw text equality is known to produce false negatives. Copycat is the explicit current-handbook example.

Name equality is also unsafe. Rainbow Energy is the explicit current-handbook counterexample.

The benchmark therefore gives a semantic compiler both kinds of guardrail:

- source-backed positive cases it should eventually recognize;
- a source-backed same-name negative case it must keep separate.

The benchmark also exposes coverage numerically. A semantic normalizer can report how the four unresolved historical compatibility rows move, while regression tests preserve the current Copycat positive, Rainbow Energy negative, and Life Herb format-relative negative boundaries.

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

The reproducer asserts the 76 / 15 benchmark size, the current 41 / 26 / 3 / 2 / 4 resolver partition, the per-name counts, and the Copycat / Rainbow Energy boundary pairs.

## Limitations

The 2012 document is historical. It cannot replace the current Tournament Handbook.

This first benchmark also covers only Trainer rows explicitly transcribed from the 2012 list with `Reference Required: No`. It intentionally excludes historical rows marked `Yes`, because the old policy allowed reference-card handling for materially updated text.

The current positive and negative boundary set is tiny. Future benchmark growth should prioritize additional official reprint lists, errata, rulings, and handbook examples over model-generated equivalence labels.

## Next work

Resolve the four remaining semantic-review rows with small rules-grounded transformations. Fisherman's explicit fewer-than-four clause and the Pokédex top-card wording are promising because the Advanced Player's Rulebook already specifies how undersized numbered effects and deck-top operations behave. Keep Life Herb `pl1-108` separate until its damage-counter wording is normalized explicitly.
