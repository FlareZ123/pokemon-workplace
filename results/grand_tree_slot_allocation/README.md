# Balanced Stage 1 / Stage 2 counts maximize joint deck accessibility

## Question

Under a fixed number of Pokémon evolution slots allocated between
Stage 1 and Stage 2, what copy split maximizes the probability that
Grand Tree can search at least one card of *each* stage from the
remaining deck at initial setup?

This is a narrowly defined **joint access** objective. It deliberately
does not include evolving naturally from hand, different evolution
engines, tactical tech cards, future draw sequencing, Prize recovery,
or the value of additional Stage 1 bodies.

## Exact theorem

Let `N` uniformly random cards remain after one designated Basic
has already been placed in the starting hand. Let `u` of those `N`
cards be outside the searchable deck, split into other opening hand
and Prize slots. Put `a` Stage 1 copies and `b` Stage 2 copies among
those `N` cards.

Define `q(k)=C(u,k)/C(N,k)` for `0<=k<=u`, and `q(k)=0`
for `k>u`. This is the probability that *all* copies in one
evolution-stage family miss the deck.

Then inclusion-exclusion yields:

```text
P(both stages have >=1 deck copy)
    = 1 - q(a) - q(b) + q(a+b).
```

For a fixed total `t=a+b`, `q(t)` is constant. Maximizing the
probability is equivalent to minimizing `q(a)+q(t-a)`.

The consecutive decreases of `q` are

```text
d(k) = q(k) - q(k+1) = q(k)*(N-u)/(N-k)

d(k+1)/d(k) = (u-k)/(N-k-1) <= 1
```

for `k < u`, and afterward both terms are zero.
Thus `q(k)` is a nonincreasing discrete convex sequence. Moving
one card from the larger count toward the smaller count cannot increase
`q(a)+q(b)`, so **the most balanced feasible split is optimal**.
For feasible, unsaturated practical 1..4 copy budgets, its optimum
is unique up to interchanging Stage 1 and Stage 2.

This is a general finite-population combinatorial result; the
standard `N=59`, `u=12` Grand Tree setup model is one instance.

## Exact 59/12 results

| Total stage copies | Best split(s) | Probability both stages in deck |
| ---: | :--- | ---: |
| 2 | 1/1 | 63.1794% |
| 3 | 1/2 or 2/1 | 76.4804% |
| 4 | 2/2 | 92.3940% |
| 5 | 2/3 or 3/2 | 95.4817% |
| 6 | 3/3 | 98.6486% |
| 7 | 3/4 or 4/3 | 99.2147% |
| 8 | 4/4 | 99.7825% |

At a four-slot budget, the balanced `2/2` split has 92.3940%
joint availability. The `1/3` split has 79.0930%, a **13.3009
percentage point** decrease for this particular objective.

The result does not imply that a player should always run a balanced
Pokémon evolution line in a real deck. More copies of the Stage 1 may
be valuable for natural evolution, utility Abilities, deck-specific
access restrictions, discard cost, or simultaneous evolution lines.
A Stage 2 in the hand may be useful through another route, and Grand
Tree cannot evolve a Basic during the player's first turn.

## Reproduction

`python results/grand_tree_slot_allocation/reproduce.py`

The reproducer checks 1..4 copy splits for totals 2..8 with exact
fractions and independent discrete convexity certificates. It then
tests the proof across `N=10..18`, `u=0..N-1` using exact arithmetic
and exhaustive split enumeration within four copies per stage.
It imports `probability_full` from the previously validated
`grand_tree_initial_zone_probability.py` module.

## Implication for optimizers

Search-based deck optimizers can use the exact balance result as a
diagnostic *for a clearly declared objective and available slots*.
If a candidate split is strongly unbalanced while a modeled effect
needs at least one searchable card of each category, the optimizer
should identify a compensating benefit that outweighs the measurable
loss in joint deck access.

A full competitive deck optimizer must evaluate those other benefits
rather than treating the static theorem as an unconditional decklist
prescription.
