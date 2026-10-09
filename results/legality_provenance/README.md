# Evidence-bearing legality provenance

## Question

The repository now has separate evidence layers for direct Expanded status, current ban overlays, functional-reprint candidates, product release timing, and regional semantic-source coverage. Can a caller inspect those layers in one place without silently collapsing them into a single boolean?

## Result

`tools/legality_provenance.py` provides a compositional view for every card in the bundled English snapshot.

It deliberately returns a **disposition plus evidence fields**, rather than an unconditional `legal=True/False` for historical reprints.

The view carries:

- exact card ID, name, set, and query date;
- direct current Expanded status and source when the print belongs to a Black & White-onward Expanded set;
- date-aware application of the repository's official Flapple and Medicham V ban overlays;
- product-release timing state for audited release anchors;
- the reprint resolver state for outside-scope prints;
- target-print timing evidence for high-confidence reprint candidates;
- explicit statements that the semantic source is the bundled English snapshot and regional legality has not been evaluated.

## Direct-print date behavior

For direct-set prints, the composition separates timing cases.

A print queried before its database set release date is `direct_not_yet_released`.

For the audited 30th Celebration sets, September 16, 2026 is the product anchor and September 30 is the ordinary tournament-legality date. Thus `me55c-106` is `direct_release_waiting` on September 29 and `direct_legal_release_verified` on September 30 and later.

Older post-release sets without an audited product calendar remain `direct_legal_snapshot_timing_unverified`. That label means the current Expanded snapshot directly includes the print, while this tool has not reconstructed the historical product-release schedule needed to answer every arbitrary past date.

The repository's official overlay entries carry effective dates, so they are applied at the correct boundary. Medicham V `swsh7-83` remains database-legal on April 9, 2026 under this historical query, then becomes `direct_banned` from the official overlay on April 10. The same mechanism covers the October 10, 2025 Flapple overlay.

Database bans and card-text tournament exclusions without a repository effective date remain current-state facts. This module does not invent historical effective dates for them.

## Historical reprint behavior

Outside the direct Black & White-onward set scope, the provenance view preserves the resolver's evidence category.

High-confidence repository candidates include exact current-semantic fingerprint candidates, historical official no-reference candidates, current official-errata candidates, and explicit current-handbook semantic candidates. They receive `high_confidence_reprint_candidate`, rather than `direct_legal`.

Examples:

| Card | Reprint evidence | Disposition |
| --- | --- | --- |
| `ecard3-125` Fisherman | exact current-semantic | high-confidence candidate |
| `pl1-108` Life Herb | exact current-semantic | high-confidence candidate |
| `ex7-83` Copycat | current-handbook semantic | high-confidence candidate |
| `base1-96` Double Colorless Energy | historical official | high-confidence candidate |
| `dp4-99` Leftovers | official errata | high-confidence candidate |
| `ex5-90` Life Herb | known non-equivalent | known non-equivalent |
| `base1-87` Pokédex | semantic review | unresolved semantic review |

For candidate rows, target-print IDs remain visible, along with whatever release-timing evidence is available for each target.

## Why this matters

A correct legality answer can depend on direct set scope, exact-print bans, the date a ban took effect, product release timing, functional equivalence, evidence quality, regional availability, and card-specific restrictions.

A one-bit flag makes it easy to erase provenance and accidentally apply current facts to historical dates. This view keeps those dimensions inspectable and lets downstream tools choose their evidence threshold.

## Regional boundary

This module does not claim that the bundled English snapshot defines worldwide paper Expanded.

The repository's separate `regional_card_source.py` has already demonstrated Japanese paper Expanded cards absent from the English snapshot. The provenance record therefore states `regional_legality_scope = "not_evaluated"` rather than silently treating English source coverage as a global legality decision.

A future region-aware legality query should compose this print-level provenance with an official or otherwise provenance-bearing regional availability source.

## Reproduction

`results/legality_provenance/reproduce.py` checks the 30th Celebration September 30 boundary, the Medicham V April 10 ban boundary, ordinary direct prints, a direct banned print, each major high-confidence historical reprint path, the Life Herb negative boundary, and the unresolved Pokédex observation boundary.

## Limitations

The historical date model is intentionally partial.

Only official overlay bans with explicit dates and audited product anchors are date-aware. Other database bans and older product schedules remain current-snapshot evidence.

A high-confidence reprint candidate is still evidence, not an automatic tournament ruling. The current functional-reprint rule, regional availability, promo legality schedules, and card-specific restrictions must be satisfied by the final consumer.

## Next work

Extend the provenance record with an explicit regional availability object and an audited promo/product calendar. The eventual legality proof object should explain an accepted or rejected deck print by source, date, region, semantics, and restriction.

## Pre-release overrides undated current bans

The source-derived release date is decisive for a print queried before its release, even when its current database ban has an unknown historical effective date. See [unreleased ban precedence](../unreleased_banned_print_priority/), which distinguishes the 2014 pre-release Shaymin-EX result from historically unresolved 2016 ban timing.

## Outside-set physical print availability

The [outside-set source-release audit](../outside_source_release_gate/) adds a release-before-reprint-evidence gate. All 25 Celebrations Classic Collection prints were unavailable as physical prints before their 2021 set release, even if identical older legal Expanded card text already existed. This records source timing as before_set_release while retaining the separate semantic reprint class.
