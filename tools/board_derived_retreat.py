"""Execute Retreat after deriving represented board-dependent state."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from attached_energy_retreat_modifiers import attached_energy_retreat_modifiers
from attached_tool_retreat_modifiers import (
    UnresolvedToolRetreatCondition,
    derive_tool_retreat_modifiers,
    tool_retreat_cost_decision_sufficient,
)
from ability_lock_causal_state import AbilityLockCausalState
from board_object_kernel import BoardState
from energy_board_conservation import EnergyBoardState
from retreat_ability_denial import opposing_retreat_denial_source_ids
from retreat_ability_lock_bridge import project_retreat_ability_state
from retreat_board_effects import active_scoop_up_block_source_ids
from retreat_cost_semantics import RetreatCostModifier, effective_retreat_cost
from retreat_dynamic_energy_units import (
    RetreatEnergyProviderContext,
    unresolved_selected_prize_provider_ids,
)
from retreat_environment_modifiers import derive_environment_retreat_modifiers
from retreat_stadium_tool_overlay import (
    project_stadium_tool_state,
    restore_persistent_tool_flags,
)
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
    unresolved_ability_lock: bool
    suppressed_own_ability_ids: tuple[str, ...]
    suppressed_opponent_ability_ids: tuple[str, ...]
    suppressed_own_tool_ids: tuple[str, ...]
    suppressed_opponent_tool_ids: tuple[str, ...]
    unresolved_tool_conditions: tuple[UnresolvedToolRetreatCondition, ...]
    tool_action_sufficient: bool
    unresolved_selected_provider_ids: tuple[str, ...]
    transaction: RetreatEnergyTransactionResult | None


def attempt_board_derived_retreat(
    state: RetreatEnergyTransactionState,
    bench_object_id: str,
    *,
    base_retreat_cost: int,
    discard_energy_ids: Iterable[str],
    opponent_board: BoardState,
    ability_lock_state: AbilityLockCausalState | None = None,
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
    tool_projection = project_stadium_tool_state(
        prepared.energy.board,
        opponent_board,
        stadium_print_id=stadium_print_id,
        stadium_effect_enabled=stadium_effect_enabled,
    )
    if tool_projection.own_board is not prepared.energy.board:
        prepared = RetreatEnergyTransactionState(
            unified=prepared.unified,
            energy=EnergyBoardState(
                zones=prepared.energy.zones,
                board=tool_projection.own_board,
                instance_classes=prepared.energy.instance_classes,
            ),
        )
    active = prepared.energy.board.get(prepared.energy.board.active_id)
    ability_projection = project_retreat_ability_state(
        prepared.energy.board,
        tool_projection.opponent_board,
        lock_state=ability_lock_state,
    )
    own_sources = ability_projection.own_board
    opponent_sources = ability_projection.opponent_board

    energy_modifiers = attached_energy_retreat_modifiers(active)
    tool_derivation = derive_tool_retreat_modifiers(
        own_sources,
        opponent_sources,
        active_remaining_hp=active_remaining_hp,
    )
    environmental_modifiers = derive_environment_retreat_modifiers(
        own_sources,
        opponent_sources,
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
    tool_action_sufficient = tool_retreat_cost_decision_sufficient(
        tool_derivation, retreat_cost,
    )
    scoop_sources = active_scoop_up_block_source_ids(opponent_sources)
    denial_sources = opposing_retreat_denial_source_ids(
        own_sources, opponent_sources,
    )
    unresolved_providers = unresolved_selected_prize_provider_ids(
        prepared,
        selected_energy_ids,
        retreat_cost=retreat_cost,
        context=provider_context,
    )

    transaction = None
    if (
        tool_action_sufficient
        and ability_projection.resolved
        and not unresolved_providers
        and not denial_sources
    ):
        transaction = retreat_with_energy_destinations(
            prepared,
            bench_object_id,
            retreat_cost=retreat_cost,
            discard_energy_ids=selected_energy_ids,
            opposing_scoop_up_block_active=bool(scoop_sources),
            prism_star_energy_ids=prism_star_energy_ids,
        )
        if transaction is not None and tool_projection.suppressed_own_tool_ids:
            corrected_board = restore_persistent_tool_flags(
                normalization.state.energy.board,
                transaction.state.energy.board,
            )
            physical_result = RetreatEnergyTransactionState(
                unified=transaction.state.unified,
                energy=EnergyBoardState(
                    zones=transaction.state.energy.zones,
                    board=corrected_board,
                    instance_classes=transaction.state.energy.instance_classes,
                ),
            )
            transaction = replace(transaction, state=physical_result)

    return BoardDerivedRetreatAttempt(
        normalization=normalization,
        effective_retreat_cost=retreat_cost,
        applied_modifiers=modifiers,
        scoop_up_block_source_ids=scoop_sources,
        retreat_denial_source_ids=denial_sources,
        unresolved_ability_lock=not ability_projection.resolved,
        suppressed_own_ability_ids=ability_projection.suppressed_own_ids,
        suppressed_opponent_ability_ids=ability_projection.suppressed_opponent_ids,
        suppressed_own_tool_ids=tool_projection.suppressed_own_tool_ids,
        suppressed_opponent_tool_ids=tool_projection.suppressed_opponent_tool_ids,
        unresolved_tool_conditions=tool_derivation.unresolved_conditions,
        tool_action_sufficient=tool_action_sufficient,
        unresolved_selected_provider_ids=unresolved_providers,
        transaction=transaction,
    )
