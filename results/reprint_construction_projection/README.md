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

The current resolver avoids the Master Ball and Computer Search projection hazards.

The five historical Master Ball prints are known non-equivalent, so they have no resolver target to project from.

The two historical Computer Search prints are also known non-equivalent. Current Standard and Expanded reprint policy requires all printed text to be functionally identical. The legal Expanded Computer Search target carries an ACE SPEC deck restriction that is absent from both historical prints.

Shining Celebi remains a live illustration of target ambiguity. Historical `neo4-106` is still in semantic review. Its legal same-name targets include `me55c-106`, which carries the same singleton rule, and `smp-SM79`, which has different gameplay text and no singleton rule.

## Implementation

`tools/reprint_construction_projection.py` compares exact source-print copy-limit rules with every legal Expanded same-name target and with the target prints selected by the current reprint resolver.

The regression asserts the eight current name-level hazards and checks how the resolver narrows them.

## Consequence for deck adjudication

Deck construction should remain attached to the submitted exact print until policy evidence explicitly says which construction rules transfer across a reprint relationship.

This is why `tools/deck_legality_proof.py` first validates the exact submitted prints and then evaluates format-legality provenance. A reprint target is evidence for legality resolution and is not a substitute physical card for deck-construction analysis.

## Scope

The detector currently audits explicit card text containing `can't have more than ... in your deck`. Future card families could encode construction restrictions through another wording or metadata category, so this is a conservative audit of the rule forms present in the current snapshot.
