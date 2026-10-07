# Multi-target public search signaling

## Question

Can the existing K1 target-selection belief model represent a public search event that removes more than one selected card from the deck?

Yes.

Implementation extension: `tools/deck_search_target_signal.py::resolve_revealed_search_targets_shuffle`  
Regression: `results/multi_target_search_signal/reproduce.py`

## Representation

The existing `TargetSelectionPolicy` already maps exact Prize-composition states to arbitrary public string labels. A label can therefore represent a canonical multi-target observation such as `XY`, an ordered sequence, an unordered set, or another caller-defined event.

The new resolver separates two concerns:

- `observed_target` is the public event used for Bayesian conditioning;
- `removed_target_groups` is the exact sequence of modeled groups physically removed from the deck-plus-Prize pool.

Each removed card decreases the pool size by one. Repeated modeled groups are decremented repeatedly and cannot exceed the available pool count. Unmodeled selected cards can be represented by `None`; they reduce pool size without changing a modeled group count.

## Analytic witness

The regression uses seven hidden-zone cards:

- singleton A, X, Y, and Z;
- three unmodeled fillers;
- two Prize cards.

The deterministic selection policy publishes `XY` exactly when A is Prized while X and Y are both unprized.

The actual actor world has A plus one filler Prized. Observing `XY` therefore tells the other observer:

- A is Prized;
- X and Y are unprized;
- the second Prize is either Z or one of the three fillers.

X and Y are then removed from the pool before the shuffle.

For the actor, the remaining deck is Z plus two fillers, so:

`P(top = Z) = 1/3`.

For the observer, Z is the unknown second Prize with probability `1/4`. Otherwise Z is one of three deck cards. Therefore:

`P(top = Z) = (3/4)(1/3) = 1/4`.

The regression reproduces both values exactly.

It also verifies that trying to remove two X cards from a pool containing only one X is rejected.

## Strategic significance

Multi-output searches can leak information through the combination of targets chosen after private full-deck inspection.

The information event and the physical target removals should be represented separately. A canonical target-set label is useful for conditioning, while exact group removals determine the post-search deck/Prize pool from which the shuffled top is drawn.

This is the missing belief primitive needed to extend Battle VIP Pass and similar public multi-target direct-Bench searches beyond single-target signaling.
