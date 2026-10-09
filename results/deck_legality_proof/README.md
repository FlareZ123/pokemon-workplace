# Compositional deck legality proof

## Question

Can a concrete paper Expanded deck be evaluated without conflating exact-print deck construction, current Expanded status, dated bans, release timing, and historical reprint evidence?

## Result

`tools/deck_legality_proof.py` composes the existing deck-construction validator with `LegalityProvenanceIndex` and returns a three-way deck disposition:

- `eligible_snapshot`: every exact print passes construction rules and has enough evidence for the selected policy;
- `invalid`: a construction rule fails or at least one print has affirmative evidence that it is unavailable for the evaluated boundary;
- `unresolved`: at least one print still depends on incomplete historical timing or functional-reprint evidence.

The default `conservative` policy preserves high-confidence reprint candidates as unresolved.

An optional `current_semantic_evidence` policy accepts three current evidence classes when an Expanded target is already available:

- exact current-semantic fingerprint candidates;
- current official errata candidates;
- current Tournament Handbook semantic candidates.

Historical-only official reprint evidence remains unresolved under this profile. Semantic-review prints also remain unresolved.

## Exact-print construction remains separate

The existing validator previously loaded only Black & White-onward Expanded-set records. This result refactors it to expose `validate_deck_construction()`, which applies deck-building rules to every exact print in the bundled snapshot while deliberately skipping format-legality decisions.

The original `validate_deck()` behavior remains the format-specific path.

This separation matters because construction rules can be print-specific. The 30th Celebration Classic Collection Shining Celebi carries a one-copy self-name rule, so exact print text remains visible during separate legality resolution.

## Current-state versus historical-date evidence

The bundled legality snapshot is current evidence, while only some historical boundaries have explicit dates.

The proof treats direct `post_release_not_audited` prints as eligible only when the query date is at least the snapshot reference date. The boundary is derived from the latest Expanded-set release present in the bundled snapshot. For this snapshot that date is 2026-09-16.

Earlier historical queries leave unaudited release timing unresolved.

The same principle applies to current database bans that lack an effective date. Dated official overlays remain decisive at their explicit boundaries.

## Historical reprints

The legality provenance layer distinguishes exact current-semantic matches, historical official evidence, official errata, explicit handbook semantic evidence, known non-equivalence, and unresolved semantic review.

Under `current_semantic_evidence`, old Copycat `ex7-83` becomes eligible through the explicit Tournament Handbook equivalence example. Exact-fingerprint Fisherman `ecard3-125` and official-errata Leftovers `dp4-99` also become eligible.

Historical Double Colorless Energy `base1-96` remains unresolved because its evidence is a historical official reprint source rather than one of the accepted current semantic classes.

Old Computer Search remains invalid because the legal Expanded target carries an ACE SPEC deck rule that is absent from the historical prints.

## Regression witnesses

`results/deck_legality_proof/reproduce.py` checks the direct current path, audited release waiting periods, both reprint evidence policies, current semantic promotion, historical-only evidence, semantic review, known non-equivalence, current bans, historical timing uncertainty, print-specific Shining Celebi limits, and unknown print IDs.

## Scope

The result is an auditable research adjudicator for the bundled English snapshot. It does not claim universal regional legality. The returned proof retains `semantic_source = bundled_en_snapshot` and `regional_legality_scope = not_evaluated`.

A later regional layer can compose with this proof while preserving its exact-print and reprint-evidence distinctions.

## Pre-release current banned prints

The [unreleased print priority result](../unreleased_banned_print_priority/) prevents a current banned flag from masking definitive historical pre-release unavailability. Shaymin-EX xy6-77 queried in 2014 is invalid because its set had yet to release; 2016 ban timing remains unaudited.
