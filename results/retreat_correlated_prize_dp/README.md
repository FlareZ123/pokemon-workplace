# Correlated-Prize Retreat payment counting with robust minimality

## Motivation

Conditional Counter Energy and Reversal Energy can supply different
amounts depending on whether their player is behind on Prize cards.
Their unit changes are tied to the **same global Prize comparison**:
all eligible copies share one possible lower world and one possible
higher world. Treating every card's eligibility as an independent coin
flip invents impossible joint configurations.

The prior `retreat_prize_minimality_paradox` demonstrated why
intersecting already-pruned minimal sets can erase a guaranteed
legal payment. This result counts all four relevant action-frontier
quantities without enumerating every labeled physical subset.

## Exact dynamic program

Each caller-certified interchangeable Energy group carries:

- Physical copy count.
- Its number of Energy units in the tied/on-par world.
- Its number of Energy units in the behind-on-Prizes world.

Both regimes share a single global comparison, and the model
requires the lower units to be positive and no greater than the
higher units. A dynamic program aggregates weighted physical
subsets by the number of selected cards, total units in each world,
and smallest selected-card units in each world.

Each selected class count receives a binomial multiplicity.
The represented physical payment bound still requires no more
selected cards than the numeric Retreat Cost.

The output distinguishes:

1. **Robust legal:** selected Energy units pay cost in both worlds.
2. **Possible legal:** selected units pay cost in at least one world.
3. **Robust minimal:** inclusion-minimal among guaranteed actions.
4. **Intersected worldwise minimal:** minimal in each world separately.

For monotone Counter/Reversal-style providers, the robust legal
frontier equals the lower-energy-world legal frontier, because
every payment valid in that world is also valid in the higher one.
Worldwise minimality need not obey that monotonicity.

## Concrete witness

Active Retreat Cost 2, one eligible Counter Energy and one Basic
Energy attached:

| Prize regime | Legal payments | Minimal payments |
| --- | --- | --- |
| Tied | Both cards | Both cards |
| Behind | Counter alone; both cards | Counter alone |
| Unknown | Both cards guaranteed; Counter alone contingent | Both cards robustly minimal |

The robust payment count is one and the possible-payment count is
two. Its robust-minimal count is one, while the count surviving
premature worldwise-minimal intersection is zero.

## Independent validation

The reproducer constructs physical EnergyAttachment objects and
calls the canonical labeled-card payment enumerator separately for
the two known regimes. It explicitly forms robust action intersections
and computes inclusion-minimal payment sets by strict subset
comparisons, independently of the dynamic program.

A Cartesian suite of **567 cases** uses zero through two copies
each of Counter Energy, Reversal Energy, DCE and Basic Energy,
with costs zero through six. It cross-checks every count reported
by the DP against the brute-force physical sets.

The dedicated CI additionally runs the exact original
1,792-case board-derived Prize minimality regression.

Run `python results/retreat_correlated_prize_dp/reproduce.py`.

## Scope and limitations

This is a deterministic numeric-count model for a fixed holder with
resolved eligibility and one common behind-Prizes predicate.
Different holder states can make Counter or Reversal Energy
ineligible, in which case both per-world unit values should be one.
It does not infer holder tags, Ability locks, Bench access,
discard destinations, turn budget or the actual public Prize counts.

More general incomplete information can affect Retreat Cost, card
destinations or action prohibitions, where the simple nested
low/high action-set argument may fail. Such cases require a
richer state model. The output is a count of action witnesses,
not a probability distribution across games.

The main planning lesson is that robust legality is evaluated
before optional strategic pruning, with the shared uncertainty
handled jointly rather than independently card by card.
