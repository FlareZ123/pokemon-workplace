"""Bind stack-bearing board Pokemon to immutable printed card profiles.

The physical board uses Pokemon object IDs and materialized card instance IDs.
Neither is a database print ID. Consumers of printed HP, type modifiers, Prize
value, or other card-profile data therefore use an explicit current-print map.
"""

from __future__ import annotations

from typing import Mapping

from board_position_state import BoardState
from pokemon_card_profile import PokemonCardProfile


def validate_current_print_bindings(
    board: BoardState,
    current_print_id_by_pokemon_id: Mapping[str, str],
) -> None:
    board_ids = {pokemon.pokemon_id for pokemon in board.pokemon}
    if set(current_print_id_by_pokemon_id) != board_ids:
        raise ValueError("current print bindings must match the board exactly")


def current_profile(
    pokemon_id: str,
    profiles: Mapping[str, PokemonCardProfile],
    current_print_id_by_pokemon_id: Mapping[str, str],
) -> PokemonCardProfile:
    try:
        print_id = current_print_id_by_pokemon_id[pokemon_id]
    except KeyError as exc:
        raise ValueError(
            f"no current print binding for Pokemon {pokemon_id!r}"
        ) from exc
    profile = profiles.get(print_id)
    if profile is None:
        raise ValueError(f"no legal Pokemon profile for {print_id!r}")
    return profile


def hp_by_stack_board(
    board: BoardState,
    profiles: Mapping[str, PokemonCardProfile],
    current_print_id_by_pokemon_id: Mapping[str, str],
) -> dict[str, int]:
    validate_current_print_bindings(board, current_print_id_by_pokemon_id)
    return {
        pokemon.pokemon_id: current_profile(
            pokemon.pokemon_id,
            profiles,
            current_print_id_by_pokemon_id,
        ).hp
        for pokemon in board.pokemon
    }
