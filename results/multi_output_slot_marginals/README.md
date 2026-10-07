# Multi-output slot marginals: when discardability beats a direct out

## Question

The capacity-one connector scan in `results/connector_marginal_regime/` found no tested state where replacing one protected filler with a currently disposable card improved realistic joint access more than replacing it with a direct out.

Does that ordering survive when the connector can satisfy several independently missing channels at once?

No.

A Secret Box-like multi-output connector creates a regime where the marginal value of one more disposable card can exceed the marginal value of one more direct out by a large factor.

Implementation: `tools/multi_output_slot_marginals.py`  
Reproducer: `results/multi_output_slot_marginals/reproduce.py`

## Model

The calculation reuses the exact setup-conditioned same-window model in `tools/multi_channel_connector.py`.

Every state has:

- 60 cards;
- 6 Prize cards;
- an accepted 7-card opening;
- 12 protected setup starters;
- one connector;
- a protected non-starter filler slot that can be replaced;
- two outs in every required target channel;
- a binary pool of currently disposable non-starters.

The connector is Secret Box-like:

- discard cost 3;
- every target channel maps to a distinct eligible output category;
- one use can satisfy every missing modeled channel up to the connector capacity.

The fixed-size substitutions are:

- replace one protected filler with +1 direct out to one target channel;
- replace one protected filler with +1 currently disposable card.

For symmetric target counts, every direct-out marginal is equal.

## Main result at D = 20

| Required channels | Baseline joint access | +1 direct out | +1 disposable | Disposable / direct |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 6.655194% | +1.697131 pp | +0.345066 pp | 0.2033× |
| 3 | 3.420250% | +0.287842 pp | +0.344627 pp | 1.1973× |
| 4 | 2.885121% | +0.058064 pp | +0.341283 pp | 5.8777× |

With two simultaneously required channels, the direct out remains much better.

With three channels, the ordering reverses slightly.

With four channels, the extra disposable card is almost six times as valuable as one additional direct out under this objective.

This is a direct counterexample to extending the capacity-one marginal ordering to multi-output connectors.

## Crossover by channel count

For the same two-outs-per-channel composition and a cost-three connector whose capacity equals the number of channels, the first integer disposable count where +1 disposable beats +1 direct is:

| Required channels | First disposable-dominant D |
| ---: | ---: |
| 2 | none in the feasible fixed-size range |
| 3 | 17 |
| 4 | 5 |

The four-channel reversal appears shortly after the three-card discard requirement becomes realistically payable.

The three-channel reversal needs a substantially denser disposable pool.

The two-channel case never reverses before the deck runs out of a protected filler slot.

## Why the ordering reverses

A direct out affects one target channel.

A disposable card affects the probability that the connector can be paid.

For a capacity-one connector, improved payability still leaves the connector unable to repair several missing channels. That is why the earlier broad scan favored direct redundancy.

For a multi-output connector, crossing the discard gate can activate several outputs in the same action. One extra disposable card can therefore unlock simultaneous repair of two, three, or four missing channels.

The marginal value of discardability becomes multiplied by connector output capacity.

This is a concrete interaction between DCI-like discardability and connector capacity. Neither variable has a stable slot value in isolation.

## Capacity-one contrast

At the four-channel, two-outs-per-channel, D=20 state:

- cost-two, capacity-one connector joint access is 0.091320%;
- +1 direct out gains 0.040698 percentage points;
- +1 disposable gains only 0.002430 points;
- disposable/direct is 0.0597×.

For the cost-three, capacity-four connector in the same composition:

- joint access is 2.885121%;
- +1 direct out gains 0.058064 points;
- +1 disposable gains 0.341283 points;
- disposable/direct is 5.8777×.

Changing connector capacity therefore changes the local deck-slot ranking itself.

## Validation

The published 60-card values are differences of exact `multi_channel_connector_access()` probabilities.

The reproducer also performs an independent labeled-card exhaustive enumeration on a 12-card toy deck:

- 2 setup starters;
- four one-copy target channels;
- one connector;
- 2 disposable cards;
- 4-card accepted opening;
- 2 Prize cards;
- discard cost 2;
- connector capacity 4.

In that independent enumeration, the disposable marginal is exactly four times the direct-out marginal. The category model matches the labeled enumeration to floating-point precision.

No Monte Carlo sampling is used.

## Strategic implication

A deck optimizer should not assign a generic positive value to either direct redundancy or discardability.

The correct marginal depends on the connector architecture.

When a connector has one-card output capacity, direct outs can relieve shared-connector contention more effectively than extra discard fodder.

When one paid connector action can satisfy several independent categories, improving payability can become the dominant local intervention because it activates several outputs together.

For Secret Box specifically, this means a three-card discard cost cannot be evaluated separately from whether the deck has a genuine multi-category same-window package that the card can assemble.

## Limitations

The target channels remain abstract.

A Secret Box interpretation requires every modeled channel to correspond to a different eligible category among Item, Pokémon Tool, Supporter, and Stadium.

The model does not yet test whether a concrete four-card package contains redundant connectors, whether one searched card can obtain another, whether the Supporter can legally be played in the same turn, whether the Tool has a legal attachment target, or whether the Stadium and Item are tactically useful in the same state.

It also keeps discardability binary and state-static.

## Next useful work

Apply this reversal to an actual Expanded Archetype-Line-Specific package.

The strongest candidate should contain a genuine Item + Tool + Supporter + Stadium demand where the four outputs are independently useful rather than graph-redundant. That concrete audit would distinguish Secret Box's theoretical four-channel capacity from executable multi-axis value.
