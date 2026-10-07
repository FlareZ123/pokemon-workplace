# Deadline-sensitive connector capacity slack

## Question

`connector_capacity_option_value/` shows that a bounded-capacity search can be worth preserving when natural draws may resolve some missing channels before the search is spent.

What happens when one target channel expires earlier than the others?

This result gives each missing channel its own draw deadline. It shows that a single immediate requirement can force a multi-output connector to commit before useful target-choice information arrives, erasing the adaptive value of waiting even though the connector's card-text capacity is unchanged.

Implementation: `tools/connector_capacity_deadlines.py`  
Independent regression: `results/connector_capacity_deadlines/reproduce.py`

## Deadline semantics

A deadline is the number of natural draws that may still occur before a target must be secured.

- deadline `0`: the target must be secured at the current action point before another natural draw;
- deadline `1`: one natural draw may occur, after which the target must be secured before any further draw;
- larger values extend the same rule.

The policy has one connector already in hand. One use can search one copy from each of up to `k` distinct missing target channels. At each action point it may use the connector or preserve it and draw, provided no unsecured deadline is already zero.

Search and natural draws remove physical target copies from the remaining deck. The objective is exact access: every target must be secured before its own deadline.

## Clean symmetric family

Consider the same family used in `connector_capacity_option_value/`:

- `m = k + 1` missing target channels;
- two copies of every target channel;
- 40 cards remaining in deck;
- one connector of capacity `k`;
- no payment gate.

When every channel has the full future horizon, the optimal policy can preserve the connector and let natural draws reveal which channels should consume its finite capacity.

Now give exactly one missing channel deadline `0` while the others retain the full horizon.

The urgent channel must be included in the connector's current output. In the symmetric family, optimal play then fills the remaining `k - 1` outputs immediately, leaving one unresolved channel for future natural draws. The policy has lost its ability to wait before deciding which channel to leave unresolved.

For this family, the urgent-deadline value equals the earlier eager-use value exactly.

## One-draw result

| Missing channels `m` | Capacity `k` | All channels allow 1 draw | One channel due now | Value destroyed by urgency |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1 | 10.000000% | 5.128205% | **4.871795 pp** |
| 3 | 2 | 15.000000% | 5.263158% | **9.736842 pp** |
| 4 | 3 | 20.000000% | 5.405405% | **14.594595 pp** |
| 5 | 4 | 25.000000% | 5.555556% | **19.444444 pp** |

One early requirement removes the entire waiting gain from the corresponding one-draw capacity-slack state.

The effect grows with the amount of target-choice flexibility that was available before the deadline was imposed.

## Longer horizons

The same pattern persists with more future draws. The table below compares a common relaxed deadline with one channel due immediately while all other channels retain the horizon.

| `m / k` | Horizon | Relaxed deadlines | One urgent channel | Urgency loss |
| --- | ---: | ---: | ---: | ---: |
| 2 / 1 | 1 | 10.0000% | 5.1282% | 4.8718 pp |
| 2 / 1 | 4 | 35.5455% | 19.7031% | 15.8424 pp |
| 3 / 2 | 1 | 15.0000% | 5.2632% | 9.7368 pp |
| 3 / 2 | 4 | 49.2548% | 20.1991% | 29.0557 pp |
| 4 / 3 | 1 | 20.0000% | 5.4054% | 14.5946 pp |
| 4 / 3 | 4 | 60.6522% | 20.7207% | 39.9314 pp |
| 5 / 4 | 1 | 25.0000% | 5.5556% | 19.4444 pp |
| 5 / 4 | 4 | 70.0131% | 21.2698% | **48.7433 pp** |

For the five-channel, capacity-four state, giving one channel an immediate deadline cuts four-draw success from 70.0131% to 21.2698%.

Nothing about the connector's search text, output capacity, or target counts changed. Only one target's timing changed.

## Too many immediate demands create a hard feasibility cutoff

If more unsecured deadline-zero channels exist than the connector can satisfy immediately, the state is impossible under this one-connector model.

For example, three channels all due now with a capacity-two connector have success probability exactly zero, regardless of how many future draws remain. Those draws occur after the unmet deadlines.

This is a temporal analogue of connector output contention: future access does not rescue a channel after its strategic window has closed.

## Relation to prior work

This result composes two earlier agent5 threads:

- `connector_capacity_option_value/`: finite output capacity creates target-choice option value when the connector can be preserved;
- `competing_connector_deadlines/`: earlier target deadlines shrink the value of flexible allocation for a capacity-one universal connector.

The combined state variable is **capacity relative to the demand that expires before more information arrives**.

A planner that records only total connector capacity can overvalue future flexibility. A planner that records only deadlines can miss that one multi-axis action may cover several urgent channels at once.

## Validation

The implementation is an exact memoized dynamic program over:

- target-copy counts;
- secured channels;
- per-channel deadlines;
- connector availability;
- remaining natural draws;
- filler count.

The reproducer independently enumerates labeled physical-card game trees. It checks:

1. every one-draw symmetric row against the prior option-value solver;
2. relaxed deadlines against the prior optimal policy;
3. one urgent channel against the prior eager policy;
4. a separate four-channel, three-draw state;
5. the hard cutoff when immediate demand exceeds capacity.

All regressions match to floating-point precision. No Monte Carlo sampling is used.

## Limits

The connector is already in hand and has no payment cost or competing use in this isolated model. Target channels are abstract. A concrete Secret Box interpretation would require distinct eligible Trainer categories, exact discard witnesses, Supporter timing, Tool and Stadium legality, and downstream line deadlines.

The current deadline means "must be secured" rather than "must be played, attached, evolved, or otherwise executed." Concrete ALS work needs downstream action timing as well as card access timing.

## Next useful work

A strong concrete application is the Aichi Vileplume Secret Box line. Its searched outputs have unequal timing roles: some are direct first-turn payloads, some are upstream connectors, and Grand Tree's competing value appears on later turns. A continuation-aware model can use the deadline-capacity representation to distinguish same-turn required outputs from resources whose value survives into later windows.
