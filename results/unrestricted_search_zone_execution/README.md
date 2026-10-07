# Conserved unrestricted-search execution: physical selection exceeds useful output

## Question

Can the fixed-count rulebook exception be executed against the repository's aggregate zone state while preserving the distinction between strategically useful output and physical cards moved?

Yes.

Implementation: `tools/unrestricted_search_zone_execution.py`
Regression: `results/unrestricted_search_zone_execution/reproduce.py`

## Representation

Each selected card class carries two counts:

- `amount`: physical copies that must leave the deck;
- `useful_units`: copies credited to the current strategic demand.

The executor checks the physical total against the rulebook-backed unrestricted fixed-count bound from `unrestricted_search_selection.py`. It then moves every selected copy through `ZoneCountState`, preserving per-class totals.

The current constrained typed-search path keeps its stronger invariant that selected units equal supplied demand units. This new layer leaves that semantic island unchanged.

## Computer Search witness

The regression starts with two fallback classes in the deck and no represented desired target. Executing an exact-one unrestricted search moves one fallback card into hand while supplying zero useful units.

So the transition has physical selected units 1 and useful supplied units 0. An empty selection is rejected while the deck is nonempty.

This is the state transition a demand-only miss cannot represent.

## Mallow witness

The exact-two regression starts with one desired card and two filler cards. The legal execution selects the desired card plus one filler.

It therefore has physical selected units 2 and useful supplied units 1. Both selected cards move from `deck` to `deck_top`, and per-class totals remain conserved. A one-card selection is rejected.

## Zone counts are insufficient for ordered topdeck payloads

Two Mallow executions select the same desired-plus-filler multiset. One orders the desired card first; the other orders the filler first.

Their aggregate `ZoneCountState` values are identical. Their `top_order` values differ.

This gives a concrete proof that an ordered top-deck relation is a separate state dimension from zone multiplicity. Index 0 of `top_order` is the next card to draw.

That distinction matters for draw sequencing, top-card effects, and multi-turn policy even though card conservation sees the two states as identical.

## Short-deck behavior

An exact-two unrestricted search against a one-card deck selects the one remaining card. This carries the closest-possible boundary through the same execution path.

## Architectural implication

Search execution now has three separate quantities:

1. card-text requested cardinality;
2. physical selected-card witness;
3. strategically useful output credited to current demands.

For selector-limited search, the current typed semantic island can often identify the last two. Unrestricted exact-count search can separate them sharply.

For destinations with intrinsic structure, such as an ordered top deck, the physical witness also needs destination topology after selection.

## Limits

This layer expects a search-ready aggregate state whose searchable copies are in the `deck` zone. It does not itself perform the preceding full-deck shuffle/topology collapse or hidden-information update. Those belong to the existing deck-search/shuffle kernels.

It currently supports hand and ordered-top destinations only.

## Next work

Compose this execution with the physical search/shuffle belief bridge so an unrestricted search can update K1, consume mandatory filler, and then establish exact ordered top-deck payloads without losing conservation or observer-relative hidden-state support.
