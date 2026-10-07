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

- **5** are exact current-semantic fingerprint candidates after current rules-grounded normalization;
- **38** resolve through the narrow historical bridge whose Black & White-onward counterpart already existed by the 2012 evidence date;
- **26** resolve through current name-wide errata;
- **3** Copycat prints resolve through the current Tournament Handbook's explicit semantic example;
- **2** Life Herb prints are now known non-equivalent in current Expanded because their Pokémon-ex target exclusion is reachable again;
- **2** remain in `semantic_review`.

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

The resolver now covers most benchmark rows through exact normalized identity, dated historical bridges, current errata, and the official Copycat example. Rules-grounded normalization resolves Fisherman `ecard3-125` and the no-exclusion Life Herb `pl1-108`. The remaining two semantic-review rows are the older Pokédex printings `base1-87` and `base4-115`. The two Pokémon-ex-excluding Life Herb printings remain current negative witnesses.

## Why this is useful

Raw text equality is known to produce false negatives. Copycat is the explicit current-handbook example.

Name equality is also unsafe. Rainbow Energy is the explicit current-handbook counterexample.

The benchmark therefore gives a semantic compiler both kinds of guardrail:

- source-backed positive cases it should eventually recognize;
- a source-backed same-name negative case it must keep separate.

The benchmark also exposes coverage numerically. The current regression preserves the two rules-grounded promotions while retaining the Copycat positive, Rainbow Energy negative, Life Herb format-relative negative boundary, and unresolved Pokédex information-state distinction.

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

The reproducer asserts the 76 / 15 benchmark size, the current 5 / 38 / 26 / 3 / 2 / 2 resolver partition, the per-name counts, and the Copycat / Rainbow Energy boundary pairs.

## Limitations

The 2012 document is historical. It cannot replace the current Tournament Handbook.

This first benchmark also covers only Trainer rows explicitly transcribed from the 2012 list with `Reference Required: No`. It intentionally excludes historical rows marked `Yes`, because the old policy allowed reference-card handling for materially updated text.

The current positive and negative boundary set is tiny. Future benchmark growth should prioritize additional official reprint lists, errata, rulings, and handbook examples over model-generated equivalence labels.

## Next work

Treat the two remaining Pokédex rows as an information-state question. The older wording permits looking at "up to 5" cards while the later wording fixes the inspected prefix at five, so any future normalization should explicitly account for observer knowledge rather than treating extra hidden information as mechanically irrelevant.
