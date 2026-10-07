# Expanded card identity resolution

## Question

What identity granularity should repository tools use when resolving cards in paper Expanded: exact print, gameplay variant, or card name?

## Answer

Use all three as separate layers. Exact print ID is required for auditable source data and current print-level legality. A conservative gameplay-variant ID is useful for grouping reprints with identical gameplay-relevant database fields. Card name is a deck-building identity, but it is frequently too coarse for gameplay analysis and is unsafe as a legality key when a name contains both legal and banned variants.

This result adds `tools/card_identity.py`, which builds explicit indexes by print ID, gameplay variant, and name while reusing the official-ban overlay and gameplay fingerprint from `tools/build_expanded_legality_baseline.py`.

## Computational result

Using the bundled 2026-09-16 card snapshot, the seven-print official-ban overlay, and the corrected exclusion of seven prints whose card text prohibits official-tournament use:

- Expanded-scope prints: **14,884**
- Card names: **3,392**
- Conservative gameplay variants: **10,449**
- Legal gameplay variants: **10,416**
- Banned gameplay variants: **33**
- Gameplay variants containing both legal and banned prints: **0**
- Names containing both legal and banned prints: **11**
- Names containing more than one gameplay variant: **1,289** (**38.0%** of names)
- Gameplay variants represented by more than one print: **2,828**
- Largest exact-fingerprint reprint class: **15 prints**

The zero mixed-legality variant count is the central finding. In this snapshot, every banned print belongs to a conservative gameplay fingerprint class that is entirely banned, while legal same-name cards belong to different gameplay variants. This means the current fingerprint is a useful intermediate identity for research, although it is not an official reprint-equivalence rule.

## Mixed-legality names

| Name | Banned prints | Legal same-name prints | Distinct gameplay variants |
| --- | ---: | ---: | ---: |
| Archeops | 2 | 6 | 5 |
| Dragapult | 1 | 4 | 4 |
| Flabébé | 1 | 10 | 10 |
| Flapple | 4 | 4 | 4 |
| Marshadow | 2 | 7 | 7 |
| Milotic | 1 | 10 | 10 |
| Mismagius | 1 | 10 | 10 |
| Oranguru | 1 | 12 | 8 |
| Sableye | 1 | 16 | 16 |
| Shaymin-EX | 3 | 4 | 3 |
| Unown | 2 | 3 | 5 |

For all eleven names, the banned prints are separated from the legal prints by gameplay fingerprint. Name-only legality therefore collapses distinctions that the data currently preserves cleanly at variant level.

## Gameplay ambiguity at name level

Legality is only one reason to preserve variant identity. **1,289 of 3,392 names** map to multiple gameplay fingerprints. The most extreme examples are Pikachu with 78 variants across 99 Expanded-scope prints, Eevee with 31 variants across 50 prints, Snorlax with 22 variants across 30 prints, Lapras with 20 variants across 25 prints, and Bisharp with 20 variants across 22 prints.

A search, simulator, optimizer, or deck parser that stores only a card name cannot reliably infer attacks, Abilities, HP, typing, evolution data, Rule Box text, Weakness, Resistance, or Retreat Cost for these names. Name is therefore appropriate for deck-building copy-limit aggregation, but generally insufficient for game-state or effect modeling.

## Method

`tools/card_identity.py` reads the same Expanded-scope set and card data as the legality baseline. Each print becomes a `PrintIdentity` containing exact card ID, name, set ID, supertype, effective legality, legality provenance, and the existing gameplay fingerprint. It then builds three indexes:

1. `prints_by_id`: exact print identity.
2. `prints_by_variant`: conservative gameplay-equivalent identity under the repository fingerprint.
3. `prints_by_name`: deck-building name identity.

The index exposes legality classification at name and variant level as `Legal`, `Banned`, or `Mixed`. The summary function records mixed names, variant multiplicity, and high-ambiguity names.

The computational check was run against the bundled card archive and reproduced the legality baseline total of 14,884 prints. The resulting counts are preserved in `summary.json`.

## Interpretation

**Fact from the current data:** no conservative gameplay-fingerprint class mixes legal and banned prints.

**Computational observation:** name-level gameplay ambiguity is common, affecting about 38% of names in scope.

**Methodological judgment:** repository systems should retain exact print ID and variant ID even when they also aggregate by card name. A three-layer identity model prevents legality, reprint, and gameplay semantics from being silently collapsed.

## Limitations

The gameplay fingerprint is a repository research convenience, not an official definition of functional reprint equivalence. Minor wording differences, errata, tournament reprint policy, or future database changes may require two cards to be treated as equivalent even when their fingerprints differ, or may reveal a case that should split an existing class. The result therefore supports a conservative identity layer rather than claiming to solve official reprint equivalence.

The analysis inherits the legality baseline's 191 remaining set-level fallback records, seven-print official overlay, and explicit tournament-prohibition handling. A future official-ban change can alter these counts until the baseline overlay is refreshed.

## Confidence and next work

Confidence is high in the snapshot counts because they are deterministic and reproduce the existing 14,884-print baseline. Confidence is moderate in the gameplay fingerprint as a long-term identity abstraction because official functional equivalence still needs explicit modeling.

The next valuable step is to add an official reprint-equivalence layer between conservative fingerprint identity and deck-building name identity, then use the resulting resolver in a deck validator and simulator input format.
