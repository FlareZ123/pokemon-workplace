# Multi-window Prize rescue with clean deterministic outs

## Question

How much can deterministic same-window search improve the full multi-window Gladion rescue problem when the model preserves the real number of Gladion copies?

This result combines four layers already developed in the repository:

- valid-opening conditioning;
- exact initial Prize topology;
- random exposure across Supporter windows;
- one rescue Supporter play per modeled window.

It then adds an abstract class of clean direct non-Supporter outs that can search one real Gladion from the deck into the hand before a Supporter play.

Implementation: tools/clean_out_rescue_deadline.py

Reproducer and exact validation: results/clean_out_rescue_deadline/reproduce.py

## Clean-out semantics

A clean direct out is assumed to:

- be a non-starter;
- be playable before the current Supporter action;
- consume no Supporter window;
- search exactly one Gladion-like rescue card from the deck into the hand;
- succeed deterministically whenever a rescue copy remains in the deck;
- have no additional discard, board, lock, or opportunity cost.

These assumptions intentionally describe an idealized connector class. Concrete cards should only be mapped into it after their state-specific conditions are established.

## Sequential model

The exact process is:

1. accept an opening hand only if it contains a setup-eligible starter;
2. set Prize cards from the remaining deck;
3. condition, when requested, on at least one critical singleton being Prized;
4. expose random non-Prize cards in configured segments before each Supporter window;
5. after each segment, convert every currently usable clean out into a rescue card from the deck;
6. play only as many rescue Supporters as are required by that point to remain capable of completing all rescues by the final window.

If c critical cards are Prized and W Supporter windows remain, the minimum number of rescue plays that must have happened by window j is:

max(0, c - (W - j))

This preserves the schedule logic from the earlier timed-access model.

## Why using all clean outs immediately is safe in this abstraction

Under the clean-out assumptions, moving a rescue card from deck to hand cannot reduce future rescue availability.

The searched rescue remains available in hand until used. Removing it from the deck also means a later random draw exposes a different card instead. Since the remaining deck is modeled as uniformly random after search, there is no strategic advantage to leaving an available clean out unused.

This dominance property would stop being automatic once connector costs or target competition are added.

## Validation

The reproducer checks the implementation in two independent ways.

First, a small nine-card case is exhaustively enumerated using labeled opening sets, Prize sets, and later draw subsets. When a clean out is used, a labeled rescue card is removed from the remaining deck and placed into the hand. The exact model matches the labeled enumeration to floating-point precision.

Second, setting the number of clean outs to zero reproduces the existing result from tools/prize_rescue_deadline.py exactly. This is an important regression check because the combined model should reduce to the earlier timed-access model when targeted search is absent.

## Main baseline

Use the same baseline as the earlier deadline result:

- 60 cards;
- 6 Prize cards;
- 7-card accepted opening hand;
- 12 setup-eligible starters;
- 4 critical non-starter singletons;
- 2 real non-starter Gladion-like rescuers;
- Supporter windows at cumulative random exposure 8 / 9 / 10;
- condition on at least one modeled critical being Prized.

The probability that at least one critical is Prized is **35.383108%**.

### Clean-out sensitivity

| Clean deterministic outs | Deadline failure given a critical is Prized | Overall deadline failure |
| ---: | ---: | ---: |
| 0 | 73.622439% | 26.049907% |
| 1 | 63.069778% | 22.316047% |
| 2 | 53.916421% | 19.077305% |
| 4 | 39.179976% | 13.863093% |
| 6 | 28.305340% | 10.015309% |
| 8 | 20.395928% | 7.216713% |

The zero-out row exactly reproduces the previous timed-access baseline.

Two idealized clean outs reduce conditional deadline failure by **19.706018 percentage points** relative to random exposure alone. Four reduce it by **34.442463 points**.

These are mathematical sensitivity values, not deck-building recommendations.

## Interaction with random exposure

| Cumulative cards seen by Supporter window | 0 outs | 2 outs | 4 outs | 6 outs | 8 outs |
| --- | ---: | ---: | ---: | ---: | ---: |
| 8 / 9 / 10 | 73.622439% | 53.916421% | 39.179976% | 28.305340% | 20.395928% |
| 10 / 13 / 16 | 59.083758% | 34.949680% | 20.688845% | 12.494575% | 7.926251% |
| 12 / 18 / 24 | 42.182300% | 18.571850% | 8.856435% | 5.079236% | 3.692868% |

Targeted access and random exposure reinforce each other.

A clean out is more useful when a real rescue card remains in the deck. Random exposure can instead draw the rescue directly. The exact model handles both routes without double-counting them.

## Strategic interpretation

The result gives a cleaner decomposition of consistency.

Physical rescue copies determine Prize topology and maximum rescue capacity.

Random exposure determines how often those physical copies naturally reach the hand.

Targeted outs accelerate hand access without increasing physical rescue capacity.

That distinction matters for multi-prized collapse. Four search cards do not protect against a Prize configuration in the same way as four additional Gladion copies. They can improve access to unprized Gladion copies while leaving the underlying rescue-capacity ceiling unchanged.

This is also why a search connector should not be represented by increasing the Gladion count in a hypergeometric model.

## Connection to the typed access network

The typed access result provides the state semantics needed to decide when a concrete route can instantiate a clean-out event.

Examples:

- a direct usable Item that searches Gladion may map to one clean out;
- Quick Ball -> Tapu Lele-GX -> Wonder Tag can map to a targeted arrival only when the discard cost can be paid, the target is in deck, Bench space exists, and Abilities are active;
- Nest Ball -> Tapu Lele-GX should not map to a targeted arrival because Wonder Tag's hand-play trigger is absent;
- Skyla -> Gladion should create a future-window arrival rather than a current-window clean out;
- Battle Compressor -> VS Seeker requires a two-card typed route rather than one generic out.

The combinatorial engine and typed engine therefore solve different halves of the same problem.

## Limitations

All critical cards, rescuers, and clean outs are non-starters.

The model does not yet include:

- costs to activate a direct out;
- stochastic search;
- multi-card connector requirements;
- Bench or evolution constraints;
- Ability, Item, or Supporter locks as random or matchup states;
- Supporter contention with non-rescue Supporters;
- targeted search for the connector itself;
- ordinary Prize-taking;
- search targets other than Gladion;
- a rule for when a critical Prized card stops being urgent.

The greedy clean-out policy is exact only under the clean-out abstraction.

## Next useful work

The next integration should replace the scalar clean-out count with typed connector packages.

A practical first package model can compare:

- one direct Item;
- one Basic-search Item plus Tapu Lele-GX;
- Battle Compressor plus VS Seeker;
- one Supporter search that delays Gladion to a future window.

Each package should have its own availability predicate and consume its actual resources. That would move the model from idealized outs toward deck-specific connector realism.
