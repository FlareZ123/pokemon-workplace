# Physical truth and observer-relative Prize/top beliefs

## Question

Can the exact physical top-deck and Prize state be advanced together with different observer posteriors after an Arc Phone-style swap?

Yes, if physical card identity and observer uncertainty remain separate layers joined by explicit consistency checks.

Implementation: `tools/top_prize_physical_bridge.py`  
Regression: `results/top_prize_physical_bridge/reproduce.py`

## Exact physical representation

`TopPrizePhysicalState` stores:

- one materialized card instance at `deck_top`;
- one materialized instance for every physical Prize slot;
- the ordered Prize-slot instance IDs;
- the public face-up mask.

The card instances live in the existing `IdentityLedger`.

A face-down Prize/top swap changes topology by moving the same two materialized instances between `deck_top` and `prize`. No card is created or destroyed.

## Observer layer

The paired `ObserverTopPrizeBeliefs` state can give different hidden-identity probabilities to different observers while preserving the same public visibility mask.

The bridge projects exact card classes into strategic belief groups supplied by the caller. Before a transition, every observer must assign positive probability to the exact grouped physical truth.

The actor's private top-card observation is derived from the physical state rather than passed independently. This prevents a combined simulator state from claiming that the actor observed a top identity different from the real top card.

## Toy transition

Exact physical truth before the swap is:

- top = X;
- Prize slot 0 = A;
- Prize slot 1 = B.

The observers begin from the same prior:

- top X or Y with probability 1/2 each;
- Prize slots contain A and B with unknown order.

The actor privately sees X and publicly swaps with slot 0 under the policy:

- X swaps with probability 1;
- Y swaps with probability 1/4.

Exact physical truth afterward is:

- top = A;
- Prize slot 0 = X;
- Prize slot 1 = B.

The same physical instances are preserved.

The actor assigns probability 1/2 to this exact grouped post-swap state because only the outgoing A/B identity remained unknown before the swap.

The opponent assigns probability 2/5 to the same exact state. Their posterior still allows Y as the hidden incoming card because observing the optional swap only raised P(X) to 4/5.

Both beliefs include the one exact physical truth, while neither belief is used as the truth itself.

## Finding

Hidden-state simulation needs two coupled representations:

1. exact physical truth for deterministic card movement and conservation;
2. observer-relative belief over that truth for legal decision-making under hidden information.

Replacing either layer with the other causes a failure. Using physical truth as player knowledge leaks hidden identities. Using one observer posterior as physical truth makes material state probabilistic and can exclude the actual world after private observations diverge.

A bridge should therefore enforce support consistency without forcing observers to share the same probabilities.

## Additional invariant

The bridge rejects a state before mutation when any observer assigns zero probability to the exact physical truth.

This catches impossible combined states early. The observer-specific transition separately rejects a visible action if the supplied actor policy gives that action zero probability after the actor's actual private observation.

## Scope and limits

The exact topology currently materializes only the current top card and Prize cards. The rest of the deck can remain exchangeable in the identity ledger.

The strategic group mapping is supplied by the caller because useful belief groups depend on the research question.

The bridge handles the optional swap or decline boundary. It does not yet model a subsequent top-card draw, a Prize take, or a shuffle that destroys position information.

## Next work

A natural extension is a hidden-zone observation executor that consumes this combined state and handles later events such as:

- private top-deck draws;
- public top-card reveals;
- Prize takes with owner-only identity visibility;
- effects that shuffle either hidden zone.

That would let observer-relative information and exact material conservation continue together across several turns.
