"""Bind Grand Tree's one-activation evolution chain to physical card zones."""

from __future__ import annotations

from dataclasses import dataclass

from tools.board_position_state import BoardState, PokemonCard
from tools.effect_evolution_source_gate import SourceActionContext, SourceGatedEvolution
from tools.effect_evolution_timing import EvolutionEffectProfile
from tools.grand_tree_chain_execution import execute_grand_tree_chain
from tools.identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
    validate_board_position_stack_bindings,
)


@dataclass(frozen=True)
class MaterializedGrandTreeChain:
    evolution: SourceGatedEvolution
    ledger: IdentityLedger


def materialized_grand_tree_chain(
    profile: EvolutionEffectProfile,
    context: SourceActionContext,
    ledger: IdentityLedger,
    board: BoardState,
    pokemon_id: str,
    stage1: PokemonCard,
    *,
    stage1_class: str,
    stage1_retreat_cost: int,
    stage2: PokemonCard | None = None,
    stage2_class: str | None = None,
    stage2_retreat_cost: int | None = None,
) -> MaterializedGrandTreeChain | None:
    """Search Stage 1 then optionally Stage 2 from deck, preserving identity.

    The two conditional picks represent the outcomes of Grand Tree's two
    searches. The card-class inventory, provided by the caller, determines
    whether an eligible selected card is actually available in the deck.
    Both selected cards join the same board Pokémon object. The Stadium
    effect is spent once if and only if the proposed chain succeeds.

    Card metadata and deck-search information are authoritative upstream.
    This function does not select eligible prints or perform a shuffle.
    """

    if (stage2 is None) != (stage2_class is None):
        raise ValueError("stage2 and stage2_class must be supplied together")

    validate_board_position_stack_bindings(ledger, board)
    evolution = execute_grand_tree_chain(
        profile,
        context,
        board,
        pokemon_id,
        stage1,
        stage1_retreat_cost=stage1_retreat_cost,
        stage2=stage2,
        stage2_retreat_cost=stage2_retreat_cost,
    )
    if evolution is None:
        return None

    candidates = ((stage1, stage1_class),)
    if stage2 is not None:
        assert stage2_class is not None
        candidates += ((stage2, stage2_class),)

    staged = ledger
    try:
        for card, card_class in candidates:
            staged = materialize(
                staged,
                card_class=card_class,
                card_name=card.name,
                source_zone="deck",
                instance_id=card.card_id,
            )
            staged = put_in_play_instance(staged, card.card_id, pokemon_id)
    except (KeyError, ValueError):
        return None

    validate_board_position_stack_bindings(staged, evolution.board)
    assert_conserved(ledger, staged)
    return MaterializedGrandTreeChain(evolution, staged)
