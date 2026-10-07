# Materialized deck top belongs to physical deck size

## Question

When the shuffled top card is materialized as an exact deck_top instance, can deck size be read from exchangeable deck counts alone?

No.

Implementation: tools/physical_deck_projection.py
Regression: results/materialized_deck_size_projection/reproduce.py

## Representation

The repository uses deck_top as a temporary physical relation for an exact top card. The card remains part of the deck.

Canonical physical deck size is therefore:

unordered exchangeable/materialized deck cards + materialized deck_top cards.

The helper physical_deck_size performs that projection through the full IdentityLedger.

## Computer Search witness

After the atomic private Computer Search regression:

- private X has left the deck for hand;
- exact Y has been materialized as deck_top;
- two filler cards remain exchangeable in deck.

The aggregate deck zone contains 2 cards. The physical deck contains 3 because Y is still its top card.

## Exact draw

draw_exact_top_to_hand moves Y from deck_top to hand and returns to a searchable unordered-deck state.

Before the draw:

- exchangeable deck count = 2;
- physical deck size = 3.

After the draw:

- exchangeable deck count = 2;
- physical deck size = 2.

The aggregate deck count does not change because the drawn card was represented as an exact instance outside that aggregate zone. Physical deck size correctly decreases by one.

Per-class card totals remain conserved.

## Strategic consequence

Deck-out checks, remaining-deck denominators, draw probabilities, and any effect depending on deck size must include materialized top instances.

A simulator can execute the top draw correctly at the identity layer and still report an unchanged deck size if its downstream metric reads only exchangeable deck counts.

## Relation to search/shuffle

The existing search/shuffle topology deliberately collapses deck_top back into the unordered deck before a later full-deck search. This result establishes the complementary projection while the top relation is still active.

The two operations are consistent: materialized top remains a deck card until a transition destroys or consumes that relation.

## Limits

The current representation models only one exact top instance. Ordered multi-card top stacks would need an ordered deck relation rather than one deck_top marker.

## Next work

Audit deck-empty loss and draw-action layers so they consume canonical physical deck size rather than raw exchangeable counts whenever a materialized top is possible.
