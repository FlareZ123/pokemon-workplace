# Connector bottleneck regimes

## Question

When one universal search connector is shared by two required target channels,
where does a deck-construction slot have more local value: another direct out
to a target, or another currently disposable card that makes the connector
easier to pay?

This extends `results/connector_slot_marginals/` from one baseline to an
exhaustive exact grid.

Implementation: `tools/connector_bottleneck_regimes.py`  
Reproducer: `results/connector_bottleneck_regimes/reproduce.py`

## Exact grid

The scan holds these assumptions fixed:

- 60 cards;
- 6 Prize cards;
- accepted 7-card opening;
- 12 protected setup starters;
- exactly one universal connector;
- target A copies in 1 through 4;
- target B copies in 1 through 4;
- disposable non-starters in 0 through 35;
- discard cost 1, 2, or 3.

At each point, one protected filler slot is converted into one of:

- +1 target-A out;
- +1 target-B out;
- +1 disposable card.

The objective is **capacity-aware, discard-gated joint access** from the
existing connector-domination model. One connector can repair only one missing
channel.

The dense scan uses the analytically Prize-collapsed solver. The reproducer
cross-checks representative extrema against the original full Prize-state
enumeration.

No Monte Carlo sampling is used.

## Result

There are 576 states per discard cost, 1,728 states total.

| Discard cost | +A wins | +B wins | A/B tie | +disposable wins |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 216 | 216 | 144 | 0 |
| 2 | 216 | 216 | 144 | 0 |
| 3 | 216 | 216 | 144 | 0 |

Every strict winner is the direct out to the **scarcer target channel**.

When A and B have equal copy counts, their one-slot marginals tie exactly.

The disposable-card substitution never wins and never ties for first anywhere
in this grid.

This is an exhaustive computational result for the stated model and range. It
is not a theorem about arbitrary deck states.

## How large is the separation?

Even the closest state leaves a nontrivial gap between the best direct out and
the disposable-card marginal:

| Discard cost | Tightest state (A, B, D) | Best direct minus disposable |
| ---: | --- | ---: |
| 1 | (1, 1, 0) | 0.817298 pp |
| 2 | (1, 1, 2) | 0.937609 pp |
| 3 | (1, 1, 5) | 0.947319 pp |

The largest disposable-card marginal observed at each cost is:

| Discard cost | State (A, B, D) | +1 disposable gain |
| ---: | --- | ---: |
| 1 | (4, 4, 0) | 0.444682 pp |
| 2 | (4, 4, 15) | 0.203421 pp |
| 3 | (4, 4, 30) | 0.200388 pp |

So the absence of a disposable-winning region is not caused only by already
saturated discard payability. The best observed discard-density interventions
remain below the direct-out marginal.

## Interpretation

The grid exposes three distinct local bottlenecks.

First, a direct out can satisfy its channel without consuming the shared
connector. That removes connector contention in states where the other channel
still needs the connector.

Second, an extra disposable card only changes whether the connector can be
paid. It does not increase the connector's one-card output capacity.

Third, the lower-count target has the larger marginal because joint success is
more sensitive to the weaker direct-access channel under this symmetric
abstract setup.

This sharpens the earlier connector-slot result: within ordinary 1-through-4
target counts, improving binary DCI by one card is never the best local slot
use in this exact same-window model, even when discard payability is poor.

## What this does not establish

The result does not say that discardability is generally unimportant.

It also does not say that every real deck should maximize direct copies.
Real cards can differ in power, searchability, evolution requirements, Energy
burden, matchup value, Bench cost, legality, Supporter contention, and whether
multiple card names serve one functional channel.

The binary disposable/protected split remains a deliberately narrow DCI model.

A different state model, larger effective-out counts, multi-output connectors,
or a card whose discardability also has independent strategic value can create
different marginal rankings.

## Modeling implication

A deck optimizer should not assign one global value to "search connectivity"
or "discard density."

Under connector contention, direct redundancy and connector payability solve
different failure modes. Local marginal evaluation should preserve connector
capacity and compare the active failure modes explicitly.
