# Balance remains optimal after conditioning on an opening target Basic

## Extension

The original balanced Stage 1/Stage 2 allocation theorem optimized
immediate deck-search availability after fixing one designated Basic
in the opening hand. The generalized model instead conditions on
**at least one of r target Basic copies** appearing in the hand.

The exact probabilities change slightly under that event, but the
optimal allocation remains balanced for a fixed total number of
copies across Stage 1 and Stage 2.

## General proof

Let the full deck have `N` cards, of which `r` are target Basics.
Condition on the opening hand containing at least one of them.
Among the remaining `N-r` non-target-Basic identities, let
`U` be the random number occupying hand or Prize locations,
so those `U` cards are not searchable by Grand Tree.

Conditional on any realized target-Basic placement and resulting
`U=u`, exchangeability of the other card identities gives:

```text
q_u(k) = P(all k cards of one evolution stage outside deck | U=u)
       = C(u,k)/C(N-r,k).
```

For each fixed `u`, the sequence `q_u(k)` is a discrete
nonincreasing convex sequence with diminishing consecutive decreases.
Taking the conditional expectation over the random `U` preserves
this convexity:

```text
q_r(k) = E[q_U(k) | >=1 target Basic in opening hand].
```

Inclusion-exclusion again gives

```text
P(both evolution stages searchable | Basic in hand)
    = 1 - q_r(a) - q_r(b) + q_r(a+b).
```

At fixed `a+b`, the last term is constant. Since `q_r`
is convex, moving copies toward an equal split cannot reduce this
joint deck-search probability. Therefore a balanced feasible split
maximizes the stated objective under the generalized condition too.

## Conditional 60-card examples

With seven opening hand cards and six Prizes:

| Target Basic copies | 2/2 evolution split | 1/3 evolution split |
| ---: | ---: | ---: |
| 1 | 92.3940% | 79.0930% |
| 2 | 92.3388% | 79.0135% |
| 4 | 92.2307% | 78.8585% |
| 8 | 92.0263% | 78.5688% |

These are initial zone-availability baselines. A stronger real-game
deck construction conclusion would require the value of other card
effects, setup access, hand-based evolution, later draws, opposing
disruption and matchups.

## Reproduction and provenance

`tools/grand_tree_slot_allocation.py` now exposes
`conditional_frontier()`, reusing the exact conditional probability
model from `grand_tree_target_basic_conditioning.py`.

`python results/grand_tree_slot_allocation_conditioned/reproduce.py`

The reproducer tests 1..12 target Basic copies, all fixed evolution
budgets 2..8 with the ordinary four-per-stage cap, and multiple
smaller finite-population variants. It also checks discrete convexity
directly using exact rational arithmetic, and proves the one-target-
Basic case matches the original designated-Basic model.

## Evidence level

Mathematical theorem for the stated finite-population objective.
The runnable checks verify implementation and representative
parameter spaces; the mixture-of-convex-sequences argument gives
the more general reasoning.

This result is orthogonal to whether running more Basic cards
actually improves or harms a complete deck.
