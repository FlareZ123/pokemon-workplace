# Prize visibility partition

## Question

Is an exact or probabilistic belief over total Prize composition sufficient after cards become face up?

No. Once card text distinguishes face-up from face-down Prize positions, total composition loses mechanically relevant information.

Implementation: `tools/prize_visibility_partition.py`  
Regression: `results/prize_visibility_partition/reproduce.py`

## Counterexample

Suppose the two remaining Prize cards are exactly:

- one modeled singleton A;
- one filler card.

Consider two states with the same total composition.

### State 1

A is face up and the filler card is face down.

A face-down-only effect cannot target A.

### State 2

The filler card is face up and A is face down.

A face-down-only effect can target A with certainty.

If both states are collapsed to an ordinary composition-only `PrizeBelief`, they become identical: two total Prizes containing exactly one A.

The regression constructs both states and verifies:

- collapsed total composition is identical;
- probability A is in the face-down partition is 0 in State 1;
- probability A is in the face-down partition is 1 in State 2.

This is a direct state-aliasing failure for composition-only Prize models.

## Why the distinction appears in the card pool

The validated Prize-effect catalog contains both kinds of operation:

- effects such as Town Map and several attacks turn Prize cards face up and leave them that way;
- effects such as Arc Phone explicitly choose a **face-down** Prize card.

Visibility therefore changes future target eligibility.

A simulator that remembers only which cards are Prized can propose illegal face-down-target lines after some of those cards have become face up.

## Representation

`PrizeVisibilityBelief` stores:

- exact counts of modeled face-up groups;
- an exact count of face-up filler cards;
- a `PrizeBelief` over the remaining face-down Prize composition.

All uncertainty stays in the face-down partition.

`reveal_random_face_down_prize()`:

1. conditions the face-down belief on the observed group;
2. removes that card from the face-down distribution;
3. adds it to the exact face-up counts;
4. preserves the total number of Prize cards.

`collapse_total_composition()` intentionally forgets visibility, making the information-loss counterexample explicit.

## Partial reveal example

Start from a uniformly random two-Prize subset of:

`A, B, F1, F2, F3`.

Reveal A from one face-down position.

Afterward:

- A is exactly face up;
- one face-down Prize remains;
- A has probability 0 of being face down;
- B has probability 1/4 of being the remaining face-down Prize;
- the total Prize count remains 2.

The same Bayesian update appears in Prize taking, while the material meaning differs: reveal moves a card between visibility partitions inside the Prize zone, whereas Prize taking removes it from the Prize zone entirely.

## Full reveal

`reveal_all_face_down_prizes()` applies the same transition repeatedly until the face-down partition is empty.

At that point the observer has exact composition information and exact visibility counts.

## Finding

Prize knowledge needs at least two axes once public reveals occur:

- **composition**: which strategic groups are in the Prize zone;
- **visibility/eligibility**: which of those cards occupy face-up versus face-down positions.

Composition-only uncertainty can be exact while still being mechanically incomplete.

## Limits

The current partition tracks counts, not persistent physical position IDs.

If two face-down positions have different known histories, an exchangeable face-down belief can still be insufficient.

The model also does not yet execute Arc Phone swaps or shuffle effects. Those operations will need explicit rules for whether visibility is preserved, destroyed, or reassigned.

Observer-specific visibility beliefs can be layered on top of this partition, but this result models one observer at a time.

## Next work

The most useful next integration is a face-down Prize swap kernel.

For an Arc Phone-like transition, the model should:

- restrict selection to the face-down partition;
- replace one selected face-down Prize with a known top-deck card;
- move the outgoing Prize card to the top-deck state;
- preserve face-up Prize cards unchanged;
- update the observer's posterior when the outgoing identity remains hidden.

That would connect the visibility partition directly to the existing Prize mutation and observer-belief kernels.
