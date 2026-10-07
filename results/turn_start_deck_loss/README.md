# Turn-start deck loss must use physical deck size

## Question

If the unordered exchangeable deck count is zero but one exact materialized
deck-top card remains, has the player already run out of cards to draw at the
beginning of the turn?

No.

The Advanced Player's Rulebook lists a loss condition when the player has no
cards left in the deck to draw at the beginning of their turn. The repository's
deck-top representation keeps an exact top card materialized outside the
exchangeable deck count while that card still physically belongs to the deck.

Implementation: tools/turn_start_deck_loss.py
Regression: results/turn_start_deck_loss/reproduce.py

## Counterexample

The regression starts from a one-card deck containing Y.

Y is materialized as the exact deck top. At that point:

- raw exchangeable deck count = 0;
- canonical physical deck size = 1;
- turn-start deck-loss predicate = false.

The exact turn-start draw then moves Y to hand. Physical deck size becomes zero.
That does not retroactively invalidate the draw that just happened. It means the
deck is empty for a later beginning-of-turn check unless some intervening effect
returns cards to the deck.

An exchangeable-count-only loss check would therefore lose the game one turn
window too early in this represented state.

## Finding

Deck-out is a physical-zone predicate with timing.

The correct represented check is:

physical unordered deck cards + materialized deck-top cards == 0

The exact top relation changes how the card is represented, while leaving it in
the deck until the draw consumes that relation.

## Architectural consequence

Any match-level beginning-of-turn resolver should use canonical physical deck
size rather than raw exchangeable counts. The same projection should feed draw
availability and any denominator that depends on cards remaining in deck.

The result reuses the existing exact-top draw transition, so the top instance
moves to hand and per-class card totals remain conserved.

## Limits

This result covers an exact materialized top card. A fully unordered deck still
needs a stochastic or sampled draw transition to materialize the drawn copy.

The module exposes the physical emptiness predicate separately so a future
match-level turn engine can use the same loss check for either exact-top or
unordered-deck draw paths.
