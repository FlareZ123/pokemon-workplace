# Same-turn Supporter outs: exact timing-overstatement baseline

## Question

How much can a raw "outs" count overstate access to a target Supporter when some connectors are themselves Supporters and therefore consume the action needed to play the target?

This result quantifies one timing distinction identified by the repository's Gladion connector work. It is an exact combinatorial baseline rather than a deck-specific consistency estimate.

Implementation: `tools/supporter_outs_timing.py`  
Reproducer and exhaustive validation: `results/supporter_outs_timing/reproduce.py`

## Context

`results/gladion_access_connectors/` classifies real Expanded routes to Gladion by timing and zone semantics. Items and appropriate Abilities can often obtain Gladion while leaving the Supporter play available. Supporter-based connectors such as Steven or Skyla normally use that Supporter play first. Attack-based connectors cross an even stronger boundary because attacking ends the turn.

`results/supporter_connector_temporality/` states the same general action-budget principle and points out an important exception: effects such as Magnezone's Dual Brains can increase Supporter capacity.

The calculation here isolates the Supporter-capacity distinction and asks how large the numerical error can become if both connector classes are treated as equivalent outs.

## Exact model

The deck is partitioned into six categories:

1. copies of the target Supporter;
2. Supporter-preserving connectors that are setup-eligible starters;
3. Supporter-preserving connectors that are non-starters;
4. Supporter-consuming connectors;
5. filler setup-eligible starters;
6. filler non-starters.

The state is generated in game order:

1. draw an opening hand and condition on at least one setup-eligible starter;
2. set Prize cards from the remaining deck;
3. optionally observe a specified number of later random draws.

A target Supporter is **typed-accessible this turn** when at least one Supporter play remains and one of these is true:

- the target itself is in the accessible hand;
- a Supporter-preserving connector is accessible and a target copy remains in the searchable deck;
- a Supporter-consuming connector is accessible, a target remains in the searchable deck, and at least two Supporter plays remain.

The comparison quantity, **naive access**, deliberately makes one error: it treats both connector classes as if they preserve the Supporter play. The difference between naive access and typed access is the timing-overstatement probability.

All connector effects in this baseline are assumed deterministic once accessible. Real cards may add coin flips, top-N sampling, discard costs, Bench requirements, Ability lock exposure, evolution timing, or other constraints.

## Illustrative composition

Use:

- 60 cards;
- 6 Prize cards;
- a 7-card accepted opening;
- 12 setup-eligible starters;
- 2 copies of the target Supporter;
- 2 idealized deterministic non-starter connectors that preserve the Supporter play;
- 4 idealized deterministic non-starter connectors that consume one Supporter play;
- 1 ordinary Supporter play remaining.

The connector counts are illustrative. They are not a proposed deck list.

| Additional random draws before access check | Typed same-turn access | Naive reachability | Naive-only overstatement |
| ---: | ---: | ---: | ---: |
| 0 | 37.877949% | 62.704345% | 24.826396% |
| 1 | 42.525892% | 68.217314% | 25.691422% |
| 2 | 46.904688% | 72.986520% | 26.081832% |
| 5 | 58.530890% | 83.665082% | 25.134192% |
| 10 | 73.470404% | 93.212812% | 19.742407% |

With only the accepted opening hand visible, the raw graph estimate says that the target Supporter is reachable in 62.70% of states. The action-typed model says it is actually playable in 37.88% of states. The absolute overstatement is 24.83 percentage points.

After two additional random draws, the absolute overstatement reaches 26.08 points in this composition.

These values do not estimate a real Gladion deck. They quantify the size of one modeling error under a deliberately controlled composition.

## Adding consuming connectors can create fictitious consistency

Keep the two target Supporters, two preserving connectors, 12 starters, and no later random draws. Vary only the number of Supporter-consuming connectors.

| Consuming connectors | Typed same-turn access | Naive reachability | Overstatement |
| ---: | ---: | ---: | ---: |
| 0 | 37.877949% | 37.877949% | 0.000000% |
| 1 | 37.877949% | 45.122231% | 7.244282% |
| 2 | 37.877949% | 51.634959% | 13.757009% |
| 3 | 37.877949% | 57.476747% | 19.598798% |
| 4 | 37.877949% | 62.704345% | 24.826396% |
| 6 | 37.877949% | 71.525637% | 33.647688% |
| 8 | 37.877949% | 78.481813% | 40.603863% |

The typed probability stays constant because, with one Supporter play remaining, none of the consuming connectors can produce and then play the target in the same turn. The naive model interprets every added connector as consistency and can therefore report a large fictitious improvement.

This gives a precise counterexample to any optimizer that rewards raw target reachability without tracking the action class of the path.

## Supporter capacity is a state variable

Using the original two-target, two-preserving, four-consuming composition with no later random draws:

| Supporter plays remaining | Typed access | Naive access | Naive-only overstatement |
| ---: | ---: | ---: | ---: |
| 0 | 0.000000% | 0.000000% | 0.000000% |
| 1 | 37.877949% | 62.704345% | 24.826396% |
| 2 | 62.704345% | 62.704345% | 0.000000% |

With two Supporter plays available, one consuming connector plus the target Supporter fits inside the action budget. The typed model then agrees with the naive reachability value for this one-connector-depth abstraction.

This is why the graph should store **remaining Supporter capacity in the state** rather than permanently labeling every Supporter-to-Supporter edge invalid. Magnezone's Dual Brains is one Expanded example that changes the capacity rule.

The implementation now accepts the repository's canonical `TurnActionBudget` directly. It derives remaining Supporter capacity from current usage, current limit, and the turn-ended boundary. The regression verifies exact equality with the older explicit-capacity interface for ordinary one-play state, a two-play Dual Brains state, one already-spent play under Dual Brains, and a closed turn.


## Strategic interpretation

### Rules-derived point

Reachability and same-turn playability are different properties. A path can put the required Supporter into hand while consuming the exact Supporter action required to use it.

### Computational point

In the illustrative composition, ignoring that distinction creates a 24.83 to 26.08 percentage-point same-turn access error across the opening through two additional random draws.

### Optimization implication

Adding a search card can increase a graph's connectivity score while adding zero probability of executing the intended current-turn action. An optimizer that rewards those edges without temporal typing can prefer a deck that looks more consistent and is no more capable of performing the line.

This is a concrete form of connector domination and AMR failure. The connector's cost includes action bandwidth in addition to discard costs, Bench slots, stochastic success, lock exposure, and alternative uses.

## Validation

The reported probabilities are exact; no Monte Carlo sampling is used.

The reproducer performs an independent exhaustive enumeration for a small 10-card deck over:

- every accepted opening-hand subset;
- every disjoint Prize subset;
- every disjoint future-draw subset.

Typed access, naive access, and naive-only overstatement match the closed-form category enumeration to floating-point precision. The total exact state mass is also asserted to be one.

A second regression check verifies the Supporter-capacity interpretation: with two Supporter plays remaining, the typed probability equals the one-play naive reachability probability for the illustrative one-consuming-connector-depth model.

## Limitations

This model intentionally treats each connector as a deterministic direct search for the target when a target copy remains in the deck. Real Expanded connectors differ substantially.

For example:

- Xtransceiver is coin-dependent;
- Pokégear 3.0 and Trainers' Mail sample a limited part of the deck;
- Computer Search and Secret Box have discard costs;
- Tapu Lele-GX and Jirachi-EX consume Bench space and require the correct hand-to-Bench trigger;
- Battle Compressor plus VS Seeker is a two-card, two-step path;
- Ability lock or Item lock can delete entire connector classes;
- a connector may have a strategically superior competing use.

The model also treats later cards as unbiased random draws. It does not include draw Supporters, targeted search for connectors, ordinary Prize-taking, or opponent interaction.

The numerical table is therefore a methodological stress test, not a real-deck consistency estimate.

## Next useful work

The strongest next extension is to combine the typed connector classes with `tools/timed_prize_rescue.py`. A state should distinguish direct Gladion copies, same-window Item/Ability routes, future-window Supporter routes, attack routes that cross a turn boundary, and extra Supporter-capacity effects.

After that foundation is sound, real connector effects can be added one at a time with their actual probability, zone, discard, Bench, and lock constraints.
