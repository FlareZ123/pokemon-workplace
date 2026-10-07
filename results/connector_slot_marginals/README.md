# One-slot marginals under connector domination

## Question

When a deck has a shared Computer Search-like connector, is one more direct out to a required channel worth more than one more disposable card that improves the connector's discard payability?

This result turns connector domination into a deck-construction comparison.

Implementation: `tools/connector_slot_marginals.py`  
Reproducer: `results/connector_slot_marginals/reproduce.py`

## Fixed-size slot substitutions

The deck size remains 60 cards.

Each experiment converts one protected non-starter filler slot into exactly one of:

- an additional target-A out;
- an additional target-B out;
- an additional currently disposable card.

The underlying state model is the exact same-window model from `results/connector_domination/`.

The main metric, **realistic joint access**, respects the one-search capacity of the universal connector and its two-card discard gate.

The comparison metric, **connector-naive gated access**, checks the discard cost but incorrectly lets the same connector satisfy every independently reachable missing channel.

## Baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup starters;
- 3 target-A outs;
- 2 target-B outs;
- 1 universal connector;
- 20 disposable non-starters;
- discard cost 2.

Baseline realistic joint access is **7.607900%**.

The connector-naive gated model reports **12.120417%**.

## One-slot marginal values

| One protected filler slot becomes | Realistic joint-access gain | Connector-naive gain | Naive / realistic |
| --- | ---: | ---: | ---: |
| +1 target-A out | +1.878295 pp | +1.500789 pp | 0.7990× |
| +1 target-B out | +2.744034 pp | +2.405112 pp | 0.8765× |
| +1 disposable card | +0.139238 pp | +0.360143 pp | 2.5865× |

The scarcest required target channel, B, has the largest direct-out marginal.

The disposable slot has much less realistic value in this state because improving payability does not increase the connector's one-card output capacity.

## Finding 1: connector-naive models can bias deck-slot valuation in opposite directions

For +1 target A, the naive model understates the realistic gain by 0.377506 percentage points.

For +1 target B, it understates the realistic gain by 0.338922 points.

For +1 disposable card, it overstates the realistic gain by 0.220905 points.

The direction flips because direct redundancy and discardability affect different failure modes.

A direct target can remove dependence on the shared connector entirely in some states. This relieves connector contention.

A disposable card can make the connector payable in more states. It cannot let the connector satisfy both missing channels.

## Finding 2: the wrong abstraction compresses the value gap

In the exact capacity-aware model:

`marginal(+1 target B) / marginal(+1 disposable) = 19.707446`

In the connector-naive gated model:

`marginal(+1 target B) / marginal(+1 disposable) = 6.678211`

The naive model still ranks the B out above the disposable card in this baseline, but it makes them look much closer than they are under the modeled capacity constraint.

An optimizer trained on the naive objective could therefore spend deck slots on discard-density improvements too aggressively and spend too few slots on direct redundancy.

## Finding 3: the weaker channel deserves more redundancy here

The starting target counts are A=3 and B=2.

Adding the fourth A out gains 1.878295 points.

Adding the third B out gains 2.744034 points.

That difference comes from joint success. When two channels are both required, additional redundancy has higher marginal value in the channel that is currently harder to satisfy.

This is a state-distribution result rather than a general rule that every lower-count card should be increased. Real card power, searchability, matchup value, and deck-building limits can reverse a purely compositional marginal.

## Relation to DCI

The extra disposable card is an intentionally simple DCI intervention. It changes one protected filler into a card that is acceptable to discard in the modeled state.

Its small marginal value does not imply that discardability is unimportant.

Earlier repository results show that discard gates can materially suppress connector AMR. The present comparison adds a second fact: once connector capacity is also modeled, increasing payability and increasing direct redundancy are not interchangeable.

The value of a DCI-improving slot depends on whether discard payability is actually the active bottleneck.

## Validation

All probabilities come from the exact multivariate-hypergeometric model in `tools/connector_domination.py`.

The reproducer asserts the baseline values and all three marginal values to floating-point precision. It also checks the realistic and connector-naive target-B/disposable marginal ratios.

No Monte Carlo sampling is used.

## Limitations

The target classes are abstract access channels.

The comparison does not model card-specific power, four-copy limits, evolution lines, Energy requirements, attacks, search routes into the targets, matchup effects, Bench constraints, locks, or multi-turn option value.

The disposable/protected split is binary and fixed for the modeled state.

The result should therefore be interpreted as a methodological warning for optimization objectives, not a recommendation to add a particular card to a real deck.

## Next useful work

The next useful extension is to map slot marginals across target counts, discard costs, and disposable-card densities.

That surface can identify regimes where the active bottleneck changes from direct target access to discard payability or connector capacity. A deck optimizer could then use the correct local marginal rather than a single global value for search connectivity or DCI.
