# Scaling the G&H Prize-information frontier to a 52-card hidden pool

## Why the larger state matters

The [small twelve-card G&H K0/K1 model](../gnh_prized_spare_information_frontier/)
proved a nontrivial information option value, but its gross five-card
Ticket-access improvement was 10/99, or about ten percentage points.
A first-turn paper Expanded state after a seven-card opener and one
normal turn draw instead has **52 initially unseen cards**, including
six initial Prizes, before accounting for other searches.

This continuation derives the same counterfactual using a 52-card
hidden pool without enumerating its many individual Prize
combinations.

## State and exact reduction

The abstract fixed hand already holds G&H, one TM: Evolution, one
Jet Energy, and two resources deemed expendable for this particular
exercise. The unseen physical pool contains **52 cards**:

- one Artazon;
- one spare TM: Evolution;
- one spare Jet Energy;
- one Ticket-role Item;
- forty-eight other physically distinct cards.

Exactly `P` of those cards are uniformly Prized; a future unused
Jirachi Stellar Wish looks at five cards after G&H searches and
shuffles the deck. The player may keep the two hand resources and
search Artazon when unprized, or commit the two-card payment
**before the deck search** and also fetch the spare Tool and Special
Energy if unprized. The Player's Rulebook permits declining an
unavailable category-limited search result.

We group Prize allocations by which subset of the **four
distinguished names** is Prized. For a specific distinguished subset
of size `k`, its exact probability is

`C(48, P-k) / C(52,P)`.

There are at most sixteen such subsets, and every remaining card
is exchangeable under the defined payoff. This compresses a
many-million-world calculation into an exact rational sum of a
constant-sized decision table, preserving correlation among
the named sources.

The paid choice incurs a hypothetical scalar continuation cost
`lambda >= 0`. K0 chooses pay/keep once before learning
the Prize map; an idealized costless K1 observation lets it
choose separately in each world. As before, **real Tag Call is
a material search action**, so free K1 is an upper-bound reference.

## Six-Prize result

The [exact search-thinning theorem](../prized_filler_search_invariance/)
gives the mean of each material search line for any valid
`P`:

| Search choice | Ticket chance after Wish |
| --- | ---: |
| Search Artazon without paying | **5/51 = 9.80392157%** |
| Pay and also fetch spare TM and Jet when available | **5/49 = 10.20408163%** |
| Gross gain before discard cost | **10/2499 = +0.40016006 pp** |

The K0 payment-choice switch therefore occurs exactly at
`lambda = 10/2499`. At that same threshold, the K0 player is
indifferent between the two choices; the idealized K1 observer
chooses the better one separately in each Prize world.

For **six uniformly Prized cards**:

- optimal K0 value: `5/51 ≈ 0.0980392157`;
- K1 value: `25989/262990 ≈ 0.0988212480`;
- ideal information premium:
  **`617/788970 ≈ 0.0007820323`**, or
  **+0.07820323 percentage points** of this synthetic
  one-Ticket-access objective.

The gross mean physical thinning gain is constant across
`P=0..6`, whereas the ideal information premium in this particular
toy increases with Prize uncertainty:

| Prized cards | Information premium at the common K0 threshold, percentage points |
| ---: | ---: |
| 0 | 0 |
| 1 | +0.015237 |
| 2 | +0.029568 |
| 3 | +0.043013 |
| 4 | +0.055588 |
| 5 | +0.067312 |
| 6 | +0.078203 |

These are conditional theoretical payoffs, **not** tournament
first-turn success rates or recommendations to discard two
valuable cards for a fraction of a percentage point of
Ticket access. The prior small-deck 10.10-point witness and
the 52-card +0.40-point calculation are consistent results
at different hidden-pool sizes.

## Reproduction

Engine: [tools/gnh_large_unseen_information_frontier.py](../../tools/gnh_large_unseen_information_frontier.py).
Regression: [reproduce.py](reproduce.py).

The regression verifies the four-category grouped exact solver
against fully labeled physical Prize-subset enumeration for
hundreds of smaller-deck parameter cases. It also reproduces
the earlier twelve-card exact model over a multi-cost grid,
checks physical thinning invariance across `P=0..6`,
and asserts the `U=52,P=6` rational fractions.

## Limits and next use

The source search card must be in hand and legally playable.
The searched Artazon, Tool and Energy must still be in the
correct zones. Source costs, resource scarcity, Bench readiness,
late Stellar Wish timing, other draw/Prize mechanics, and
matchup-specific continuation value are not included. Treat
`lambda` as an invented illustrative scalar that invites
sensitivity analysis rather than a calibrated card value.

For real Aichi experiments, this exact result is most useful
as a local analytical oracle for a fixed K0 observation class
in which the sources have known names and the hidden pool
has the stated composition. A deck-wide optimal policy
must still aggregate over **actual opening-hand observation
classes**, Supporter choices, G&H payments, and alternate
Tag Call/Stellar Wish lines.
