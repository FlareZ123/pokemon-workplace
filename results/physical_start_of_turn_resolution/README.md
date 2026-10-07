# Physical deck state now feeds the game-resolution deck-out rule

## Question

The game-resolution kernel already has a beginning-of-turn deck-out resolver,
but it accepts a caller Boolean named current_turn_player_could_draw. Can exact
physical deck state determine that input safely?

Yes.

Implementation: tools/physical_start_of_turn_resolution.py
Regression: results/physical_start_of_turn_resolution/reproduce.py

## Bridge

resolve_physical_start_of_turn_deck_out reads the current player's IdentityLedger
through the canonical physical deck-size predicate and passes the resulting
could-draw fact into the existing Outcome resolver.

This keeps responsibilities separate:

- physical representation decides whether a card physically remains in deck;
- game-resolution semantics decide whether that beginning-of-turn state is a
  loss and who wins.

## Counterexample

A one-card deck has its only card materialized as deck_top.

The raw exchangeable deck count is zero. The physical deck still contains the
exact top card.

The new bridge returns CONTINUE for both players at the beginning-of-turn loss
check. An empty IdentityLedger returns LOSS for the current-turn player and WIN
for the opponent.

This directly connects the materialized-deck projection result to the existing
rulebook-derived Outcome model.

## Finding

A Boolean game-rule input can still conceal a representation bug upstream.

The game-resolution kernel was mechanically correct given
current_turn_player_could_draw. The new adapter makes that premise auditable from
the same conserved physical state used by exact and sampled draw transitions.

## Limits

The bridge handles only the beginning-of-turn empty-deck condition. Prize and
no-Pokémon conditions keep their existing event-specific timing.

The resolver does not itself draw a card. If the game continues, callers can
use the exact-top or sampled unordered draw transitions in
tools/turn_start_deck_loss.py.
