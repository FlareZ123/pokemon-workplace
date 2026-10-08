# Exact K0/K1 access for a discard-fed Teleport Room line

## Question

Once a live Gothitelle / Teleport Room can exploit a Sky Field discarded by
Ultra Ball, what is the probability of accessing that particular legal line
when Ultra Ball, Sky Field, and an additional discard payment must all become
available in a short random hand window?

This result quantifies a *specified conditional branch*. It builds on
[`teleport_discard_payload_line`](../teleport_discard_payload_line/) and
[`bench_teleport_capacity_bridge`](../bench_teleport_capacity_bridge/).

- Exact code: [`tools/teleport_discard_access_bound.py`](../../tools/teleport_discard_access_bound.py)
- Independent labeled-state regression: [`reproduce.py`](reproduce.py)
- GitHub Actions: [passing run 37771960886](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37771960886)

## Scope of the probability

The board is **already** under Collapsed Stadium at four-of-four occupancy,
the ordinary Stadium-play quota is exhausted, and a live Gothitelle source
still has Teleport Room available. One required Basic entrant is already in
hand. Another specific singleton Basic must still be in the deck so that
Ultra Ball can retrieve it. Item lock, Ability lock, opposing Roadblock,
alternative recovery actions, and other card interactions are excluded.

The unseen portion of the deck before Prize setting contains 46 physical
cards, partitioned into disjoint strategic groups:

| Category | Copies | Function |
| --- | ---: | --- |
| Ultra Ball (U) | 4 | Pay discard two, then retrieve the singleton |
| Sky Field (S) | 2 | One copy must go from hand to discard |
| Approved other discard (D) | 16 | One other card pays Ultra Ball's second discard |
| Specific singleton target (T) | 1 | Must remain searchable in the deck |
| Filler (F) | 23 | Irrelevant to this bounded execution |

First, six face-down Prize cards are sampled uniformly; then five cards are
sampled uniformly from the remaining 40. The line becomes accessible when
the five seen cards include U, S, and D, and T lies in neither the six Prizes
nor the five seen cards. The counted U/S/D categories are disjoint. Payment
cards are assumed fully available for this intended line.

The event does not count hands where T was naturally drawn, where alternative
legal discards exist outside D, or where other cards could reach the same
Bench objective. The derived probability is not a whole-game win rate.

## Exact expression

Let N be the original unknown pool size, p the six Prize cards, h the later
random hand sample, and U/S/D the sizes of the three disjoint card categories.

For a successful singleton search, the target T must remain in the deck.
Conditioned on that event, the h observed cards are uniformly chosen from
N-1 other physical cards. An inclusion-exclusion calculation gives:

```text
P(line) = (N-p-h)/N *
    [sum over J subset of {U,S,D}:
       (-1)^|J| * C(N-1-sum_{j in J} n_j, h)
     ] / C(N-1,h)
```

The first factor is the exact singleton-searchability probability. The
summation requires at least one accessible card of every required category.
The model evaluates fractions exactly, without Monte Carlo error.

An intentionally optimistic graph-access comparator omits D from the
inclusion-exclusion requirement while keeping U, S, and T. That reveals the
cost of **ignoring the second physical discard payment** under this model.

## Results

<details>
<summary>K0 marginal over random Prizes</summary>

For N=46, p=6, h=5, U=4, S=2, D=16, and singleton T=1:

| Outcome | Exact probability | Percent |
| --- | --- | ---: |
| Full bounded line, payment-aware | 7280/174537 | **4.171035%** |
| Access-only, second discard ignored | 213800/4014351 | **5.325892%** |
| Optimism gap (percentage points) | Comparator minus full line | **1.154857 pp** |

In this regime, the extra discard requirement eliminates more than
one-fifth of the access-only successes (conditional on that comparator
event). This last statement concerns the constructed disjoint grouping.

</details>

### Access versus approved payment pool

Here N=46, six Prizes, five seen, four Ultra Ball, two Sky Field, and one
searchable singleton T remain fixed; the approved payment group D is
substituted for filler slots.

| D copies | Exact payment-aware K0 success |
| ---: | ---: |
| 0 | 0.000000% |
| 2 | 0.758529% |
| 4 | 1.441329% |
| 8 | 2.595687% |
| 12 | 3.494961% |
| 16 | **4.171035%** |
| 20 | 4.655796% |

A generic deck with other useful discardable cards will not obey these
category bounds unless its approved-discard partition is defined consistently.
This comparison is about the chosen resource model.

### K1 Prize-conditioned counterfactuals

Consider now an exact known non-Prize pool of 40 cards before the five are
seen, containing the singleton T:

| Known non-Prize category counts | Conditional five-card success |
| --- | ---: |
| All U4, S2, D16 present | **6.793838%** |
| One Sky Field Prized, leaving U4, S1, D16 | **3.523361%** |
| Both Sky Field Prized | 0% |
| Singleton target T Prized | 0% |

The K1 numbers are conditional on those explicitly different available
category counts. They should not be mistaken for the expectation over random
Prize placements.

## Validation

The SFT independently enumerates all labeled Prize-set/hand-set combinations
for two small populations and asserts exact equality with the symbolic
inclusion-exclusion calculation. It also asserts the closed-form fractions,
probability monotonicity as approved payment cards increase, and zero-access
boundaries when Sky Field, the target, or an additional discard cannot be
obtained. Run `37771960886` completed successfully.

This adds probability and Prize-status uncertainty to the deterministic
Sky Field discard sequence, while preserving a narrow explicitly declared
objective and a clear separation between physical executability and
statistical reachability.

## Limitations and next work

An established Stage 2 Gothitelle is assumed and costs nothing within the
unknown pool. The example's 46-card pool and strategic categories are
illustrative, not an actual tournament decklist. The model does not optimize
hand sequencing against alternate Ultra Ball targets, other search Items,
Supporter use, card-specific discard priorities, game turns, or failure to
establish the required board.

Potential follow-ups are to incorporate the probability of *establishing*
Gothitelle and paying evolution/Bench costs, then quantify whether the
discard-fed channel provides net improvement over direct Stadium outs.
