# Typed search zone transition

## Question

When a compiled search action is feasible, is the strategic demand-output vector alone sufficient to update the physical zone state?

No.

A demand profile can merge distinct physical target choices. The state transition must retain the richer exact action that records which target groups were consumed.

Implementation: `tools/search_zone_transition.py`  
Regression: `results/typed_search_zone_transition/reproduce.py`

## Counterexample

Consider one search output:

`Search your deck for 1 Energy card.`

The deck contains one Basic Fire Energy and one Double Colorless Energy, and the current strategic demand is simply one generic Energy card.

The typed target allocator correctly reports one demand profile:

`(1,)`

That profile is strategically useful, but it aliases two exact actions:

- consume the Basic Fire Energy target group: `target_cost=(1, 0)`;
- consume the Double Colorless Energy target group: `target_cost=(0, 1)`.

Those actions produce different hand states even though their demand output is identical.

This matters because later attack readiness, typed Energy requirements, discard costs, and other card-specific transitions can distinguish the two cards.

## Transition boundary

`apply_typed_search_action()` binds each allocator target position to the card-class namespace used by `ZoneCountState`, then moves exactly the consumed copies from deck to hand.

The bridge verifies target-vector dimensionality, nonnegative action values, consistency between consumed targets and supplied units, current source-zone availability, allocator target-copy capacity, and per-card-class conservation. It also rejects stale actions whose selected target is no longer present in the source zone.

## Why copies remain exchangeable

Searching a card from deck into hand does not itself create board topology or copy-specific persistent history.

The transition therefore stays in the exchangeable count layer:

`deck count -> hand count`

It deliberately does not assign an arbitrary physical instance ID. Instance materialization remains reserved for relations such as an Energy attached to one Pokémon, an evolution stack, or another state where individual copies cease to be exchangeable.

## Result

The regression produces one collapsed demand profile, two exact target actions, and two distinct hand outcomes while conserving both card-class totals.

This closes one part of the compiler-to-state gap: exact typed search choices can now mutate canonical exchangeable zone counts without losing physical target identity at the class level.

## Limits

This transition executes only the searched-card movement. It does not yet consume the Trainer card itself, pay discard costs, consume Supporter/Stadium bandwidth, shuffle the deck, or compose a complete Trainer action transaction.

Those resources already exist in adjacent kernels. A stronger follow-up should make the full connector action atomic across search target movement, action-cost payment, Trainer-card disposal, and turn-budget consumption.
