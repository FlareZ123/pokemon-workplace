# Prize-aware three-support chain with stochastic Bench release

## Question

A Bench slot may be recycled more than once. When three *different*
singleton support Pokémon must each enter from hand, how do their joint
access probability, search-connector sharing, and number of pickup successes
interact?

This generalizes [the two-trigger baseline](../bench_double_trigger_release/)
to two through five distinct singleton supports. Both variants use the same
accepted-opening and hidden-Prize model.

- Model: [bench_multi_trigger_access.py](../../tools/bench_multi_trigger_access.py)
- Independent exhaustive oracle: [reproduce.py](reproduce.py)

## Mechanical model

Assume a normal five-slot Bench with `q` slots available for transient
support Pokémon, where `q >= 1`. The `n` distinct support Pokémon all
require hand-to-Bench entry; every successful pickup can remove a spent
resident support without losing the already-performed trigger.

The minimum number of pickup **successes**, regardless of which support is
picked up, is

`k = max(0, n - q)`.

If the visible hand contains `g` guaranteed pickup Items and `r` fair
independent coin-flip pickup Items, the conditional success probability is

`P(release | visible hand) = 2^(-r) sum_{j=max(0,k-g)}^r C(r,j)`.

An empty sum equals zero. For example, with three supports and one slot, two
successes are needed: observing exactly two coin pickups succeeds with
probability `1/4`, while observing all four succeeds with probability
`11/16`. With two free slots, only one success is needed, and all four
visible flips succeed with probability `15/16`.

The model enumerates accepted opening hands, later random-card access, and
hidden Prize dispositions. It enforces a distinct deck-to-hand connector for
every missing singleton and excludes direct-from-deck-to-Bench placement
as a source of hand-entry triggers. If no other Basic appears in the opening,
one support singleton must become the starting Active.

## Exact 60-card sensitivity

The illustrative deck has three different singleton support Basics, four
other ordinary Basic starters, four ideal deck-to-hand Basic search Items,
four direct-to-Bench connectors, and four Super Scoop Up-like coin pickup
Items. There are six Prizes, seven opening cards, and four additional
uniformly random cards. Other slots are filler.

All reported probabilities are conditional on an accepted ordinary-Basic
opening. Each row represents a **different initial persistent core Bench
occupancy**, changing the available slack.

| Free Bench slots `q` | Required pickup successes | Nominal joint access | Role-aware | Typed, one-use search | Coin-weighted executable access |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 7.527194% | 4.664345% | 0.393795% | **0.105588%** |
| 2 | 1 | 31.828384% | 20.050087% | 2.156556% | **1.180277%** |
| 3 | 0 | 60.280359% | 38.411541% | 4.827882% | **4.827882%** |

In this benchmark, nominal one-slot feasibility is over **70 times**
the coin-weighted typed probability. A one-slot estimate that treats a
single reachable pickup as enough for three support entries even misstates
the *number of necessary actions*. Increasing slack from one to two
corresponds to moving from four protected core Bench occupants to three,
so this sensitivity must be interpreted together with the opportunity
cost of that lost core slot.

The three-slot case needs no pickup, but still has a substantial access
penalty from the starting-Active and one-use connector effects. Search
capacity and Bench-release capacity are distinct bottlenecks.

## Mathematical method

Group the deck into `n` singleton target classes, ordinary Basics,
hand connectors, direct-Bench connectors, certain pickups, coin pickups,
and filler. Enumerate the opening multivariate hypergeometric count vectors
conditional on a valid ordinary-Basic start. Enumerate later visible draws.

Conditional on those visible samples, remaining hidden Prize cards are a
uniform subset of the remaining unseen population. Only the Prize
indicators of the still-unseen target singletons matter. Exact integer
weights for those Prize classes and exact binomial pickup tails are
combined into `fractions.Fraction` outputs.

The `n=2` mode reproduces the preceding two-support implementation
exactly across four independent parameter configurations.

## Independent validation

The test code independently enumerates a labeled **12-card deck**:
A/B/C singleton targets, one other Basic, two hand connectors, one
direct-Bench connector, two coin pickups and three fillers. It samples a
five-card opener, one Prize, two later cards, a physical starting Active,
and both fair coin outcomes.

Across **309,120 valid labeled sample-and-coin paths**, the independent
oracle agrees exactly with the grouped three-support implementation at
all three Bench-slack levels. Unlike a sparser first test deck, this
fixture produces strictly positive typed and stochastic access even
when two pickup successes are required.

Small-deck exact stochastic fractions are:

| Slack | Nominal | Role-aware | Typed | Coin-weighted |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1307/6440 | 375/5152 | 87/2576 | 87/10304 |
| 2 | 1573/2576 | 1275/5152 | 51/322 | 129/1472 |
| 3 | 273/368 | 1611/5152 | 5/23 | 5/23 |

## Limits and next steps

All searches are idealized single-use, zero-cost Item transitions and
every pickup is assumed available by the deadline. Real Quick Ball needs
a discard; actual support Abilities may discard or draw important hand
cards; Item lock, ACE SPEC selection, attack windows, and opponent play
are upstream constraints. The model counts the opportunity to resolve
the distinct hand-entry triggers, irrespective of their tactical value.

A useful follow-on is to compile actual support Ability execution and
hand sequencing. A Dedenne-GX activation can discard a hand containing
the pickup or a second support, creating order-dependent states that
this unordered access model deliberately excludes.
