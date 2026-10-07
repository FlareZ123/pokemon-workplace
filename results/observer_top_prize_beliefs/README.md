# Observer-indexed Prize/top-deck swap beliefs

## Question

After an Arc Phone-style optional swap, can both players share one joint belief over the top deck and Prize positions?

No. The physical swap is public, while the information that generated it can be private.

Implementation: `tools/observer_top_prize_beliefs.py`  
Regression: `results/observer_top_prize_beliefs/reproduce.py`

## Composition of existing results

This result joins three existing pieces:

- `PrizeSlotVisibilityBelief` for legal face-down Prize targets;
- `TopPrizeJointBelief` for cross-zone correlation after a Prize/top-deck swap;
- `condition_on_optional_swap_decision()` for policy-censored information carried by the visible choice to swap or decline.

The new wrapper keeps one joint belief per observer while requiring every observer to agree on the public Prize visibility mask.

## Toy Arc Phone state

Two face-down Prize slots contain exactly A and B, with their physical order unknown.

The top card is independently X or Y with probability 1/2 each.

The actor looks at the top card privately. Their swap policy is:

- top X: swap with probability 1;
- top Y: swap with probability 1/4.

The actor observes X and performs the swap with Prize slot 0.

## Different posteriors after one public action

The actor knows the incoming card was X, so after the swap:

- selected Prize slot 0 is X with probability 1;
- the new top card is A or B with probability 1/2 each.

The opponent sees the swap but not the private top-card inspection. Bayes' rule gives:

- P(incoming X | swap) = 4/5;
- P(incoming Y | swap) = 1/5.

After propagating the same physical swap through that posterior:

- selected Prize slot 0 is X with probability 4/5;
- selected Prize slot 0 is Y with probability 1/5;
- the new top card is still A or B with probability 1/2 each.

The observers therefore agree that the swap happened and agree on the public slot geometry while assigning different identities to the selected face-down Prize slot.

## Cross-zone correlation survives observer divergence

For both observers, the unknown outgoing Prize becomes the new top card.

If the new top is A, the untouched Prize slot must be B. If the new top is B, the untouched Prize slot must be A.

The regression verifies that impossible same-identity combinations retain probability zero for both observers.

A later private observation of top A then makes the actor certain the untouched Prize is B. The opponent remains at 1/2 A and 1/2 B for that untouched slot.

## Finding

Observer-relative uncertainty can span several hidden zones at once.

A canonical simulator therefore needs to separate public physical topology and visibility from each observer's joint posterior over hidden identities. Public optional actions can transmit policy-based information, while later observations may condition only a subset of observers.

A single global hidden-zone belief would leak private information or erase information the actor actually has.

## Scope and limits

This kernel deliberately reuses the existing top-dependent swap-policy model. Real Arc Phone decisions can depend on hand, matchup, Prize knowledge, future draw value, and other state.

All observers are assumed to know the same policy probabilities. Uncertainty over the opponent's policy would require a higher-order belief.

The kernel models information and the public swap geometry. Exact physical card-class movement remains in the repository's material-state layer.

A declined swap has no selected Prize position in this model because no physical Prize/top transition occurred.

## Next work

The next useful composition step is to bind observer-indexed joint beliefs to exact hidden physical truth. One public Prize/top swap should then update exact top and Prize card classes, every observer's joint posterior, later private or public observations, and conservation across the physical zones.
