# Prize slot visibility: a third information axis

## Question

If Prize composition and physical position mapping are both known exactly, is that sufficient for every Prize-position decision?

No. Face-up versus face-down eligibility is a third state dimension.

Implementation: `tools/prize_slot_visibility.py`  
Regression: `results/prize_slot_visibility/reproduce.py`

## Three separable dimensions

Recent Prize work now exposes three distinct kinds of information:

1. **composition**: which strategic groups are Prized;
2. **position**: which physical Prize slot contains each group;
3. **visibility**: which physical slots are face up versus face down.

The first two are represented by `PrizePositionBelief`. This result adds a visibility mask over that kernel.

## Minimal counterexample

Take two Prize positions with a fully known mapping:

- slot 0 contains A;
- slot 1 contains filler.

Compare two states.

### State A-up

- slot 0 is face up;
- slot 1 is face down.

### State filler-up

- slot 0 is face down;
- slot 1 is face up.

The two states have:

- identical exact Prize composition;
- identical exact physical position mapping.

They differ only in visibility.

For an effect restricted to a face-down Prize position:

- best probability of targeting A in State A-up: **0**;
- best probability of targeting A in State filler-up: **1**.

Therefore composition plus position is still not a sufficient mechanical state once face-up status matters.

## Representation

`PrizeSlotVisibilityBelief` wraps a `PrizePositionBelief` with one deterministic `face_up` flag per physical slot.

A face-up slot must have one exact grouped identity across the belief support. This encodes the information consequence of public face-up status.

The wrapper provides:

- face-up and face-down position sets;
- best success probability restricted to face-down positions;
- conditioning plus reveal of a chosen position;
- an E-35-style transition that turns all positions face down and randomizes their identity mapping.

## Reveal transition

Start from exact composition A + filler with unknown slot mapping.

If slot 0 is revealed as A:

- slot 0 becomes face up and known A;
- slot 1 remains face down;
- probability of A in an eligible face-down slot becomes 0.

If slot 0 is revealed as filler:

- slot 0 becomes known filler;
- A is forced into face-down slot 1;
- face-down A probability becomes 1.

This preserves the position-aware Bayesian conditioning from the existing kernel.

## Face-down shuffle

Starting from a known A in face-up slot 0, an E-35-style shuffle:

- turns the relevant Prize cards face down;
- randomizes the mapping;
- preserves exact total composition.

With two slots containing A + filler, the best face-down-position probability for A becomes `1/2`.

That change is invisible to a composition-only model and distinct from position information alone because the pre-shuffle A position was already known exactly.

## Relationship to the card pool

The Prize effect catalog contains wording that exercises all three dimensions:

- Town Map and similar effects create face-up status;
- Peonia can preserve deliberate physical placement without a Prize shuffle;
- Arc Phone chooses a face-down Prize position;
- Gladion explicitly shuffles the remaining Prize cards;
- E-35-style shuffling removes order information and returns cards face down.

A complete Prize action compiler therefore needs to update composition, position mapping, and visibility separately.

## Limits

This wrapper assumes face-up identity is public and exact at the grouped level.

It does not yet model observer-specific visibility differences for effects where only one player looks at a face-down card without turning it face up. Those belong in the observer-indexed layer.

It also does not yet execute a full Prize/top-deck swap or preserve the outgoing top-deck posterior. The position kernel supplies the right base representation for that next step.

## Next work

The next executable transition should compose an Arc Phone-style swap:

1. choose only a face-down slot;
2. place the known top-deck group into that slot while keeping it face down;
3. move the unknown outgoing Prize identity to the top of the deck;
4. return a posterior over the outgoing top-card identity;
5. update different observers according to whether they can infer the chosen slot and incoming card.

That transition would combine the position kernel, visibility mask, and observer-specific knowledge work directly.
