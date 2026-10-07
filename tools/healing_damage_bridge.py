"""Apply compiled healing profiles to the damage-capable board-object state."""

from __future__ import annotations

from dataclasses import replace

from board_object_kernel import BoardPokemon, BoardState
from healing_profile_compiler import HealingProfile, HealingTarget


def _replace_object(board: BoardState, pokemon: BoardPokemon) -> BoardState:
    next_board = replace(
        board,
        objects=tuple(
            pokemon if row.object_id == pokemon.object_id else row
            for row in board.objects
        ),
    )
    next_board.validate()
    return next_board


def apply_healing_to_object_board(
    profile: HealingProfile,
    board: BoardState,
    *,
    source_object_id: str | None = None,
    selected_object_id: str | None = None,
) -> BoardState | None:
    """Apply one compiled heal to the board used by damage/KO kernels."""

    if profile.target == HealingTarget.SOURCE_POKEMON:
        if source_object_id is None or selected_object_id is not None:
            raise ValueError("source healing requires exactly source_object_id")
        target_id = source_object_id
    else:
        if selected_object_id is None or source_object_id is not None:
            raise ValueError("selected healing requires exactly selected_object_id")
        target_id = selected_object_id

    try:
        pokemon = board.get(target_id)
    except KeyError:
        return None

    if profile.source_kind == "trainer" and pokemon.damage_counters == 0:
        return None

    healed_counters = profile.heal_damage // 10
    next_damage = max(0, pokemon.damage_counters - healed_counters)
    if next_damage == pokemon.damage_counters:
        return board
    return _replace_object(
        board,
        replace(pokemon, damage_counters=next_damage),
    )
