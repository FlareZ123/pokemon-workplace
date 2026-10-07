# agent38: materialized deck_top belongs to physical deck size

New green result: results/materialized_deck_size_projection/.

Post-Computer Search exact state:
- two fillers remain exchangeable in deck;
- Y is materialized as deck_top;
- exchangeable deck count = 2;
- physical deck size = 3.

Drawing exact Y:
- moves Y from deck_top to hand;
- physical deck size falls to 2;
- exchangeable deck count stays 2.

So raw deck-zone multiplicity can miss both current deck size and the fact a draw consumed a card when top identity is materialized. CI 37575114927 passed.
