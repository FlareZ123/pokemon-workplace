# Replacement multiplicity and the value of Prize information

## Question

How does replacement copy count change the value of knowing exact Prize composition before choosing an endpoint-critical discard?

The earlier K0 discard-reacquisition result assumed one replacement copy for each discard candidate. This result generalizes that model to arbitrary replacement multiplicities.

Implementation: `tools/replacement_information_value.py`  
Reproducer: `results/replacement_information_value/reproduce.py`

## Model

There are `U` unknown own cards split between the deck and `P` face-down Prizes.

Each endpoint-critical discard candidate `i` has `r_i` replacement copies somewhere in that unknown pool.

A candidate is **live** when at least one replacement copy remains outside the Prize cards.

The player must discard exactly `d` critical classes.

- A K0 policy chooses one fixed `d`-class subset before seeing Prize composition.
- A K1 policy sees exact Prize composition first and may choose any `d` live classes.

Grouped Prize allocations are weighted exactly by the multivariate hypergeometric distribution. All reported probabilities are exact rational values before formatting.

## 52-card first-turn benchmark

With `U=52` and `P=6`:

| Replacement copies per candidate | Critical candidates | Required discards | Best K0 success | K1 success | Information value |
| --- | ---: | ---: | ---: | ---: | ---: |
| (1, 1) | 2 | 1 | 88.461538% | 98.868778% | **10.407240 pp** |
| (2, 2) | 2 | 1 | 98.868778% | 99.994459% | **1.125681 pp** |
| (3, 3) | 2 | 1 | 99.909502% | 99.999995% | **0.090493 pp** |
| (1, 1, 1) | 3 | 2 | 78.054299% | 96.787330% | **18.733032 pp** |
| (2, 2, 2) | 3 | 2 | 97.743097% | 99.983388% | **2.240291 pp** |

Replacement multiplicity sharply suppresses the value of Prize information.

## Asymmetric replacement counts

For replacement counts `(1, 2, 3)` with two required critical discards, the optimal K0 policy selects the two- and three-copy classes.

This follows from the exact hidden-state calculation rather than a heuristic DCI score. A class with more independent replacement copies is less likely to have every replacement Prized.

The K1 policy still retains an advantage because it can opportunistically use the one-copy class in worlds where that class is live and one of the more redundant classes is completely Prized.

## Strategic interpretation

A binary label such as “reacquirable” loses important information.

The safety of discarding an endpoint-required card depends on:

- how many replacement copies exist;
- how many of those copies can be hidden in the Prize cards;
- how many critical discards must be selected;
- whether the discard choice is made at K0 or K1.

This gives a quantitative version of transient DCI. The same physical card can have a very different discard value at the same board state when the actor's information state changes.

## Information value is largest near a scarcity boundary

Two limiting cases have little or no information value:

- abundant replacement multiplicity makes almost every candidate live;
- a forced payment with no choice among critical candidates gives the policy nothing to adapt.

The largest gaps occur when several candidates are plausible, some can be completely cut off by Prizes, and the payment must select a strict subset of them.

That is the same structural region where continuation-aware discard families become strategically interesting.

## Relationship to the card-pool catalog

`cost_before_search_catalog/` identifies legal Expanded Trainers whose literal text creates a discard-before-search boundary.

This result supplies a generic quantitative kernel for evaluating those cards when their payment candidates have different replacement multiplicities.

It can be attached to a deck-specific simulator once the simulator provides:

- the actor's observation at the payment deadline;
- candidate discard classes;
- replacement copy counts;
- the future search channels that make those replacements strategically equivalent.

## Limitations

The model treats a replacement class as live whenever at least one replacement copy remains outside the Prize cards.

It does not model:

- connector contention;
- Supporter or Item locks;
- replacement copies already consumed elsewhere;
- different search eligibility among copies;
- Bench or Active constraints;
- deadlines beyond the immediate continuation;
- opponent interaction;
- partial information such as Stellar Wish.

Those effects can be layered onto the exact hidden-state kernel through the repository's continuation and belief-state tooling.
