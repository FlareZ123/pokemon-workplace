"""Derive beginning-of-turn deck-out from canonical physical deck size."""

from __future__ import annotations

from identity_materialization import IdentityLedger
from physical_deck_projection import physical_deck_size
from post_knockout_game_resolution import Resolution, resolve_start_of_turn_deck_out


def resolve_physical_start_of_turn_deck_out(
    *,
    player_ids: tuple[str, str],
    current_turn_player: str,
    current_turn_player_ledger: IdentityLedger,
) -> Resolution:
    """Resolve the deck-out condition from complete physical deck state."""

    return resolve_start_of_turn_deck_out(
        player_ids=player_ids,
        current_turn_player=current_turn_player,
        current_turn_player_could_draw=(
            physical_deck_size(current_turn_player_ledger) > 0
        ),
    )
