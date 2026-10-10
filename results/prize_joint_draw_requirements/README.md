# Simultaneous Pokémon and Energy access: a multivariate draw-window model

## Question

Deck setup frequently requires **several different resource categories** inside the same opening draw or reset window. Can a model multiply separately correct card-access probabilities to estimate the probability of satisfying all required categories?

In general, no. Drawing without replacement makes category exposures dependent, and an ordered near-future deck prefix may further constrain the joint event.

## Representation

`tools/prize_joint_draw_requirements.py` implements `probability_joint_draw_requirements`, taking:

- a `PrizeDeckPrefixBelief` containing the top card, a finite ordered suffix prefix, and an exchangeable deeper remainder, with full group-count conservation;
- a mapping from disjoint strategic card groups to required minimum draw counts;
- the number of upcoming draws;
- an optional full-deck shuffle before drawing.

For each physical support world:

1. Count the already determined group occurrences in the portion of the known top/prefix falling inside the draw window.
2. Subtract those counts from each category's requirement.
3. Compute the **multivariate hypergeometric tail** for all remaining categories simultaneously in the unknown suffix, with the unmodeled remainder pooled into a single category.
4. Average the conditional success probabilities using the joint world's mass.

If `M_i` cards of each required category `i` remain among `N` exchangeable cards, and `u` cards are drawn, the conditional probability is a sum over feasible counts `x_i`:

\[
P(\forall i:\,x_i\ge r_i)
=\frac{1}{\binom Nu}
\sum_{\substack{x_i\ge r_i\\ \sum_i x_i\le u}}
\left(\prod_i\binom{M_i}{x_i}\right)
\binom{N-\sum_iM_i}{u-\sum_ix_i}.
\]

Impossible selections contribute zero. This is a finite exact-combinatorial formula, evaluated as floating-point probabilities in the current research API.

## Five-card independent experiment

Suppose a five-card deck contains `X, P1, P2, E, F`. Here `P1` and `P2` are two Pokémon-category cards, `E` is one Energy-category card, and `X,F` are other cards. The player knows the top is X; the other four positions are uniformly exchangeable.

Draw the next **three** cards. Success requires **at least one P and one E**.

- Exact joint success: **1/3**.
- Marginal probability of seeing P: **5/6**.
- Marginal probability of seeing E: **1/2**.
- Incorrect product of marginals: **5/12**.

The product estimate therefore overstates success for this setup condition. A full-deck shuffle before drawing raises joint success to **1/2** by making the known miss X eligible to move out of the three-card draw window.

If the player additionally knows the second card is E, the probability of meeting both conditions rises from **1/3 to 2/3**; if the third card is also known to be a Pokémon, success is certain.

For a stronger requirement, both P copies plus E within the next four draws occurs with probability **1/4** while X is fixed on top, or **2/5** after a full shuffle.

## Verification

The regression independently enumerates all **120 labeled permutations** of the five-card deck and the **24** with X on top, and checks each joint success rate with exact rational counts. It also verifies:

- one-category queries reproduce the earlier univariate draw exposure kernel;
- private second/third-position knowledge changes the joint result as predicted;
- empty and zero-threshold requirements;
- invalid category, negative, or fractional requirements are rejected.

## Implications and scope

This directly addresses a frequent deck-optimization failure: independently estimating access to a Pokémon and an Energy, then multiplying these marginals, can misestimate whether a fully executable turn exists.

Even this improved direct-draw model does **not** establish whether the player can play or search the drawn cards that turn. A complete planner must still model Supporter contention, activation constraints, Energy attachment limits, payment discards, Bench spaces, item locks, Prize risk and sequencing.

All requirement groups here are **mutually exclusive** modeled card categories. A physical card that simultaneously satisfies several logical roles would require a richer Boolean eligibility representation, rather than counting it independently in overlapping categories.

The deeper deck suffix is exchangeable unless a source effect supplies additional order information. All examples are finite card-arrangement calculations rather than observed tournament statistics.

## Next

Compose category requirements with realistic line-specific constraints and existing card-access graphs. Study overlapping-role cards and resource contention, particularly whether the same search connector can satisfy both Pokémon and Energy channels on a single turn.
