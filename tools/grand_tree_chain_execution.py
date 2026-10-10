"""Resolve both stages of Grand Tree's optional chain within one activation.

Grand Tree sv7-136 uses a once-per-player-turn Stadium effect. Its permitted
Stage 1 -> Stage 2 continuation is part of that same effect, even though the
newly evolved Stage 1 has not waited another turn.

Exact deck search, card metadata, Prize state, and shuffle remain upstream.
"""

from __future__ import annotations

from tools.board_position_state import BoardState, PokemonCard
from tools.effect_evolution_execution import effect_evolve
from tools.effect_evolution_source_gate import (
    SourceActionContext,
    SourceGatedEvolution,
    execute_source_gated_evolution,
)
from tools.effect_evolution_timing import EvolutionEffectProfile


def execute_grand_tree_chain(
    profile: EvolutionEffectProfile,
    context: SourceActionContext,
    board: BoardState,
    pokemon_id: str,
    stage1: PokemonCard,
    *,
    stage1_retreat_cost: int,
    stage2: PokemonCard | None = None,
    stage2_retreat_cost: int | None = None,
) -> SourceGatedEvolution | None:
    """Execute one Grand Tree use with optional Stage 2 follow-through.

    Source availability, the turn-one Basic ban, and entry-turn Basic ban apply
    to the first step. The optional second step is explicitly authorized in
    the same Grand Tree effect, so freshly evolving into Stage 1 does not
    prevent the Stage 2 continuation. Neither step commits partial caller
    state on a failed proposed transition.
    """

    if profile.card_id != "sv7-136":
        raise ValueError("Grand Tree chain requires the sv7-136 profile")
    if (stage2 is None) != (stage2_retreat_cost is None):
        raise ValueError("stage2 and its retreat cost must be supplied together")

    first = execute_source_gated_evolution(
        profile,
        context,
        board,
        pokemon_id,
        stage1,
        new_retreat_cost=stage1_retreat_cost,
    )
    if first is None or stage2 is None:
        return first

    assert stage2_retreat_cost is not None
    second = effect_evolve(
        first.board,
        pokemon_id,
        stage2,
        new_retreat_cost=stage2_retreat_cost,
        first_turn_policy=profile.timing_policy,
        # Grand Tree explicitly authorizes the second evolution immediately
        # after its own first evolution. Its entry-turn prohibition is about
        # evolving a newly played Basic, already checked in the first step.
        entry_turn_policy="c12_default_permitted",
        source_available=True,
    )
    if second is None:
        return None

    return SourceGatedEvolution(second.state, first.window, first.stadium_state)
