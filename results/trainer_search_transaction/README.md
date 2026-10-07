# Trainer search transaction

## Question

Can exact search-target choice, exact discard choice, lock state, zone counts, and Supporter budget be executed as one Trainer search transition?

Yes, for the compiled Item and Supporter subset with fixed-count discard costs.

Implementation: `tools/trainer_search_transaction.py`  
Regression: `results/trainer_search_transaction/reproduce.py`

## Transaction contract

The transition verifies that the played Trainer is in hand, its play channel is open, any Supporter budget remains, any retained play condition is satisfied, the exact typed-search action belongs to the compiled profile, and the exact discard selection matches the selected branch's cost.

It then moves selected discard cards from hand to discard, moves the exact searched target classes from deck to hand, moves the played Item or Supporter from hand to discard, and verifies per-card-class conservation.

Whole-hand discard profiles and Trainer classes with different played-card destination rules are rejected explicitly.

## Regressions

Secret Box validates the four-axis Item case. A frozen discard policy protects Boss's Orders, the other three candidate cards pay the cost, all four search targets move to hand, Secret Box moves to discard, and Supporter budget remains unused. Item lock rejects the transaction.

Arven validates shared Supporter bandwidth. The first Arven searches an Item and Pokémon Tool and consumes the Supporter quota. A second Arven in the same turn is rejected even when another Arven and more searchable targets remain.

Guzma & Hala validates the conditional branch. Exact axis usage identifies that the Tool and Special Energy additions were selected, so the transaction requires the two-card optional discard, consumes the Supporter quota, retrieves all three target classes, and discards the played Supporter.

## Representation consequence

Feasibility projections and execution witnesses now stay separate:

- demand output says which strategic needs were satisfied;
- exact target cost says which deck classes were retrieved;
- scalar discard capacity says whether a cost may be payable;
- exact discard selection says which hand classes were spent;
- the transaction applies those choices to canonical zone and turn state.

This avoids treating an optimization summary as a sufficient game-state mutation.

## Limits

The current layer does not execute whole-hand discard search effects, Stadium or Pokémon Tool play as the search action, deck-order changes beyond exchangeable search counts, or later plays of retrieved cards.

A useful next extension is whole-hand discard, whose exact cost depends on the hand snapshot at the action boundary.
