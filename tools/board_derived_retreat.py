"""Execute Retreat after deriving represented board-dependent state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from attached_energy_retreat_modifiers import attached_energy_retreat_modifiers
from attached_tool_retreat_modifiers import (
    UnresolvedToolRetreatCondition,
    derive_tool_retreat_modifiers,
)
from board_object_kernel import BoardState
from retreat_board_effects import active_scoop_up_block_source_ids
from retreat_cost_semantics import RetreatCostModifier, effective_retreat_cost
from retreat_dynamic_energy_units import RetreatEnergyProviderContext
from retreat_energy_normalization import (
    RetreatEnergyNormalization,
    normalize_retreat_energy_state,
)
from retreat_energy_transaction import (
    RetreatEnergyTransactionResult,
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)


@dataclass(frozen=True)
class BoardDerivedRetreatAttempt:
    normalization: RetreatEnergyNormalization
    effective_retreat_cost: int
    applied_modifiers: tuple[RetreatCostModifier, ...]
    scoop_up_block_source_ids: tuple[str, ...]
    unresolved_tool_conditions: tuple[UnresolvedToolRetreatCondition, ...]
    transaction: RetreatEnergyTransactionResult | None


def attempt_board_derived_retreat(
    state: RetreatEnergyTransactionState,
    bench_object_id: str,
    *,
    base_retreat_cost: int,
    discard_energy_ids: Iterable[str],
    opponent_board: BoardState,
    provider_context: RetreatEnergyProviderContext | None = None,
    active_remaining_hp: int | None = None,
    external_modifiers: tuple[RetreatCostModifier, ...] = (),
    prism_star_energy_ids: Iterable[str] = (),
) -> BoardDerivedRetreatAttempt:
    """Normalize state, derive represented modifiers/effects, then Retreat."""

    normalization = normalize_retreat_energy_state(
        state,
        provider_context=provider_context,
    )
    prepared = normalization.state
    active = prepared.energy.board.get(prepared.energy.board.active_id)

    energy_modifiers = attached_energy_retreat_modifiers(active)
    tool_derivation = derive_tool_retreat_modifiers(
        prepared.energy.board,
        opponent_board,
        active_remaining_hp=active_remaining_hp,
    )
    modifiers = (
        external_modifiers
        + energy_modifiers
        + tool_derivation.modifiers
    )
    retreat_cost = effective_retreat_cost(base_retreat_cost, modifiers)
    scoop_sources = active_scoop_up_block_source_ids(opponent_board)

    transaction = None
    if tool_derivation.exact:
        transaction = retreat_with_energy_destinations(
            prepared,
            bench_object_id,
            retreat_cost=retreat_cost,
            discard_energy_ids=discard_energy_ids,
            opposing_scoop_up_block_active=bool(scoop_sources),
            prism_star_energy_ids=prism_star_energy_ids,
        )

    return BoardDerivedRetreatAttempt(
        normalization=normalization,
        effective_retreat_cost=retreat_cost,
        applied_modifiers=modifiers,
        scoop_up_block_source_ids=scoop_sources,
        unresolved_tool_conditions=tool_derivation.unresolved_conditions,
        transaction=transaction,
    )
