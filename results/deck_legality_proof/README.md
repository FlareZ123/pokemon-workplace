# Compositional deck legality proof

## Question

Can a concrete paper Expanded deck be evaluated without conflating exact-print deck construction, current Expanded status, dated bans, release timing, and historical reprint evidence?

## Result

`tools/deck_legality_proof.py` composes the existing deck-construction validator with `LegalityProvenanceIndex` and returns a three-way deck disposition:

- `eligible_snapshot`: every exact print passes construction rules and has direct current-snapshot or audited release support;
- `invalid`: a construction rule fails or at least one print has affirmative evidence that it is unavailable for the evaluated boundary;
- `unresolved`: no hard failure is known, but at least one print still depends on incomplete historical timing or functional-reprint policy evidence.

The important methodological change is that strong reprint evidence does not silently become a tournament legality ruling.

## Exact-print construction remains separate

The existing validator previously loaded only Black & White-onward Expanded-set records. This result refactors it to expose `validate_deck_construction()`, which applies deck-building rules to every exact print in the bundled snapshot while deliberately skipping format-legality decisions.

The original `validate_deck()` behavior remains the format-specific path.

This separation matters because construction rules can be print-specific. The 30th Celebration Classic Collection Shining Celebi carries a one-copy self-name rule, so exact print text must remain visible even when legality is resolved through a separate evidence layer.

## Current-state versus historical-date evidence

The bundled legality snapshot is current evidence, while only some historical boundaries have explicit dates.

The proof therefore treats direct `post_release_not_audited` prints as eligible only when the query date is at least the snapshot reference date, defined conservatively as the latest set release present in the bundled snapshot. For this snapshot that date is 2026-09-16.

For earlier historical queries, a direct print whose product timing was never reconstructed becomes `unresolved` rather than being backdated from current status.

The same principle applies to current database bans that lack an effective date. Dated official overlays remain decisive at their explicit boundaries.

## Historical reprints

The legality provenance layer distinguishes exact current-semantic matches, historical official evidence, official errata, explicit handbook semantic evidence, known non-equivalence, and unresolved semantic review.

This deck proof uses those categories conservatively:

- high-confidence reprint candidates remain `unresolved`;
- semantic-review prints remain `unresolved`;
- known non-equivalent outside-scope prints are `invalid`;
- outside-scope prints with no Expanded counterpart are `invalid`.

This preserves the repository's distinction between evidence quality and final tournament policy.

## Regression witnesses

`results/deck_legality_proof/reproduce.py` checks:

- an ordinary current Expanded deck reaches `eligible_snapshot`;
- a 30th Celebration print on 2026-09-29 is invalid because the audited release wait ends on 2026-09-30;
- old Copycat `ex7-83` remains unresolved despite official-semantic candidate evidence;
- old Pokédex `base1-87` remains unresolved under semantic review;
- old Rainbow Energy `base5-17` is invalid because the handbook-backed evidence marks the wording non-equivalent;
- old Computer Search `base1-71` is invalid because its ACE SPEC target has a deck rule absent from the historical print;
- a current banned print is invalid;
- a historical query predating the snapshot reference does not inherit unaudited current timing as certainty;
- exact-print Shining Celebi construction limits remain enforced on both the current Classic Collection print and historical `neo4-106`;
- unknown print IDs fail explicitly.

## Scope

The result is an auditable research adjudicator for the bundled English snapshot. It does not claim universal regional legality. The returned proof therefore retains `semantic_source = bundled_en_snapshot` and `regional_legality_scope = not_evaluated`.

A later regional layer can compose with this proof without changing its exact-print and reprint-evidence distinctions.
