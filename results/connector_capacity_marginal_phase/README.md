# Effective connector-capacity marginal phase

## Question

The repository has two apparently conflicting slot-marginal results:

- capacity-one shared search strongly favors direct redundancy;
- a full four-output Secret Box-like connector can make one extra disposable
  card much more valuable than one extra direct out.

Where does the ranking change as the connector's **effective output capacity**
moves between those extremes?

This result holds the Secret Box-like discard cost at three and scans effective
capacity directly.

Implementation: `tools/connector_capacity_marginal_phase.py`  
Reproducer: `results/connector_capacity_marginal_phase/reproduce.py`

## Model slice

Every state uses:

- 60 cards;
- 6 Prize cards;
- an accepted 7-card opening;
- 12 protected setup starters;
- one connector;
- discard cost 3;
- 2 outs in every required target channel;
- at least one protected filler slot;
- a binary pool of currently disposable non-starters.

The scan considers 2, 3, and 4 simultaneously required channels.

For each channel count, effective connector capacity ranges from 1 up to the
number of required channels.

At each disposable count, the fixed-size slot comparison is:

- replace one protected filler with +1 direct out to one target channel;
- replace one protected filler with +1 currently disposable card.

Because the target channels are symmetric, every direct-out marginal is equal.

## Phase diagram

The table reports every integer disposable-card range where +1 disposable has
strictly greater exact joint-access value than +1 direct out.

| Required channels | Effective capacity | Disposable-dominant D |
| ---: | ---: | --- |
| 2 | 1 | none |
| 2 | 2 | none |
| 3 | 1 | none |
| 3 | 2 | none |
| 3 | 3 | 17-33 |
| 4 | 1 | none |
| 4 | 2 | none |
| 4 | 3 | 10-19 |
| 4 | 4 | 5-38 |

This gives a direct capacity threshold.

Two channels never enter a disposable-dominant regime in the feasible
fixed-size range.

Three channels require full effective capacity before the ranking can reverse.

Four channels reverse at capacity three, and full capacity four makes the
discardable slot dominant from D=5 through the maximum feasible D=38.

## Finding 1: partial capacity can create a bounded reversal

The capacity-three, four-channel case is especially informative.

+1 disposable wins only for D=10 through D=19.

At D=9 the disposable/direct marginal ratio is 0.925183x.

At D=10 it crosses to 1.015566x.

The ratio peaks at D=14 at 1.136860x.

At D=19 it is still 1.005423x.

At D=20 it falls back to 0.968054x, so direct redundancy regains the lead.

The reversal is therefore non-monotone in discard density.

Once the connector is already easy to pay, another disposable card loses
marginal value while another direct out still improves natural target access.

## Finding 2: full four-output capacity changes the scale

With four required channels and capacity four, +1 disposable first wins at
D=5 and remains dominant through D=38.

The disposable/direct marginal ratio peaks at D=18 at **5.951119x**.

At D=20, the already published full-capacity baseline is:

- +1 direct out: 0.058064 percentage points;
- +1 disposable: 0.341283 points;
- disposable/direct: 5.877665x.

The magnitude is qualitatively different from the narrow capacity-three band.

## Finding 3: hand-size packing explains a hard capacity boundary

The abstract model protects target cards from discard.

A payable connector-based success therefore needs at least:

`1 starter + 1 connector + discard_cost + max(0, channels - capacity)`

cards in the opening hand.

For four channels, cost three:

| Capacity | Minimum slots |
| ---: | ---: |
| 1 | 8 |
| 2 | 7 |
| 3 | 6 |
| 4 | 5 |

A capacity-one paid success cannot fit in the seven-card opening at all.

Its exact +1-disposable marginal is therefore zero throughout this slice,
apart from floating roundoff.

Capacity two only just fits the full seven-card hand, leaving very little state
mass where improved payability can matter.

Capacity three and four relax that packing constraint enough for the discard
gate to become an important local bottleneck.

## Finding 4: effective capacity matters more than printed maximum capacity

Secret Box can search one Item, one Pokémon Tool, one Supporter, and one
Stadium.

Its effective capacity for a particular line can be lower than four:

- two missing needs may occupy the same output category;
- a nominal output may be strategically redundant;
- a searched card may be unusable in the current action window;
- another required channel may not be Secret Box-eligible at all.

The phase diagram therefore says that a four-output card should not
automatically receive four-output marginal value.

The line has to expose enough independent, executable output channels.

## Relation to earlier results

`connector_marginal_regime/` and `connector_bottleneck_regimes/` describe
the capacity-one side: direct redundancy dominates improved discardability in
their tested grids.

`multi_output_slot_marginals/` supplies the full-capacity reversal.

The present result connects them by varying effective capacity while keeping
the other core composition assumptions fixed.

## Validation

All probabilities come from the exact setup-conditioned
`multi_channel_connector_access()` model with analytical Prize integration.

The reproducer:

- asserts every dominance interval;
- checks the start and end boundaries directly;
- cross-checks D=20 against the existing fixed-size marginal wrapper;
- verifies the four-channel, capacity-one eight-slot packing impossibility.

No Monte Carlo sampling is used.

## Limits

This remains an abstract same-window access model.

It does not prove that Secret Box is superior in a real deck.

The model omits:

- card-specific utility after search;
- Supporter-play contention;
- legal Tool targets;
- Stadium replacement consequences;
- Item lock and other source-scoped restrictions;
- Bench constraints;
- Energy timing;
- multi-turn option value;
- graded or matchup-dependent discardability.

The target channels also remain symmetric two-out abstractions.

## Modeling implication

Connector output capacity, discard payability, and direct redundancy form a
joint phase system.

A local deck-slot optimizer should represent effective executable capacity
rather than printed search breadth alone, then compare direct and discardability
marginals at the current state distribution.
