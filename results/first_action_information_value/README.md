# When knowing hidden Prizes before the first action would matter

## Exact information operator

Suppose a player observes their hand and legal first actions, but the exact Prize configuration is hidden. Let `w` range over hidden worlds with conditional probability `p(w)`. Let `W(w)` be the set of first actions that admit a successful **adaptive continuation** after the player next searches and reveals the deck.

Two genuinely different decision quantities are:

- **Clairvoyant feasibility:** sum of `p(w)` over worlds with a nonempty `W(w)`.
- **Nonanticipative success:** maximum, over first actions `a`, of the sum of `p(w)` over worlds where `a` belongs to `W(w)`.

The **information gap** is the first quantity minus the second. It is always nonnegative. A common first action that succeeds in *every positive-probability world where any first action could succeed* makes the gap exactly zero. If the intersection of those successful first-action sets is empty, the gap is positive. Worlds in which success is impossible with any first action impose no additional restriction.

This is a binary objective. The same reasoning applies with utility values after replacing success sets by worldwise expected conditional utilities, but the simple successful-action intersection criterion no longer generally suffices.

Implementation: `tools/first_action_information_value.py`. It uses `Fraction` and returns the two values, their difference, all maximizing first actions, and a universal successful-action witness when it exists.

## Validated examples

The minimal contested example has two equally probable hidden worlds: the first is winnable only by leading with an Item called A, and the second only by leading with B. A clairvoyant player succeeds in 100% of worlds; a K0 player must commit and succeeds in at most 50%; the information gap is 50 percentage points. This is an abstract decision matrix, not a literal Pokémon matchup.

A second example has winning actions {A,B} in one world and {B} in the other. B succeeds in both. Both values equal 100%, so the information gap vanishes.

The executable regression independently enumerates **584 asymmetric-weight decision matrices** with one to three available actions and three hidden worlds. Every exact value and successful-action intersection is checked against separate direct formulas.

## Published Regidrago application

The [Regidrago K0 first-Item study](../regidrago_k0_joint_launch/) already has an exact Prize-conditioned first-action kernel. Across the **five published or one-card-swap Regidrago 60-card candidates** at D=0 and D=10, its information gap is exactly zero. This is supported by the original full-information category solver and independent physically labeled ten-card BF searches. The result narrows the search for bias in that particular first-turn proxy: the first Item commitment does not affect access to its two stated simultaneous resources. Later choices or other contested strategic goals remain open.

**CI:** [Manual exact decision and Regidrago comparison, run 38280453044](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38280453044).

## Practical use

A card-access graph should not automatically credit the availability of different first actions in mutually exclusive hidden worlds. Build world-specific complete legal action sets, evaluate the first actual decision on the observation available at that decision, then optimize continuations after any information-revealing action. The operator makes this information boundary measurable.

The underlying `W(w)` must come from trustworthy rule-constrained state transitions. Abstract labels and exact fractions alone do not validate a deck's real-world win rate.
