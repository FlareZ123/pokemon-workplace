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

This audit establishes a representation constraint.

## Resolver-aware interpretation

The current resolver avoids all three broad name-level projection hazards.

The five historical Master Ball prints are known non-equivalent, so they have no resolver target to project from.

The two historical Computer Search prints are also known non-equivalent. Current Standard and Expanded reprint policy requires all printed text to be functionally identical. The legal Expanded Computer Search target carries an ACE SPEC deck restriction that is absent from both historical prints.

Historical Shining Celebi `neo4-106` now resolves through an exact current-semantic fingerprint to `me55c-106`. Those two prints carry the same singleton rule. The unrelated legal same-name print `smp-SM79` has different gameplay text and no singleton rule, so exact target identity remains important.

## Implementation

`tools/reprint_construction_projection.py` compares exact source-print copy-limit rules with every legal Expanded same-name target and with the target prints selected by the current reprint resolver.

The regression asserts the eight current name-level hazards and checks how the resolver narrows them.

## Consequence for deck adjudication

Deck construction remains attached to the submitted exact print until policy evidence identifies a valid reprint relationship.

This is why `tools/deck_legality_proof.py` validates submitted print construction before evaluating format-legality provenance. The resolved target contributes legality evidence without replacing the physical source print in construction analysis.

## Scope

The detector currently audits explicit card text containing `can't have more than ... in your deck`. Future card families could encode construction restrictions through another wording or metadata category, so this is a conservative audit of the rule forms present in the current snapshot.
