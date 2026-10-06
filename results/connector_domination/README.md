# Connector domination: one universal search cannot satisfy two missing channels

## Question

How much can a reachability model overstate same-window success when one universal search connector appears to reach two independently required resources?

The motivating case is Computer Search. The bundled Expanded card data records `bw7-137` as an ACE SPEC Item that discards two cards, then searches the deck for one card. The one-card output creates a hard capacity limit. If two independent channels are both missing, the same Computer Search cannot fill both of them.

This result formalizes the connector-domination idea from `resources/human_concepts.md` and combines it with the repository's discard-gate work.

Implementation: `tools/connector_domination.py`  
Reproducer and exhaustive validation: `results/connector_domination/reproduce.py`

## Model

The deck is partitioned into six disjoint categories:

- target A;
- target B;
- one universal connector;
- currently disposable non-starters;
- protected setup-eligible starters;
- protected non-starters.

The opening hand is conditioned on containing at least one setup-eligible starter. Six Prize cards are then sampled from the remaining deck.

The modeled objective is to have at least one target A and one target B accessible in the same action window.

The connector can search the post-Prize deck for one card. With `discard_cost=2`, its narrow cost structure matches Computer Search. Only the explicitly designated disposable cards can pay the cost. Extra copies of the targets and setup starters remain protected in this first model.

## Four access measurements

**Direct joint access** requires both target classes to be present in hand already.

**Capacity-aware no-cost access** lets the connector repair exactly one missing channel and ignores its discard cost.

**Capacity-aware gated access** is the main result. It preserves the one-search limit and also requires enough disposable cards to pay the connector.

**Naive shared-connector gated access** checks the discard cost, then treats the connector as though every individually reachable missing target can be obtained simultaneously. This is the specific connector-domination error.

A fourth comparison, **naive shared-connector no-cost access**, also ignores the discard gate.

## Illustrative baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup-eligible starters;
- 4 copies of target A;
- 2 copies of target B;
- 1 universal connector;
- 20 disposable non-starters;
- discard cost 2.

| Measurement | Probability |
| --- | ---: |
| Direct joint access | 7.023479% |
| Capacity-aware, no discard cost | 11.505118% |
| Capacity-aware, discard-gated | 9.486195% |
| Naive shared connector, discard-gated | 13.621206% |
| Naive shared connector, no discard cost | 17.346604% |

The cost-aware reachability error is therefore **4.135011 percentage points**. The discard gate separately removes **2.018923 points** from the capacity-aware ideal. Ignoring both constraints produces **7.860409 points** of overstatement relative to the modeled realistic value.

At this baseline, the fully naive value is about 82.86% larger than the capacity-aware gated value.

## Finding 1: access to each channel does not imply joint access

In 4.135011% of accepted starts, the connector is payable and both targets remain searchable, while neither target is in hand.

A graph that evaluates the channels separately can mark both as reachable:

`Computer Search -> target A`

`Computer Search -> target B`

The joint objective still fails in that state because one use of Computer Search returns only one card.

The exact capacity-overstatement term equals the probability of these payable, both-missing states.

## Finding 2: discard gating and connector capacity are separate failure modes

With 20 disposable non-starters, the connector is payable in 54.951237% of states where exactly one target is missing and the connector could otherwise repair it.

That discard gate accounts for 2.018923 percentage points of lost joint access.

A different group of states contains two missing channels. Paying the connector does not solve the capacity problem in those states. This creates the separate 4.135011-point connector-domination error.

A model that corrects discard AMR while leaving connector use unconstrained can still remain materially optimistic.

## Finding 3: better discardability exposes connector contention

The following sensitivity keeps the two targets and the one-search connector fixed while varying the binary disposable pool.

| Disposable non-starters | Capacity-aware gated | Connector-capacity overstatement | Discard-gate loss | Fully naive |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 7.848839% | 1.637180% | 3.656279% | 17.346604% |
| 15 | 8.651879% | 2.970632% | 2.853238% | 17.346604% |
| 20 | 9.486195% | 4.135011% | 2.018923% | 17.346604% |
| 25 | 10.233654% | 4.981917% | 1.271463% | 17.346604% |
| 30 | 10.819001% | 5.494658% | 0.686116% | 17.346604% |
| 35 | 11.209856% | 5.740790% | 0.295262% | 17.346604% |

As disposable density rises, the discard gate becomes less important. More both-missing states also become payable, so the connector-capacity error grows toward its no-cost ceiling.

This is useful for model design. Fixing one realism channel can make another hidden simplification become the dominant source of error.

## Relation to prior repository results

`results/discard_gated_supporter_access/` quantifies the loss from a connector's discard requirement when one target Supporter is needed.

`results/prize_rescue_discard_connector/` adds the same kind of discard gate to a turn-by-turn Prize-rescue policy.

The present result adds a second independently required target and measures the opportunity cost of sharing one connector across the two channels.

The three results together separate:

1. whether the connector can be paid;
2. whether it acts in the correct timing window;
3. whether its one use has enough capacity for all simultaneous requirements.

## Validation

The category calculation is exact and uses multivariate hypergeometric state probabilities.

The reproducer also builds an independent labeled-card test case:

- 10-card deck;
- 3-card accepted opening;
- 2 Prize cards;
- 2 setup starters;
- 2 target-A cards;
- 1 target-B card;
- 1 universal connector;
- 2 disposable cards;
- 2 protected cards;
- discard cost 1.

It exhaustively enumerates every accepted labeled opening hand and every disjoint labeled Prize set.

The exhaustive calculation matches every reported metric from the category model to floating-point precision. The setup-conditioned state mass is also asserted to equal one.

Two structural identities are checked:

- connector-capacity overstatement equals the probability mass of payable states where both channels are missing but individually searchable;
- discard-gate loss equals the one-missing connector-route mass that cannot pay the discard cost.

## Interpretation

Universal search should be represented as a scarce action resource with capacity, cost, and competing uses.

A hypergraph can still be useful, provided a connector edge carries state that records whether the connector has already been spent and how many outputs the action can actually produce.

For optimization, the important object is a feasible line or policy under shared-resource constraints. Independent reachability of each desired node is insufficient.

## Limitations

This is a deliberately narrow same-window baseline.

The model does not include:

- later natural draws;
- targeted access to the connector;
- multi-turn policies;
- graded or card-specific DCI;
- target copies becoming discardable;
- more than one connector;
- Secret Box's simultaneous multi-category output;
- Supporter contention after a target is obtained;
- lock effects;
- Bench constraints;
- ordinary Prize-taking;
- matchup-specific target value;
- sequencing where one target changes the value of the other.

Target A and target B are abstract resource classes. The baseline does not claim that four copies and two copies correspond to a universally optimal real deck.

## Next useful work

The strongest extension is a finite-horizon policy with two competing objectives.

A Computer Search-like connector could choose between a setup resource and a Gladion-like Prize-rescue Supporter. Later draws would change which target is missing, while the connector's discard cost would change with hand composition. The policy should optimize when to hold the connector and which channel to spend it on.

That would turn connector domination from a same-window feasibility correction into an explicit opportunity-cost model.
