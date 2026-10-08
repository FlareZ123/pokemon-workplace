"""Enumerate executable Retreat payment and promotion actions from exact boards."""

from __future__ import annotations

from dataclasses import dataclass

from ability_lock_causal_state import AbilityLockCausalState
from board_derived_retreat import (
    BoardDerivedRetreatAttempt,
    attempt_board_derived_retreat,
)
from board_object_kernel import BoardState, legal_retreat_energy_choices
from retreat_cost_semantics import RetreatCostModifier
from retreat_dynamic_energy_units import (
    COUNTER_ENERGY_PRINT_IDS,
    REVERSAL_ENERGY_PRINT_IDS,
    RetreatEnergyProviderContext,
    holder_has_rule_box,
    holder_is_evolution,
    holder_is_pokemon_ex,
    holder_is_pokemon_gx,
)
from retreat_energy_transaction import RetreatEnergyTransactionState


@dataclass(frozen=True)
class LegalRetreatAction:
    bench_object_id: str
    discard_energy_ids: tuple[str, ...]
    attempt: BoardDerivedRetreatAttempt


@dataclass(frozen=True)
class RetreatActionEnumeration:
    preflight: BoardDerivedRetreatAttempt | None
    actions: tuple[LegalRetreatAction, ...]
    checked_candidate_count: int
    information_complete: bool


def _prize_provider_ambiguity(
    state: RetreatEnergyTransactionState,
    context: RetreatEnergyProviderContext | None,
) -> bool:
    if context is not None and context.prize_counts_known:
        return False
    board = state.energy.board
    active = board.get(board.active_id)
    for energy in active.energy:
        if (
            energy.card_name == "Counter Energy"
            and energy.print_id in COUNTER_ENERGY_PRINT_IDS
            and not holder_is_pokemon_gx(active.tags)
            and not holder_is_pokemon_ex(active.tags)
        ):
            return True
        if (
            energy.card_name == "Reversal Energy"
            and energy.print_id in REVERSAL_ENERGY_PRINT_IDS
            and holder_is_evolution(active.tags)
            and not holder_has_rule_box(active.tags)
        ):
            return True
    return False


def enumerate_board_derived_retreat_actions(
    state: RetreatEnergyTransactionState,
    opponent_board: BoardState,
    *,
    base_retreat_cost: int,
    ability_lock_state: AbilityLockCausalState | None = None,
    provider_context: RetreatEnergyProviderContext | None = None,
    active_remaining_hp: int | None = None,
    external_modifiers: tuple[RetreatCostModifier, ...] = (),
    stadium_print_id: str | None = None,
    stadium_effect_enabled: bool = True,
    prism_star_energy_ids: tuple[str, ...] = (),
) -> RetreatActionEnumeration:
    """Enumerate legal physical payment choices and promoted Bench targets.

    A probe derives current effective cost and normalized attached Energy.
    Each candidate is independently executed from the original immutable
    state, preserving payment-specific destination and quota outcomes.
    Under unknown Prize-dependent provider state, only guaranteed outcomes
    can be returned and information_complete is marked false.
    """
    bench_ids = tuple(sorted(state.energy.board.bench_ids))
    if not bench_ids:
        return RetreatActionEnumeration(None, (), 0, True)

    options = dict(
        base_retreat_cost=base_retreat_cost,
        opponent_board=opponent_board,
        ability_lock_state=ability_lock_state,
        provider_context=provider_context,
        active_remaining_hp=active_remaining_hp,
        external_modifiers=external_modifiers,
        stadium_print_id=stadium_print_id,
        stadium_effect_enabled=stadium_effect_enabled,
        prism_star_energy_ids=prism_star_energy_ids,
    )
    preflight = attempt_board_derived_retreat(
        state, bench_ids[0], discard_energy_ids=(), **options,
    )
    uncertain = (
        preflight.unresolved_ability_lock
        or bool(preflight.unresolved_tool_conditions)
        or _prize_provider_ambiguity(preflight.normalization.state, provider_context)
    )
    if preflight.unresolved_ability_lock or preflight.unresolved_tool_conditions:
        return RetreatActionEnumeration(preflight, (), 0, False)

    normalized_board = preflight.normalization.state.energy.board
    active = normalized_board.get(normalized_board.active_id)
    payments = legal_retreat_energy_choices(
        active, preflight.effective_retreat_cost,
    )
    actions = []
    checked = 0
    for bench_id in bench_ids:
        for payment in payments:
            checked += 1
            attempt = attempt_board_derived_retreat(
                state, bench_id, discard_energy_ids=payment, **options,
            )
            if attempt.transaction is not None and attempt.transaction.committed:
                actions.append(
                    LegalRetreatAction(bench_id, payment, attempt)
                )
    return RetreatActionEnumeration(
        preflight=preflight,
        actions=tuple(actions),
        checked_candidate_count=checked,
        information_complete=not uncertain,
    )
