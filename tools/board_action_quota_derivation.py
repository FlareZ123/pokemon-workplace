"""Derive live action quotas from canonical physical board state.

The first supported physical quota source is Magnezone bw8-46 / Dual Brains.
Exact print identity and effective-Ability state are read from BoardPokemon.
"""

from __future__ import annotations

from dataclasses import replace

from action_quota_effects import ActionQuotaGrant, DUAL_BRAINS, derive_action_quotas
from board_object_kernel import BoardPokemon, BoardState
from canonical_turn_budget_owner import (
    CanonicalCompositeTurnState,
    with_canonical_budget,
)
from turn_action_budget import TurnActionBudget


DUAL_BRAINS_PRINT_ID = "bw8-46"


def set_board_pokemon_abilities_enabled(
    board: BoardState,
    object_id: str,
    enabled: bool,
) -> BoardState:
    """Set effective Ability activity for one physical in-play Pokemon."""

    board.get(object_id)
    objects = tuple(
        replace(pokemon, abilities_enabled=enabled)
        if pokemon.object_id == object_id
        else pokemon
        for pokemon in board.objects
    )
    next_board = replace(board, objects=objects)
    next_board.validate()
    return next_board


def quota_grants_from_board(board: BoardState) -> tuple[ActionQuotaGrant, ...]:
    """Compile currently active quota grants from exact in-play objects."""

    grants: list[ActionQuotaGrant] = []
    for pokemon in board.objects:
        if (
            pokemon.print_id == DUAL_BRAINS_PRINT_ID
            and pokemon.abilities_enabled
        ):
            grants.append(
                ActionQuotaGrant(
                    source=f"{DUAL_BRAINS.source} / object {pokemon.object_id}",
                    action=DUAL_BRAINS.action,
                    limit=DUAL_BRAINS.limit,
                )
            )
    return tuple(grants)


def derive_board_action_quotas(
    board: BoardState,
    budget: TurnActionBudget,
) -> TurnActionBudget:
    """Recompute current action limits from the current physical board."""

    return derive_action_quotas(budget, quota_grants_from_board(board))


def refresh_canonical_action_quotas(
    state: CanonicalCompositeTurnState,
) -> CanonicalCompositeTurnState:
    """Recompute canonical quota limits from the state's current board."""

    budget = derive_board_action_quotas(state.board, state.budget)
    return with_canonical_budget(state, budget)
