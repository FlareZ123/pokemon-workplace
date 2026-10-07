# Prize rescue through Xtransceiver coin flips

## Question

How much rescue reliability does Xtransceiver contribute when its coin flip is modeled as an actual stochastic Item action rather than a deterministic search edge?

Earlier repository work established that Xtransceiver is an Expanded-legal current-window Item route to a Supporter: it preserves the Supporter play, but only a heads result searches the deck for a Supporter. `results/prize_rescue_connector_turns/` quantified ideal deterministic preserving connectors, while `results/prize_rescue_discard_connector/` added discard payability for Computer Search-like connectors. This result adds the missing stochastic connector mechanic.

Implementation: `tools/prize_rescue_xtransceiver.py`  
Reproducer and independent exhaustive validation: `results/prize_rescue_xtransceiver/reproduce.py`

## Model

The setup and Prize sequence follows the existing exact rescue kernels:

1. draw a seven-card opening hand and condition on a valid setup-eligible starter;
2. set six Prize cards from the remaining deck;
3. begin each modeled rescue turn with one random draw;
4. allow Xtransceiver-like Item attempts before the turn's one rescue-Supporter play.

Each connector copy is a physical one-shot Item. Playing it consumes that copy. On a hit it searches one rescue Supporter from the deck into the hand. On a miss it only consumes the connector. With the default hit probability of `1/2`, this matches Xtransceiver's coin-flip gate for the narrow question of reaching the modeled rescue Supporter.

The policy is optimized exactly. After every natural draw and coin result it may use another connector, play a rescuer already in hand, or preserve remaining connectors for a later turn. Multiple Xtransceiver copies may be tried during the same turn because Item play itself does not consume the Supporter action.

The rescue card remains the repository's existing **Gladion-like abstraction**: a use recovers one modeled critical Prize and consumes one rescue Supporter from hand. Literal Gladion instead shuffles the played Gladion into the remaining Prize cards, so Gladion's own Prize-zone cycling is outside this result and is a separate modeling question.

## Baseline result

Use the same 60-card composition as the typed-connector rescue baseline:

- 12 setup-eligible starters;
- 4 modeled non-starter critical singletons;
- 2 rescue Supporters;
- 0 to 4 Xtransceiver-like connectors;
- remaining cards as other non-starters.

Condition on at least one modeled critical being initially Prized.

| Xtransceiver copies | Rescue by turn 1 | Turn 2 | Turn 3 | Turn 4 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 20.988290% | 23.799232% | 26.377561% | 28.912644% |
| 1 | 25.320925% | 28.700941% | 31.665151% | 34.550311% |
| 2 | 29.401124% | 33.315653% | 36.601162% | 39.768253% |
| 3 | 33.241428% | 37.657648% | 41.205874% | 44.594014% |
| 4 | 36.853866% | 41.740626% | 45.498586% | 49.053592% |

Four copies raise first-window rescue by **15.865576 percentage points** over the no-connector baseline and turn-4 rescue by **20.140948 points**.

## Finding 1: a coin-flip connector is materially weaker than a deterministic graph out

The same physical connector package can be evaluated with `hit_probability = 1`, which reduces to the repository's deterministic preserving-connector model.

| Copies | Turn 1, 50% hit | Turn 1, certain hit | Gap | Turn 4, 50% hit | Turn 4, certain hit | Gap |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 25.320925% | 29.653559% | 4.332634 pp | 34.550311% | 40.187978% | 5.637667 pp |
| 2 | 29.401124% | 37.309088% | 7.907964 pp | 39.768253% | 49.784411% | 10.016158 pp |
| 3 | 33.241428% | 44.055194% | 10.813766 pp | 44.594014% | 57.922303% | 13.328289 pp |
| 4 | 36.853866% | 49.984029% | 13.130163 pp | 49.053592% | 64.797247% | 15.743655 pp |

A reachability model that turns each Xtransceiver into a full deterministic Supporter out therefore gives a large optimism error. The error grows with copy count because each additional stochastic connector adds another edge whose success is being overstated.

## Finding 2: multiple copies partly recover the stochastic loss through same-turn retries

Xtransceiver is an Item, so a failed first copy does not mechanically end the attempt. A second copy can be played immediately if one is in hand and a rescue Supporter remains searchable.

To isolate this bandwidth, the model includes a counterfactual that allows at most one connector attempt per turn.

| Copies | Turn 1 with retries | Turn 1 one-attempt counterfactual | Retry value | Turn 4 retry value |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 25.320925% | 25.320925% | 0.000000 pp | 0.000000 pp |
| 2 | 29.401124% | 29.148689% | 0.252435 pp | 0.001095 pp |
| 3 | 33.241428% | 32.521742% | 0.719686 pp | 0.003517 pp |
| 4 | 36.853866% | 35.486160% | 1.367707 pp | 0.007652 pp |

The immediate-window effect is visible because a second Item attempt can repair a tails result before the same Supporter deadline expires. By turn 4 the difference is tiny in this isolated model: unused copies can usually be attempted on later turns, and later natural draws reveal whether a connector is still needed.

This is a useful temporal distinction. The same collection of physical outs has different value when the objective expires now versus when several future action windows remain.

## Finding 3: connector quantity and connector reliability are separate state dimensions

Four 50% connectors reach 36.853866% first-window success, below the 49.984029% of four certain-hit connectors. Their value also does not collapse to the probability of at least one heads, because access depends on whether a connector is actually in hand, whether a rescuer remains in the searchable deck, whether a rescuer was drawn directly, how many critical Prizes still require recovery, and whether the policy should preserve a connector for later information.

A stochastic connector should therefore remain an action with a probability branch inside the state transition. Replacing it with a fractional card count or a deterministic edge loses timing, physical-copy, and information effects.

## Validation

The reported values are exact; no Monte Carlo sampling is used.

The reproducer validates three independent properties:

- setting the connector hit probability to one with four copies reproduces the published deterministic preserving-connector results for turns 1 through 4;
- a labeled 10-card deck is exhaustively enumerated over every accepted opening hand, disjoint Prize set, future natural draw, connector choice, and coin branch; its conditional success `89.567175%` matches the category dynamic program to floating-point precision;
- the same labeled regression also matches when same-turn retrying is disabled, independently checking that the retry transition is represented correctly.

The exact setup-conditioned state mass is asserted to be one.

## Strategic interpretation

This result isolates stochastic AMR. Xtransceiver has favorable timing because it is an Item and leaves the Supporter window available, while its coin flip can still erase a large share of nominal graph value. Extra copies provide both redundancy across turns and some immediate retry bandwidth.

That makes Xtransceiver qualitatively different from both a deterministic preserving connector such as an idealized any-card Item and a Supporter-consuming connector that cannot enable same-window rescue. Connector models should preserve action class and stochastic resolution separately.

## Limitations

This remains a deliberately narrow exact baseline. It excludes Item lock, connector search, other Supporter targets, competing uses of Items, draw Supporters and Abilities, ordinary Prize-taking, alternative Prize recovery, matchup-dependent criticality, and opponent interaction. It also assumes the coin has the modeled fixed probability and that any successful search chooses the needed rescue Supporter when one remains in the deck.

Most importantly, it inherits the existing Gladion-like rescue abstraction. Literal Gladion enters the remaining Prize cards after use. Modeling that zone transition could change multi-rescue topology and is a high-value next extension.

## Next useful work

The clearest correctness extension is a literal Gladion state kernel that preserves the Supporter's own zone transition into the Prize cards. It should distinguish initially critical Prize cards from rescue Supporters that later enter the Prize zone, permit later Gladion uses to select a Prized Gladion when strategically useful, and compare the resulting timed recovery ceiling against the consumed-rescuer abstraction used by the current rescue models.
