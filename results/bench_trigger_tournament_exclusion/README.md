# Tournament-prohibited Greninja in Bench-trigger catalogs

## Finding

The static hand-to-Bench trigger census previously counted **124** Expanded-legal
Basic Pokémon prints from **49** names and **52** gameplay fingerprints. One
entry, Greninja ★ (`swshp-SWSH144`), bears explicit printed text prohibiting
use at official tournaments. Its *Shadow Knife* Ability matches the scanner's
literal hand-to-Bench pattern, but the scanner's private legality predicate
checked only database bans and an incomplete overlay.

The corrected census contains **123** prints, **48** names, and **51**
fingerprints. The downstream Bench-trigger lifecycle analysis now reports the
correct input population; its **22** self-vacating prints across six names
were unaffected.

The separate `bench_resource_catalog` reused the same incomplete predicate,
potentially exposing Greninja ★ as a legal Bench-entry effect. Its general
legal-card iterator now yields **14,829**, excluding seven explicitly
tournament-prohibited promo prints.

## Resolution

Both catalogs call the existing shared
`build_expanded_legality_baseline.classify_effective_legality` function
to avoid contradictory print-level tournament judgments. Source card data in
`resources/cards/en/swshp.json` supplies the exact physical-print rule and
the Shadow Knife wording.

Run `python -m results.bench_trigger_tournament_exclusion.reproduce`.
The reproducer checks the prohibited Greninja source card, the full trigger
and lifecycle populations, and the full legal Bench iterator against the
set of seven printed tournament exclusions. The workflow additionally runs
existing exact opening-role and lifecycle regressions.

These are catalog corrections. Real-deck setup probabilities require a
separate check of their modeled decklists; this census alone cannot
establish changed simulation outputs.
