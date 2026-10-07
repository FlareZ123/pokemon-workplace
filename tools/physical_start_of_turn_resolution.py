"""Bridge canonical physical deck state into beginning-of-turn game resolution."""

from __future__ import annotations

from identity_materialization import IdentityLedger
from post_knockout_game_resolution import Resolution, resolve_start_of_turn_deck_out
from turn_start_deck_loss import deck_empty_for_turn_start_loss


def resolve_physical_start_of_turn_deck_out(
    *,
    player_ids: tuple[str, str],
    current_turn_player: str,
    current_turn_player_ledger: IdentityLedger,
) -> Resolution:
    """Resolve deck-out from physical deck state instead of a caller Boolean."""

    return resolve_start_of_turn_deck_out(
        player_ids=player_ids,
        current_turn_player=current_turn_player,
        current_turn_player_could_draw=not deck_empty_for_turn_start_loss(
            current_turn_player_ledger
        ),
    )
