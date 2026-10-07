# Private unrestricted-search targets create hidden deck-composition uncertainty

## Question

After an unrestricted search such as Computer Search, the acting player sees the full deck and privately chooses an arbitrary card to put into hand. How should a post-shuffle belief model treat the selected card for an opponent who does not see its identity?

The opponent must marginalize over the target-selection policy. Supplying one exact post-search pool count to every observer can leak private target identity.

Implementation: `tools/private_search_target_belief.py`
Regression: `results/private_search_target_belief/reproduce.py`

## New state distinction

The existing full-search belief kernel correctly models K1 and post-shuffle top/Prize correlation when the deck-plus-Prize pool is common knowledge. The revealed-target bridge correctly removes a public target from that shared pool.

Unrestricted private search has a different information geometry:

- the actor learns exact Prize composition from full deck inspection;
- the actor knows the selected arbitrary card;
- a non-acting observer sees the search action and following shuffle, but not selected-card identity;
- the card physically leaves the deck before the new top is sampled.

The opponent therefore has uncertainty over Prize state and which card was privately removed from the deck.

## Kernel

For every supported Prize state, the transition derives the remaining deck counts, applies a target-selection policy, removes each possible private target in a weighted branch, samples the new top, and marginalizes target identity out of observer-visible state.

For the actor, the wrapper first conditions on exact K1 Prize composition and then on the actor's known selected target. Other observers keep the target marginalized.

## Uniform-selection exhaustive witness

Use five labeled cards: A, B, and three fillers. One card is Prized. From the remaining four-card deck, one private target is selected uniformly, then one shuffled top is sampled uniformly from the remaining three.

An independent labeled enumeration has 5 x 4 x 3 = 60 ordered physical branches. The analytic kernel matches every collapsed `(top group, Prize group)` probability.

The opponent's top marginal is:

- P(top=A) = 1/5;
- P(top=B) = 1/5;
- P(top=filler) = 3/5.

The opponent's Prize marginal remains 1/5 A, 1/5 B, 3/5 filler because target identity was not revealed and the action occurs in every supported world.

## Actor/opponent divergence

Take the exact world where the Prize is filler and the actor privately selected A.

The actor knows A left the deck and has:

- P(top=A) = 0;
- P(top=B) = 1/3;
- P(top=filler) = 2/3.

The opponent keeps the marginalized 1/5, 1/5, 3/5 top distribution under uniform private selection.

One physical state therefore supports different post-shuffle deck beliefs for different observers solely because target identity is private.

## Strategic private policy

A second policy chooses A whenever A is in deck, otherwise B. The target remains private.

The opponent's Prize marginal stays unchanged, while the next-top marginal becomes:

- P(top=A) = 0;
- P(top=B) = 1/5;
- P(top=filler) = 4/5.

The opponent can know that the policy systematically removes A from every world where A is searchable without learning which target was chosen in this particular game.

This differs from public target signaling. No observed target conditions the Prize posterior. The hidden policy changes the transition kernel for the remaining deck.

## Architectural implication

A shared exact post-search pool is safe when removed target identity is public. It is unsafe for private target search unless an observer explicitly knows that identity.

Observer-relative hidden state needs to distinguish public target removal, private target removal known to the actor, and marginalized target removal for other observers.

The existing `TopPrizeJointBelief` can represent the resulting top/Prize marginal after private target identity has been integrated out. The missing operation was the policy-weighted transition that constructs it.

## Limits

The target policy is indexed by grouped Prize composition rather than full game state. A strategic simulator may condition target choice on hand, board, intended line, deck contents outside the modeled groups, and opponent state.

This result conditions on the search action occurring. If the decision to use Computer Search is itself hidden-state dependent, observing that public action can signal information and requires an additional action-selection policy layer.

## Next work

The physical integration should materialize the actor's exact private target in hand while checking that every observer's marginalized top/Prize belief retains support on exact material truth. A further action-policy layer can then account for information leaked merely by choosing to use the unrestricted search.
