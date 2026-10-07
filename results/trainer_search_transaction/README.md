# Trainer search transaction

## Question

Can exact search-target choice, exact discard choice, lock state, zone counts, and Supporter budget be executed as one Trainer search transition?

Yes, for the compiled Item and Supporter subset, including fixed-count and whole-hand discard costs.

Implementation: `tools/trainer_search_transaction.py`  
Regression: `results/trainer_search_transaction/reproduce.py`

## Transaction contract

The transition verifies that the played Trainer is in hand, its play channel is open, any Supporter budget remains, any retained play condition is satisfied, the exact typed-search action belongs to the compiled profile, and the exact discard selection matches the selected branch's cost.

The played Trainer first leaves hand for a temporary resolving zone. Its instructions then operate on the remaining hand. Fixed-count costs use an exact discard selection; whole-hand costs derive their discarded classes from that resolving hand snapshot. Search targets move from deck to hand, then the played Item or Supporter moves from the resolving zone to discard. Per-card-class totals remain conserved.

This temporary zone matters when another copy of the same Trainer remains in hand: the resolving copy is not available to pay its own "other cards" cost, while a second copy can be. Trainer classes with different played-card destination rules remain outside the current scope.

## Regressions

Secret Box validates the four-axis Item case. A frozen discard policy protects Boss's Orders, the other three candidate cards pay the cost, all four search targets move to hand, Secret Box moves to discard, and Supporter budget remains unused. Item lock rejects the transaction.

Arven validates shared Supporter bandwidth. Under the ordinary quota of one, the first Arven consumes the Supporter quota and a second same-turn Arven is rejected. With a Supporter limit of two, the same two-Arven sequence succeeds, matching the quota-based turn-budget abstraction needed for Expanded effects such as Dual Brains.

Guzma & Hala validates the conditional branch. Exact axis usage identifies that the Tool and Special Energy additions were selected, so the transaction requires the two-card optional discard, consumes the Supporter quota, retrieves all three target classes, and discards the played Supporter. A second Guzma & Hala copy in hand can legally be one of those discarded cards while the first copy occupies the resolving zone.

Larry's Skill validates whole-hand sequencing. The resolving Supporter leaves the hand first, every remaining hand card moves to discard, and only then do the selected Pokémon, Supporter, and Basic Energy targets enter the hand.

## Representation consequence

Feasibility projections and execution witnesses now stay separate:

- demand output says which strategic needs were satisfied;
- exact target cost says which deck classes were retrieved;
- scalar discard capacity says whether a cost may be payable;
- exact discard selection says which hand classes were spent;
- the transaction applies those choices to canonical zone and turn state.

This avoids treating an optimization summary as a sufficient game-state mutation.

## Limits

The current layer does not execute Stadium or Pokémon Tool play as the search action, deck-order changes beyond exchangeable search counts, or later plays of retrieved cards.

A useful next extension is sequencing the retrieved cards into later actions while preserving their exact identities and remaining action budgets.
