"""Resolve a narrow, causal Garbotoxin Ability-suppression overlay.

This module models only the verified Garbotoxin / Stealthy Hood / Jamming Tower
interaction needed by current canonical quota research. It returns suppressed
object IDs instead of mutating base board truth, so the overlay can be removed
and recomputed when the lock state changes.
"""

from __future__ import annotations

from board_object_kernel import BoardPokemon, BoardState


GARBOTOXIN_PRINT_IDS = frozenset(
    {"bw6-54", "bw9-119", "bw11-68", "xy9-57"}
)
STEALTHY_HOOD = "Stealthy Hood"
JAMMING_TOWER = "Jamming Tower"


def garbotoxin_source_active(pokemon: BoardPokemon) -> bool:
    """Return whether this exact source currently satisfies Garbotoxin."""

    return (
        pokemon.print_id in GARBOTOXIN_PRINT_IDS
        and pokemon.abilities_enabled
        and pokemon.tool is not None
    )


def stealthy_hood_protects_from_opponent(
    pokemon: BoardPokemon,
    *,
    stadium_name: str | None = None,
) -> bool:
    """Return whether Hood's opponent-Ability protection is currently live."""

    return (
        pokemon.tool is not None
        and pokemon.tool.card_name == STEALTHY_HOOD
        and pokemon.pokemon_state.tool_effect_enabled
        and stadium_name != JAMMING_TOWER
    )


def garbotoxin_suppressed_object_ids(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None = None,
) -> frozenset[str]:
    """Return this player's in-play Pokemon suppressed by active Garbotoxin.

    A Garbotoxin source on the player's own board suppresses their other
    Abilities regardless of Stealthy Hood, whose protection is only from the
    opponent's Abilities. An opposing source is blocked for a Hood holder while
    the Tool effect is live. Garbotoxin itself is exempt from Garbotoxin.
    """

    own_lock = any(garbotoxin_source_active(row) for row in player_board.objects)
    opposing_lock = any(
        garbotoxin_source_active(row) for row in opponent_board.objects
    )

    suppressed: set[str] = set()
    for pokemon in player_board.objects:
        if pokemon.print_id in GARBOTOXIN_PRINT_IDS:
            continue
        if own_lock:
            suppressed.add(pokemon.object_id)
            continue
        if (
            opposing_lock
            and not stealthy_hood_protects_from_opponent(
                pokemon,
                stadium_name=stadium_name,
            )
        ):
            suppressed.add(pokemon.object_id)
    return frozenset(suppressed)
