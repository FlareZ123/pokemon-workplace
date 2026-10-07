# Sampled unordered turn-start draw preserves physical identity

## Question

Can the same physical deck-loss boundary support a deck whose exact top card is
not represented?

Yes, if the stochastic choice is made outside the mechanics kernel and supplied
as a concrete sampled card class.

Implementation extensions:
- tools/physical_deck_projection.py
- tools/turn_start_deck_loss.py

Regression: results/sampled_turn_start_draw/reproduce.py

## Transition

draw_sampled_deck_card_to_hand consumes one exchangeable copy from the unordered
deck, materializes a new physical instance for that sampled copy, and moves that
instance to hand.

The transition checks that physical deck size falls by exactly one and that
per-class totals are conserved.

resolve_sampled_turn_start_draw applies the same beginning-of-turn physical deck
emptiness predicate used by the exact-top path. An empty deck produces no draw
transition. A nonempty unordered deck delegates to the sampled draw.

## Regression

The deck contains one A and two filler cards.

A caller samples A. The transition produces drawn-a in hand, reduces physical
deck size from 3 to 2, leaves both filler cards in the unordered deck, and
preserves card totals.

A later request to sample another A is rejected because no exchangeable A
remains in deck. An empty deck returns no turn-start draw transition.

## Finding

Randomness and physical movement can remain separate.

A policy or simulation layer chooses which exchangeable class was sampled. The
mechanics layer then materializes and moves exactly one copy while enforcing
availability and conservation.

This gives turn-start deck handling two compatible physical paths:

- exact top already materialized -> draw_exact_top_to_hand;
- unordered deck -> draw_sampled_deck_card_to_hand.

Both paths share the same physical deck-size loss predicate.

## Limits

This result does not define the probability distribution for the sampled class.
The caller must sample according to the current unordered deck composition.

It also does not model ordered multi-card deck topology. A future ordered-deck
representation should expose a corresponding draw transition without routing
through the unordered sampler.
