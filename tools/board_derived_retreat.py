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
from retreat_ability_denial import opposing_retreat_denial_source_ids
from retreat_board_effects import active_scoop_up_block_source_ids
from retreat_cost_semantics import RetreatCostModifier, effective_retreat_cost
from retreat_dynamic_energy_units import (
    RetreatEnergyProviderContext,
    unresolved_selected_prize_provider_ids,
)
from retreat_environment_modifiers import derive_environment_retreat_modifiers
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
    retreat_denial_source_ids: tuple[str, ...]
    unresolved_tool_conditions: tuple[UnresolvedToolRetreatCondition, ...]
    unresolved_selected_provider_ids: tuple[str, ...]
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
    stadium_print_id: str | None = None,
    stadium_effect_enabled: bool = True,
    prism_star_energy_ids: Iterable[str] = (),
) -> BoardDerivedRetreatAttempt:
    """Normalize state, derive represented modifiers/effects, then Retreat."""

    selected_energy_ids = tuple(discard_energy_ids)
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
    environmental_modifiers = derive_environment_retreat_modifiers(
        prepared.energy.board,
        opponent_board,
        stadium_print_id=stadium_print_id,
        stadium_effect_enabled=stadium_effect_enabled,
    )
    modifiers = (
        external_modifiers
        + energy_modifiers
        + tool_derivation.modifiers
        + environmental_modifiers
    )
    retreat_cost = effective_retreat_cost(base_retreat_cost, modifiers)
    scoop_sources = active_scoop_up_block_source_ids(opponent_board)
    denial_sources = opposing_retreat_denial_source_ids(
        prepared.energy.board, opponent_board,
    )
    unresolved_providers = unresolved_selected_prize_provider_ids(
        prepared,
        selected_energy_ids,
        retreat_cost=retreat_cost,
        context=provider_context,
    )

    transaction = None
    if tool_derivation.exact and not unresolved_providers and not denial_sources:
        transaction = retreat_with_energy_destinations(
            prepared,
            bench_object_id,
            retreat_cost=retreat_cost,
            discard_energy_ids=selected_energy_ids,
            opposing_scoop_up_block_active=bool(scoop_sources),
            prism_star_energy_ids=prism_star_energy_ids,
        )

    return BoardDerivedRetreatAttempt(
        normalization=normalization,
        effective_retreat_cost=retreat_cost,
        applied_modifiers=modifiers,
        scoop_up_block_source_ids=scoop_sources,
        retreat_denial_source_ids=denial_sources,
        unresolved_tool_conditions=tool_derivation.unresolved_conditions,
        unresolved_selected_provider_ids=unresolved_providers,
        transaction=transaction,
    )
