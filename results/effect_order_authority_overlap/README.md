# Overlapping effect-order authority

## Question

What should a simulator do when multiple evidence-backed ordering rules appear
applicable to one event and those rules identify different players?

Implementation: `tools/effect_order_authority_overlap.py`
Regression: `results/effect_order_authority_overlap/reproduce.py`

## Evidence boundary

The existing `effect_order_authority` result preserves separate ordering scopes
from the bundled Advanced Player's Rulebook.

Two scopes matter for this investigation:

1. The bundled rulebook says that when several Pokemon are Knocked Out at the
   same time and several effects activate from those Knock Outs, the player
   whose turn is being played decides their order.
2. The official Pokemon Asia Q&A for Lost City and Reuniclus says the owner of
   Reuniclus chooses whether Persistent Cells or Lost City resolves first.

Official Q&A:
https://asia.pokemon-card.com/ph/rules/search/?keyword=Lost+City

These statements have different scopes. The repository currently has no
authoritative evidence that establishes precedence when a local Lost
City/Persistent Cells ordering question occurs inside a multi-Pokemon Knock Out
event.

## Representation

`resolve_overlapping_authority()` takes the authority cases that an upstream
semantic layer considers applicable. It evaluates each case through the existing
`ordering_player()` catalog and returns one of three states:

| Status | Meaning |
| --- | --- |
| `resolved` | Every case has enough context and identifies the same player. |
| `missing_context` | At least one case lacks required role information. |
| `conflict` | Every case resolves individually, but the cases identify different players. |

The overlap layer does not rank the rules.

## Counterexample

Suppose Player A is taking the turn and Player B owns the Reuniclus. If an
upstream semantic model asserts both authority scopes, the existing evidence
produces two claims:

- multi-Pokemon Knock Out scope -> Player A;
- Lost City/Persistent Cells scope -> Player B.

The combined status is `conflict`. This repository layer therefore authorizes
neither player until a more specific rule or ruling resolves the overlap.

## Safe collapse when roles coincide

If Player A is both the current-turn player and the Reuniclus owner, both claims
identify Player A. The concrete chooser is then Player A regardless of which
scope has precedence.

The resolver returns `resolved` for that concrete state.

This lets an engine continue when every applicable evidence-backed claim agrees
while preserving uncertainty only where an unknown precedence can change who
controls the choice.

## Finding

Rule uncertainty and game-state uncertainty are separate dimensions.

An unresolved relationship between two rules does not make every concrete state
unresolvable. Execution depends on whether the applicable authority claims
disagree after player roles are instantiated.

A conservative simulator can therefore:

1. identify the exact evidence-backed authority scopes that apply;
2. instantiate each scope against current player roles;
3. execute when all concrete claims agree;
4. surface an explicit authority conflict when claims disagree;
5. add precedence only when stronger evidence supports it.

## Limits

This result does not claim that the multi-Pokemon rule and the
Lost City/Persistent Cells ruling necessarily overlap in every simultaneous
Knock Out state. Applicability belongs to the semantic rules layer.

The current conclusion is narrower: the repository does not yet contain evidence
that justifies a precedence rule for that overlap. Future authoritative rulings
can refine the resolver without discarding this claim-based representation.
