# Conditioning on an opening target Basic changes deck-search availability

## Why revisit the setup-zone prior?

The first Grand Tree probability model fixes **one designated Basic card**
as already present in the seven-card opening hand. This condition is
exactly appropriate if the deck contains one target Basic copy, or
when that particular copy is deliberately specified as a known
opening-hand card.

A real deck may play several eligible Basics. Conditioning instead on
**at least one of r target Basic copies** being in the opening seven
is a different event. It changes the distribution of evolution cards
between the remaining hand, six Prizes and searchable deck.

This result computes that event exactly without inventing a
full-game setup simulator.

## Model

The 60-card deck has `r` target Basic copies, `a` Stage 1 copies,
`b` Stage 2 copies, and `60-r-a-b` exchangeable filler.
Draw seven opening-hand cards and condition on at least one target
Basic being present. Then set six Prizes from the remaining 53.
The event of interest is that at least one Stage 1 and one Stage 2
remain among the 47 deck cards after this process.

Other filler Pokémon may be Basics. The conditional event here concerns
the specified *target* Basic family only, so it makes no claim about
the unconditional mulligan rate of a complete deck.

## Exact formula

Let `N=60`, `H=7`, `P=6`, `u=H+P=13`,
`B` be the event that the opening hand contains at least one of
the `r` target Basics, and `E_m` be the event that **all `m`
copies of one named evolution-stage family are absent from the final
deck**.

By symmetry,

```text
P(E_m) = C(H+P,m)/C(N,m)
P(no target Basic in hand) = C(N-r,H)/C(N,H).
```

When the hand contains no target Basic, all seven cards were drawn
from the `N-r` other cards. For `h` copies of the particular
stage family in hand, its probability is
`C(m,h) C(N-r-m,H-h)/C(N-r,H)`. The remaining `m-h` copies
must then all land among six Prize cards, with conditional probability
`C(P,m-h)/C(N-H,m-h)`.

Thus the conditional missing-deck probability is:

```text
q_r(m) = P(E_m | B)
       = [P(E_m) - P(no-Basic-hand) *
          sum_h(
            C(m,h) C(N-r-m,H-h)/C(N-r,H)
            * C(P,m-h)/C(N-H,m-h)
          )] / P(B).
```

If the no-target-Basic-hand event is impossible, the formula
reduces to the unconditional missing-deck probability.

Since the Stage 1 and Stage 2 families are disjoint,
inclusion-exclusion gives the desired exact result:

```text
P(Stage 1 and Stage 2 both have deck copies | B)
 = 1 - q_r(a) - q_r(b) + q_r(a+b).
```

## Comparison: both evolution stages singletons

| Copies of target Basic | Conditional full-chain deck access |
| ---: | ---: |
| 1 | 63.1794% |
| 2 | 63.0607% |
| 3 | 62.9440% |
| 4 | 62.8298% |
| 8 | 62.4008% |

The difference is small but real. With more target Basic copies,
conditioning on at least one of them is less restrictive than fixing
a specific Basic in hand. A model that silently substitutes the
designated-Basic condition changes the probability distribution.

For `r=1`, both conditional experiments are identical. The exact
full-chain result reduces to `1081/1711`, as proven by the earlier
`grand_tree_initial_zone_probability` model.

## Independent verification

`tools/grand_tree_target_basic_conditioning.py` implements two
independent exact-Fraction computations:

1. A closed-form inclusion-exclusion expression that subtracts the
   no-target-Basic-hand worlds.
2. An exhaustive four-category multivariate-hypergeometric enumeration
   of target Basics, Stage 1, Stage 2 and filler across hand, Prizes
   and deck.

`python results/grand_tree_target_basic_conditioning/reproduce.py`
checks all `r=1..5`, `a=0..4`, `b=0..4` combinations,
plus multiple smaller setup populations. It also verifies the
equivalence to the previous designated-Basic model when `r=1`.

## Limits and interpretation

This is an exact *initial setup-zone* result conditional on an
opening target Basic. It does not model Grand Tree's activation
timing, future draw or search, Stage 1 cards in hand as an alternative
line, prizes taken, mulligan retries, opponent play, or the outcome
of any actual decklist. In particular, Grand Tree's printed restriction
still forbids evolving a Basic during the player's first turn.

Deck-building recommendations should use this as a precise baseline
within a richer model. A small difference in this one conditional
availability probability does not establish a strategically better
or worse Basic count.
