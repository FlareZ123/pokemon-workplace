# Prize/top-deck swap beliefs preserve cross-zone correlation

## Question

After an Arc Phone-style swap moves an unknown face-down Prize card to the top of the deck and a known top-deck card into that Prize slot, can the top deck and Prize zone be modeled by separate marginal beliefs?

In general, no.

Implementation: `tools/prize_top_swap_belief.py`  
Regression: `results/prize_top_swap_belief/reproduce.py`

## Minimal counterexample

Start with two face-down Prize positions containing exactly one A and one B, with their slot mapping unknown.

The acting player looks at a known top-deck card X and switches it with Prize slot 0.

Before the swap, the two possible Prize states are:

- slot 0 = A, slot 1 = B;
- slot 0 = B, slot 1 = A.

Each has probability 1/2.

After the swap, the true joint support is:

- top deck = A, Prize slots = X, B;
- top deck = B, Prize slots = X, A.

Each still has probability 1/2.

## Marginals lose a hard constraint

The separate marginals are:

- top A: 1/2;
- top B: 1/2;
- untouched Prize slot A: 1/2;
- untouched Prize slot B: 1/2.

If those marginals are treated as independent, the model invents:

- top A with Prize A;
- top B with Prize B.

Each false combination would receive probability 1/4 under an independence assumption.

Their true probability is zero.

The outgoing top card and the remaining Prize composition are perfectly anti-correlated.

## Later information uses that correlation

If a later effect reveals the new top card is A, the remaining untouched Prize slot is certainly B.

If the top card is B, the remaining Prize slot is certainly A.

`TopPrizeJointBelief.condition_top()` preserves that update exactly.

A model that had already split the zones into independent marginals could not recover the correct posterior.

## Transition

`swap_known_top_with_face_down_prize()` operates on `PrizeSlotVisibilityBelief`.

It:

1. requires the selected Prize position to be face down;
2. treats the incoming top-deck strategic group as known to the acting player;
3. replaces that Prize slot with the known incoming group;
4. moves the unknown outgoing Prize group into the joint top-deck variable;
5. preserves correlations between that outgoing identity and every untouched Prize slot.

The selected Prize slot remains face down, matching Arc Phone's text that the cards stay face down. Its identity can nevertheless be known to the acting player because that player looked at the incoming top card before the swap.

## Finding

Hidden-zone transitions can create **cross-zone correlations**.

The repository's earlier physical-state work correctly favors one canonical material truth. The same principle has an informational analogue: when one hidden card moves between zones, separate probabilistic summaries for each zone can become insufficient even if every individual marginal is correct.

Belief state therefore sometimes needs a joint distribution spanning several hidden zones.

## Relationship to existing Prize kernels

This result composes:

- `PrizePositionBelief` for physical slot uncertainty;
- `PrizeSlotVisibilityBelief` for face-down target eligibility.

It extends them with a joint top-deck variable rather than modifying either base kernel.

The Prize effect catalog identifies Arc Phone as the concrete legal wording family for this transition.

## Limits

The current transition is from the acting player's perspective.

It assumes the incoming top-deck group is already known. An opponent who did not see that top card needs a different observer-specific joint posterior.

Only one selected Prize position and one top-deck card are represented.

Physical card-instance movement remains outside this belief kernel.

The result does not model the later action required to draw or otherwise access the new top card.

## Next work

The natural extension is an observer-indexed joint swap:

- the acting player knows the incoming top card and chosen slot;
- the opponent may know the chosen physical slot while remaining uncertain about both identities;
- later public or private top-deck observations should condition each observer's joint belief differently.

That would connect the observer-specific Prize layer to cross-zone correlated hidden state.
