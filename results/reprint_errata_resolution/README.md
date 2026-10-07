# Errata-aware reprint resolution

## Question

Can official Pokémon TCG errata resolve part of the historical same-name reprint pool that raw database fingerprints leave ambiguous?

## Result

Yes. The official TCG Errata resource has a "Major Changes to Existing Cards" section containing 15 name-wide Trainer corrections. Applying those entries as an explicit evidence layer produces **44 additional historical print candidates across 11 names** that were absent from the exact-gameplay-fingerprint candidate set.

Against the current bundled card snapshot, the existing 4,260-print same-name review pool partitions into:

- **106** exact-gameplay-fingerprint candidates;
- **44** additional official-errata candidates;
- **4,110** prints that still require semantic review.

The conservative high-confidence candidate set therefore grows from 106 to **150 prints** before any fuzzy or language-model semantic comparison.

Trainer cards show the largest immediate gain. There are **168** historical outside-scope Trainer prints sharing a name with a legal Expanded Trainer. Exact fingerprinting resolves 2 of them, and the errata layer resolves another 44, for **46 of 168 (27.38%)**.

This result adds `tools/reprint_errata_resolution.py`. It keeps direct legality, exact-fingerprint evidence, official errata evidence, semantic review, and missing-counterpart states separate.

## Why errata belongs before semantic similarity

The repository Advanced Player's Rulebook says that when card text has been updated, the latest version of the effect must be applied. The official TCG Errata resource likewise states that its corrected text reflects the text that should apply instead of how the card originally appeared.

Those rules create an authoritative normalization step. A raw card database can preserve historical printed wording while tournament play uses corrected wording.

The exact-fingerprint path now runs through tools/official_print_errata.py before comparison. That layer covers all 41 print-specific entries in the current official errata resource and materially changes 24 bundled records. The present snapshot still has 106 exact historical candidates after that normalization, so the candidate partition below is unchanged while the semantics feeding it are now corrected.

The 15 name-wide Trainer entries modeled here are:

- Energy Recycler
- Energy Retrieval
- Great Ball
- Hyper Potion
- Leftovers
- Lum Berry
- Pal Pad
- PlusPower
- Pokémon Catcher
- Potion
- Quick Ball
- Rare Candy
- Sitrus Berry
- Super Rod
- Superior Energy Retrieval

All 15 names have at least one effectively legal Expanded print in the current snapshot. Eleven also have historical prints outside the database's Expanded-set universe, producing the 44 new candidates.

## Candidate counts by name

| Name | Historical prints promoted to errata candidate |
| --- | ---: |
| Potion | 16 |
| Rare Candy | 7 |
| PlusPower | 6 |
| Great Ball | 4 |
| Energy Retrieval | 3 |
| Lum Berry | 2 |
| Quick Ball | 2 |
| Hyper Potion | 1 |
| Leftovers | 1 |
| Sitrus Berry | 1 |
| Super Rod | 1 |

Every one of these 44 prints failed the exact gameplay-fingerprint test first. The gain therefore comes entirely from authoritative errata information rather than duplicate counting.

## Resolver states

`ReprintResolver.resolve()` returns one of seven explicit states:

1. `direct_legal`
2. `direct_banned`
3. `outside_disallowed`
4. `exact_fingerprint_candidate`
5. `official_errata_candidate`
6. `semantic_review`
7. `no_expanded_counterpart`

The two candidate states are intentionally separate. Exact fingerprinting is repository-local structural evidence. The errata state records a direct official source.

The resolver still uses the word "candidate" because this layer does not attempt to reproduce every tournament-handbook judgment, historical ruling, or future erratum. Deck validation can consume this evidence later through an explicit policy decision.

## Regression cases

The reproducer preserves several useful boundary cases.

- `dp4-99` Leftovers resolves as `official_errata_candidate`. Its historical text heals 10 damage, while the official erratum updates Leftovers to heal 20.
- `ex2-88` Rare Candy resolves as `official_errata_candidate`. The official erratum replaces the older evolution behavior with the modern Stage 2-only timing rules.
- `gym1-18` Misty remains `exact_fingerprint_candidate`, showing that the older exact-matching path still takes precedence.
- `ex7-83` Copycat remains `semantic_review`. The Tournament Handbook uses Copycat as a positive example of functional equivalence despite wording differences, so this is a known false negative that belongs to the next semantic layer.
- `base5-17` Rainbow Energy remains `semantic_review`. The Tournament Handbook gives historical Rainbow Energy as a negative example because damage and damage counters are distinct mechanics, so same-name matching must not promote it automatically.
- `bw5-100` Rare Candy is `direct_legal`, preserving direct format membership as the strongest route.

Together, Copycat and Rainbow Energy prevent two opposite errors. The resolver does not require raw-text equality for every future equivalence, and it does not treat same-name similarity as sufficient evidence.

## Evidence classes

**Official rule fact.** The Advanced Player's Rulebook states that the latest updated card text applies when a card's text has been changed.

**Official errata evidence.** The Play! Pokémon TCG Errata page provides the 15 name-wide Trainer corrections used by this overlay.

**Tournament-policy evidence.** The Play! Pokémon TCG Tournament Handbook's reprint section requires identical card names and functionally identical text, with Copycat as a positive example and Rainbow Energy as a negative example.

**Computational result.** The 106 / 44 / 4,110 partition and the 46-of-168 Trainer coverage come from deterministic scanning of the bundled snapshot.

**Methodological judgment.** Official errata should be applied before free-form semantic comparison because it is a stronger source of card meaning than historical database wording.

## Official sources

- TCG Errata: https://play.pokemon.com/en-us/resources/documents/tcg-errata/
- Current TCG Tournament Handbook: https://www.pokemon.com/static-assets/content-assets/cms2/pdf/play-pokemon/rules/play-pokemon-tcg-tournament-handbook-en.pdf
- Repository rule reference: `resources/advanced-players-rulebook.md`, section II-A, "About Card Text"

## Reproduction

Run:

`python results/reprint_errata_resolution/reproduce.py`

The regression asserts:

- 4,260 same-name review prints;
- 106 exact-fingerprint candidates;
- 44 official-errata candidates across 11 names;
- 4,110 remaining semantic-review prints;
- 150 total conservative candidates before semantic review;
- 168 historical Trainer review prints;
- 46 Trainer candidates resolved by exact fingerprint or official errata.

## Limitations

The name-wide candidate overlay still covers only the Trainer entries in the official errata page's "Major Changes to Existing Cards" section. Exact print-specific corrections are now normalized before fingerprint comparison through tools/official_print_errata.py. The global historical Pokémon Tool category update remains a separate normalization problem, as do later card-specific announcements that may not yet be reflected in the official errata resource.

The overlay is static repository data and must be maintained as official errata changes.

This work also does not decide the remaining 4,110 semantic-review cases. Copycat demonstrates that some are true functional reprints despite wording differences. Rainbow Energy demonstrates that others are mechanically distinct despite sharing a name.

## Next work

The next identity layer should normalize the global historical Pokémon Tool category rule and then add a small auditable semantic grammar for Trainer and Energy text. It should preserve explicit positive and negative exemplars from the Tournament Handbook before being connected to tools/deck_validator.py.
