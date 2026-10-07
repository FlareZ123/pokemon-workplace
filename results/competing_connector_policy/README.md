# Competing connector policy: finite-horizon allocation between rescue and setup

## Question

When one discard-gated universal connector can solve either of two important channels, how much value comes from deciding which channel to search only after seeing the current state?

The motivating abstraction is one Computer Search-like connector shared between:

- a Gladion-like Prize-rescue Supporter channel; and
- one separate setup target that must reach hand by the same deadline.

This extends three existing repository results:

- `results/connector_domination/` shows that one universal one-card search cannot satisfy two simultaneously missing channels at once;
- `results/prize_rescue_discard_connector/` gives a finite-horizon rescue policy with a discard-gated preserving connector whose only modeled target is the rescue Supporter;
- `results/connector_option_value/` motivates preserving a connector until later information makes its best use clearer.

Implementation: `tools/competing_connector_policy.py`  
Reproducer and independent labeled-card validation: `results/competing_connector_policy/reproduce.py`

## Model

The opening hand is conditioned on containing at least one setup-eligible starter. Six Prize cards are then sampled from the remaining deck.

The modeled deck contains:

- critical non-starter cards that may be initially Prized;
- rescue Supporters;
- copies of one separate setup target;
- exactly one universal connector;
- currently disposable non-starters;
- protected setup starters;
- protected non-starters.

Each modeled turn begins with one random draw and has one ordinary Supporter play.

Success requires both of these conditions by the horizon:

1. every initially Prized modeled critical card has been rescued;
2. at least one setup target has reached hand.

The connector preserves the Supporter play. When it is in hand and its discard cost can be paid, it can search for one card from one allowed channel. It can also be held for a later turn.

This is an exact category-state dynamic program. It optimizes actions after every natural draw.

## Four policies

The result compares four policies while keeping the same deck slots fixed.

- **No connector**: the connector is present but unusable for either target.
- **Rescue-only**: it may search only rescue Supporters.
- **Setup-only**: it may search only the setup target.
- **Flexible**: it may search either target, and the policy chooses the better action in each state.

Every searchable policy may wait. The comparison therefore measures target-allocation flexibility rather than an eager-use heuristic.

## Baseline

Use:

- 60 cards;
- 6 Prize cards;
- valid 7-card opening;
- 12 protected setup starters;
- 4 critical non-starters;
- 2 rescue Supporters;
- 2 setup-target copies;
- 1 universal connector;
- 20 disposable non-starters;
- discard cost 2.

Condition on at least one modeled critical card being initially Prized.

| Horizon | No connector | Rescue-only | Setup-only | Flexible | Flexible gain over best single-purpose |
| ---: | ---: | ---: | ---: | ---: | ---: |
| Turn 1 | 4.523828% | 5.818968% | 5.818968% | 7.114108% | 1.295140 pp |
| Turn 2 | 5.862171% | 7.779168% | 7.736094% | 9.642679% | 1.863511 pp |
| Turn 3 | 7.297798% | 9.848039% | 9.776292% | 12.303622% | 2.455583 pp |
| Turn 4 | 8.857541% | 12.058535% | 11.950575% | 15.114299% | 3.055764 pp |

The flexible policy does not receive extra connector capacity. It still gets one search from one connector. Its advantage comes only from allocating that search after observing which resources arrived naturally and whether the discard gate is currently payable.

## Finding 1: a universal connector has state-contingent allocation value

At the three-turn baseline, locking the connector permanently to rescue gives 9.848039% joint success. Locking it permanently to setup gives 9.776292%.

Allowing the same single connector to choose its target by state raises success to 12.303622%.

The **2.455583 percentage-point gain** is a direct finite-horizon measure of connector option value across competing uses.

This is a different failure mode from the original connector-domination result. There, an optimistic graph illegally spends one connector twice in the same state. Here, the connector is spent at most once. The question is whether the policy commits its future use in advance or retains the right to allocate it after more information arrives.

## Finding 2: discardability controls how much target flexibility can matter

Three-turn sensitivity with the same two rescue Supporters and two setup targets:

| Disposable non-starters | No connector | Rescue-only | Setup-only | Flexible | Flexible gain |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 7.297798% | 7.696984% | 7.687515% | 8.083379% | 0.386394 pp |
| 10 | 7.297798% | 8.549070% | 8.517458% | 9.758032% | 1.208961 pp |
| 15 | 7.297798% | 9.323168% | 9.268945% | 11.276539% | 1.953371 pp |
| 20 | 7.297798% | 9.848039% | 9.776292% | 12.303622% | 2.455583 pp |
| 25 | 7.297798% | 10.134103% | 10.051217% | 12.861559% | 2.727456 pp |
| 30 | 7.297798% | 10.258155% | 10.169490% | 13.102401% | 2.844246 pp |

When the discard gate is hard to pay, connector target flexibility is mostly latent. As discardable-card density rises, more states can actually exercise the choice, so the value of flexible allocation increases.

This links DCI directly to connector opportunity cost. A connector can be broad in text while still having little practical allocation value when the hand cannot pay for it.

## Finding 3: the preferred dedicated target flips with surrounding density

Keep the three-turn horizon, two rescue Supporters, twenty disposable non-starters, and cost two. Vary only setup-target copies:

| Setup-target copies | Rescue-only | Setup-only | Flexible |
| ---: | ---: | ---: | ---: |
| 1 | 5.267896% | 6.456355% | 7.799298% |
| 2 | 9.848039% | 9.776292% | 12.303622% |
| 3 | 13.818214% | 12.414610% | 15.975838% |
| 4 | 17.248824% | 14.662568% | 19.122464% |

With one setup copy, dedicating the connector to setup is better than dedicating it to rescue.

With three or four setup copies, natural setup access is common enough that dedicating the connector to rescue is better.

A static rule such as "the universal search should be reserved for rescue" or "the universal search should be reserved for setup" therefore loses value across deck compositions. The correct allocation depends on the remaining outs and the current hand state.

## Validation

The category dynamic program is exact and uses no Monte Carlo sampling.

The reproducer independently implements a labeled-card recursion for:

- 10 cards;
- 3-card accepted opening;
- 2 Prize cards;
- 3 setup starters;
- 2 critical non-starters;
- 1 rescue Supporter;
- 1 setup target;
- 1 connector;
- 2 disposable cards;
- discard cost 1;
- 2 turns.

It exhaustively enumerates every accepted labeled opening hand, every disjoint Prize set, every future natural draw, and every legal modeled action.

The category and labeled models agree to floating-point precision on:

- `P(any critical initially Prized | valid start) = 40.44817927170866%`;
- no-connector success = `21.024930747922474%`;
- rescue-only success = `28.559556786703644%`;
- setup-only success = `28.559556786703644%`;
- flexible success = `34.98614958448758%`.

The reproducer also asserts total setup-conditioned state mass equals one and that the flexible policy cannot underperform either single-purpose subset policy.

## Interpretation

A universal connector should be represented as a scarce option over future state-contingent actions.

Its strategic value depends on at least:

- whether it can be paid now;
- which targets remain naturally accessible;
- which targets are already in hand;
- which targets are Prized;
- how many action windows remain;
- whether using the connector on one channel leaves the other channel solvable by natural draws.

This strengthens the repository's broader conclusion that typed access edges are insufficient without shared-resource state and policy timing.

## Limitations

This is still an abstract baseline.

It does not model:

- ordinary Prize-taking;
- search access to the connector itself;
- graded or card-specific DCI;
- state-dependent changes in which cards are disposable;
- competing non-rescue Supporters;
- different deadlines for setup and rescue;
- lock effects;
- Bench constraints;
- Energy attachment requirements;
- matchup-dependent target value;
- Secret Box's simultaneous multi-category output;
- a real deck where the setup target has card-specific play conditions.

The setup target is modeled only as a card that must reach hand. The result should not be read as a full-match win-rate estimate.

## Next useful work

The strongest next extension is to separate the two deadlines.

A setup target such as an attacker, Energy enabler, or lock piece can be urgent on turn 1 or turn 2 while a Prized singleton may only need rescue by a later turn. Giving those objectives distinct deadlines would measure when the connector should rationally spend early on setup even when rescue remains important.

A second extension is a real-deck instantiation where the competing setup channel is taken from an Expanded list and the connector's legal target, discard gate, and downstream play requirements are compiled from card text rather than represented as an abstract hand-acquisition flag.
