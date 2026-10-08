# Hidden-Prize payment-information penalty depends on replacement cards

## Problem

Prior exact models of Secret Box's three-card discard **before** the first deck search quantified:

- a 6.733 percentage-point clairvoyance gap in one fully specified visible hand;
- a 0.072988-point opening-weighted gap for one illustrative 60-card deck.

These magnitudes should not be promoted to universal values. The distribution
of acceptable payments and the searchable replacement copies changes the
geometry of the underlying hidden-state optimization.

This exact sensitivity scan varies disposable-card density and Item/Stadium
redundancy while retaining the same Box-first Tool A + Tool B + Stadium +
Special Energy in-hand acquisition endpoint.

Implementation: tools/secret_box_k0_sensitivity.py.
Reproducer: results/secret_box_k0_sensitivity/reproduce.py.
Sources: results/secret_box_k0_payment/ and
results/secret_box_k0_opening_mix/.

## State and counting method

One Secret Box is conditioned to be in the initial seven. Among the other 59
cards, exactly 12 protected cards are eligible Basic starters. The other six
opening cards must include at least one. Then one natural draw occurs and six
hidden Prizes are integrated by exact multivariate-hypergeometric counting.
Guzma & Hala is available to be played after Box when searched or held.

Every configuration has 60 physical cards including Box, 6 hidden Prizes and
fixed terminal categories. The initial Box discard choice must be identical
across hidden worlds compatible with the visible hand, while post-search
choices can use knowledge of the remaining deck. This creates the exact
K0 versus clairvoyant K1 comparison.

## 1. Disposable-card sensitivity

Hold Item I=1, Tool A=2, Tool B=1, Guzma & Hala=2, Stadium=2, Special Energy=1.
Replace protected nonstarter filler with cards classified as currently
disposable, keeping twelve protected Basics.

| Disposable D | K0 acquisition success | K1 minus K0, percentage points |
| ---: | ---: | ---: |
| 5 | 2.267262% | **0.008983** |
| 10 | 9.162455% | **0.031600** |
| 15 | 20.420234% | **0.055774** |
| 20 | 34.324041% | **0.072988** |
| 25 | 48.593357% | **0.078288** |
| 30 | 61.078543% | **0.070282** |
| 35 | 70.270364% | **0.051142** |

The penalty peaks near 25 disposables within the tested grid, then falls.
This is a strict nonmonotonicity witness: improving the probability of
having sufficient discard stock can increase the number of relevant
alternative payment policies, then eventually make most payment choices
unimportant once enough surplus material exists.

This latter mechanism is a **hypothesis** based on the model's payment
geometry, not an experimentally isolated decomposition.

## 2. Item and Stadium redundancy

Fix D=20, Tool A=2, Tool B=1, Guzma & Hala=2, Special Energy=1 and
twelve protected Basics. Vary Item and Stadium deck copies by replacing
protected nonstarter filler. The table shows **K1 - K0**, in percentage
points, for all twenty configurations.

| Stadium S \ Item I | 0 | 1 | 2 | 3 | 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 2 | 0.000381 | 0.072988 | 0.089662 | 0.093680 | 0.094946 |
| 3 | 0.000112 | 0.086092 | 0.102625 | 0.104799 | 0.104034 |
| 4 | 0.000020 | 0.088307 | 0.103694 | 0.104680 | 0.102809 |

**One-Stadium boundary:** in all five tested Item densities with S=1,
K1 and K0 agree exactly, despite K0 acquisition probability increasing
from 4.197988% to 25.798485%. There is no information-dependent
initial payment advantage for these particular states.

**Increasing redundancy can create an information penalty:** changing
from one to two Stadium copies while I=1 creates a gap of 0.072988 points.
The same comparison with I=0 produces only 0.000381 points. Making more
downstream replacement resources searchable can unlock lines where
discarding a potentially useful held card is justified in some hidden
Prize worlds, but needs preservation in others.

**More copies need not mean a larger error:** S=3, I=3 produces a
0.104799-point gap, slightly above S=4, I=3 at 0.104680, and S=3, I=4
at 0.104034.

## Exact finite-decision interpretation

For a fixed observed hand h, let P(h) be its finite set of legal
pre-search three-card payments. Let E_p be the set of hidden Prize worlds
where payment p can reach the terminal acquisition goal after optimizing
the known-deck continuation.

Then for the conditional hidden-world measure:

    K1(h) = Pr( union_{p in P(h)} E_p )
    K0(h) = max_{p in P(h)} Pr(E_p)

Consequently the information penalty is exactly the probability mass of
the union of success events beyond the largest single payment-success
event. It vanishes if some one payment succeeds in every hidden world
where any payment succeeds (up to zero-probability states). Otherwise the
penalty is positive.

This event-family interpretation is **mathematically exact** for binary
terminal success. It directly explains why the count of possible
payments alone is insufficient: payment outcome events must differ
across hidden worlds for advance Prize information to have value.

## Validation

Exact rational output is used for all calculations. Fixed regression
fractions and structural inequalities check selected configurations.
The underlying K0 model has an independent physically labeled hidden
Prize oracle over 48 states; the accepted-opening mixture has a labeled
opening/draw oracle over 121 small-deck states and 3465 weighted orders.

The new scan verifies that each 60-card composition remains fixed-size,
and that the information gap never exceeds the probability mass of
visible hands in which a gap exists. No Monte Carlo sampling occurs.

## Limitations

All results condition on Box in the initial hand and a legal Basic start.
The disposable/protected classification is an abstract fixed state, so
changing D is an intervention in that classification. The line assumes
an available Supporter play and can end after acquiring cards in hand.
No full board, Tool attachment, Stadium play, opponent locks, earlier
deck-search observation, Prize-taking, tactical damage, or win-rate
endpoint is evaluated.

These numbers demonstrate how **optimizer information bias** changes
with deck architecture. They do not establish a preferred tournament
deck composition or a measurable win-rate penalty.

A practical next test is to perform the same K0/K1 comparison in actual
Expanded lists and terminal board-execution simulations, especially
states with mixed unique and redundant Stadium, Supporter and Tool
functions.
