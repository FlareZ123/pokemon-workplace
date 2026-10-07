# Beginning-of-turn deck-out must use physical deck size

## Question

Can the existing beginning-of-turn deck-out resolver safely derive draw availability from exchangeable deck counts when an exact top card is materialized?

No.

Implementation: tools/physical_start_turn_deck_out.py
Regression: results/physical_start_turn_deck_out/reproduce.py

## Rule timing

The game-loss rule checks whether the player has a card available to draw at the beginning of their turn.

The repository already represents this timing with resolve_start_of_turn_deck_out and a current_turn_player_could_draw Boolean. This result supplies that Boolean from canonical physical deck state.

## One-card counterexample

Construct a deck whose only remaining card is a materialized deck_top instance.

The exchangeable deck count is zero. The physical deck size is one.

At the beginning of the turn, the player can draw that top card, so the game continues. Deriving draw availability from raw exchangeable deck counts would report an immediate loss.

After the exact top card is drawn into hand, physical deck size becomes zero. On a later beginning-of-turn check with no card restored to deck, the player loses.

## Adapter

resolve_physical_start_of_turn_deck_out delegates terminal semantics to the existing validated game-resolution kernel and only derives could_draw from physical_deck_size.

This keeps rule timing and physical representation separate.

## Finding

The deck-top projection error can change a terminal game result, not only a probability denominator.

Any state engine that materializes top identity must make deck-out depend on physical deck membership rather than one internal storage zone.

## Limits

The adapter addresses the beginning-of-turn empty-deck condition only. Other terminal conditions remain owned by existing Prize and board-resolution kernels.

It also assumes the physical ledger reflects all effects that could restore a card to deck before the beginning-of-turn draw check.

## Next work

Audit other card-count predicates and transition guards for raw-zone access. Searchability and recovery effects are candidates when exact instances can reside in semantically equivalent subzones.
