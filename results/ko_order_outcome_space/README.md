# Exact outcome space of ordered Knock Out redirections

## Question

Given already-compiled destination programs for several simultaneously available KO effects, how many **physically different** outcomes can their externally permitted application orders produce? Which order witnesses each physical result?

The existing `knockout_redirection_conflicts.py` detects disagreeing per-card destinations and `knockout_redirection_ordering.py` resolves one selected order. The new `tools/ko_order_outcome_space.py` enumerates the **outcome space** without requiring a factorial scan through every permutation.

## Semantics and scope

The input is `{effect_id: {physical_card_id: explicit_destination}}`. On each physical card, the first explicitly assigned destination wins. The default final destination for an untouched card is `discard`. Crucially, an explicit `discard` assignment cannot be collapsed into an unassigned card: it can preempt a subsequent conflicting route.

Optional `precedences=((before_id, after_id), ...)` are constraints supplied by an external authority/eligibility analysis, never inferred by this tool. All linear extensions of those constraints are counted. With no precedence constraints, every total order is counted. These counts are **numbers of orderings**, not probabilities of gameplay decisions or estimates of tournament frequency.

The solver uses a subset dynamic program whose state is (chosen-effect bitmask, first-explicit-assignment vector). It accumulates the exact integer multiplicity of each state and a lexicographically smallest witness. Once all effects have been applied, states are projected onto physical destinations, coalescing even those whose effect provenance differs.

## Exact illustrative witness

Three *abstract* route programs use the destination geometry of a return-to-hand effect, Lost City-like redirection, and selected attached-Energy recovery:

- `return: {pokemon: hand, energy: discard}`
- `lost: {pokemon: lost_zone, energy: discard}`
- `recover: {energy: hand}`

Under six unconstrained abstract orderings, there are exactly four physical outcomes:

| Pokemon | Energy | Orders | Example witnessing order |
| --- | --- | ---: | --- |
| hand | discard | 2 | return, lost, recover |
| lost_zone | discard | 2 | lost, recover, return |
| hand | hand | 1 | recover, return, lost |
| lost_zone | hand | 1 | recover, lost, return |

Requiring `recover` before `return` leaves three physical outcomes among three orders. Requiring `return` before both alternatives leaves a **single** physical result among two orders.

These effects are an abstract conflict-surface construction: the tests do not claim the three corresponding real card effects can all activate simultaneously in an actual game. Their trigger legality, effect activation scope, card-specific predicates, and actual chooser remain outside the tool.

A second witness has two conflicting assignments for one Pokemon (`hand` and `lost_zone`). Without constraints there are two outcomes; a supplied precedence requiring `hand` first yields one. This is a precise reason that a static detected conflict need not imply uncertainty after legal order constraints are applied.

## Reproduction and independent validation

Run `python results/ko_order_outcome_space/reproduce.py` from the repository root. The test implements an independent factorial `itertools.permutations` oracle. It verifies outcome multiplicities and lexicographically earliest witnesses for 225 deterministic random cases (one to five effects), including random acyclic precedence constraints, and tests malformed/cyclic precedence rejection. A ten-effect disjoint example compresses `10! = 3,628,800` orderings to one physical outcome.

The correctness argument is inductive. Every permitted total order has a unique first effect, then a unique sequence of allowed prefix states. The dynamic program extends exactly those prefixes and sums counts whenever the used-set and assigned route vector agree. Future extensions depend only on that state, so merging prefixes cannot change any downstream physical destination or its multiplicity. The final projection merges states that share the same destination for each physical instance.

This exactness is **conditional on the first-assignment model and supplied legality constraints**. Resolving late trigger eligibility, event creation, KO chaining, authority conflicts between official sources, and the consequences of other game-state mutations require further work. The current code does not replace `ko_redirection_authorized_order.py`; it can serve as a diagnostic stage before a player legally selects one order.

## Research relevance

The destination count is a more refined measure of order sensitivity than the presence of a conflict. Especially where many effects touch disjoint cards or agree on destinations, large numbers of syntactically different orderings may collapse to few materially distinct states. An optimizer can reason about outcome equivalence classes without treating action-order count as strategic value.
