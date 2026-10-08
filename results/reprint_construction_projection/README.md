# Reprint construction-rule projection hazard

## Question

Can a historical print inherit deck-construction restrictions from any legal Expanded print with the same name?

## Result

A name-level projection is unsafe in the bundled snapshot.

The audit finds eight outside-scope prints across three names where at least one legal Expanded same-name target carries a different explicit copy-limit rule:

| Historical family | Outside-scope prints | Construction difference |
| --- | ---: | --- |
| Computer Search | 2 | historical prints have no ACE SPEC deck rule; the legal Expanded target is an ACE SPEC |
| Master Ball | 5 | historical prints have no ACE SPEC deck rule; the legal Expanded targets are ACE SPEC prints |
| Shining Celebi | 1 | legal same-name targets disagree with each other about the self-name singleton rule |

This audit establishes a representation constraint. It does not decide tournament legality for unresolved historical prints.

## Resolver-aware interpretation

The current resolver already avoids two of the broad hazards.

The five historical Master Ball prints are known non-equivalent, so they have no resolver target to project from.

The historical Shining Celebi `neo4-106` is an exact current-semantic candidate for `me55c-106`. Those two exact prints carry the same singleton rule. The other legal same-name Shining Celebi print has different gameplay text and no singleton rule. Target identity therefore matters.

The remaining direct witness is old Computer Search. Both `base1-71` and `base4-101` remain in semantic review. Their same-name Expanded target `bw7-137` carries the ACE SPEC deck-wide restriction while the historical prints do not.

A future equivalence ruling for Computer Search would therefore need an explicit policy decision about deck-construction semantics. Effect equivalence alone cannot safely determine the legal copy count.

## Implementation

`tools/reprint_construction_projection.py` compares exact source-print copy-limit rules with:

1. every legal Expanded same-name target;
2. the target prints selected by the current reprint resolver.

The regression asserts the eight current name-level hazards and checks how the resolver narrows them.

## Consequence for deck adjudication

Deck construction should remain attached to the submitted exact print until policy evidence explicitly says which construction rules transfer across a reprint relationship.

This is why `tools/deck_legality_proof.py` first validates the exact submitted prints and then evaluates format-legality provenance. A reprint target is evidence for legality resolution. It is not a substitute physical card for deck-construction analysis.

## Scope

The detector currently audits explicit card text containing `can't have more than ... in your deck`. Future card families could encode construction restrictions through another wording or metadata category, so this is a conservative audit of the rule forms present in the current snapshot.
