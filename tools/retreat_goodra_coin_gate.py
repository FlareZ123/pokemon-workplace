"""Exact two-branch normal-Retreat overlay for Goodra's Slimy Sliding.

The engine's deterministic Retreat action is the *heads* continuation.
Tails prevents Energy payment and movement but spends one canonical Retreat
quota. Multiple active Slimy Sliding sources cause only one coin flip.
This wrapper applies to ordinary Retreat actions, never effect-based Switch.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction

from board_object_kernel import BoardState
from energy_board_conservation import EnergyBoardState
from retreat_ability_lock_bridge import project_retreat_ability_state
from ability_lock_causal_state import AbilityLockCausalState
from retreat_action_enumerator import LegalRetreatAction
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnAction
from unified_state_kernel import consume_turn_action


GOODRA_SLIMY_SLIDING_PRINT_IDS = frozenset({"me4-68"})


@dataclass(frozen=True)
class GoodraRetreatOutcome:
    label: str
    probability: Fraction
    state: RetreatEnergyTransactionState
    retreated: bool
    source_ids: tuple[str, ...]


def opponent_slimy_sliding_sources(
    opponent_board: BoardState,
) -> tuple[str, ...]:
    """Only live, verified printed Goodra Abilities count; Bench is allowed."""
    return tuple(sorted(
        source.object_id for source in opponent_board.objects
        if source.print_id in GOODRA_SLIMY_SLIDING_PRINT_IDS
        and source.card_name == "Goodra"
        and source.abilities_enabled
    ))


def _failed_retreat_spent_state(
    state: RetreatEnergyTransactionState,
) -> RetreatEnergyTransactionState:
    """No zone or position change, but the Retreat quota is consumed."""
    unified = consume_turn_action(state.unified, TurnAction.RETREAT)
    if unified is None or unified.turn_budget is None:
        raise ValueError("Retreat quota was unavailable for supplied action")
    board = replace(
        state.energy.board,
        retreat_used=unified.turn_budget.retreat_used,
    )
    board.validate()
    return RetreatEnergyTransactionState(
        unified=unified,
        energy=EnergyBoardState(
            zones=state.energy.zones,
            board=board,
            instance_classes=state.energy.instance_classes,
        ),
    )


def normal_retreat_goodra_outcomes(
    state: RetreatEnergyTransactionState,
    opponent_board: BoardState,
    action: LegalRetreatAction,
    *,
    ability_lock_state: AbilityLockCausalState | None = None,
) -> tuple[GoodraRetreatOutcome, ...]:
    """Resolve the success/failure distribution for an existing Retreat action.

    Call with the same initial state, opponent board, and Ability-lock context
    used to enumerate the supplied legal action. Other random replacement
    effects and response effects are outside this restricted model.
    """
    transaction = action.attempt.transaction
    if transaction is None or not transaction.committed:
        raise ValueError("Expected a committed deterministic Retreat action")

    projected = project_retreat_ability_state(
        state.energy.board, opponent_board, lock_state=ability_lock_state,
    )
    if not projected.resolved:
        raise ValueError("Cannot branch under unresolved Ability-lock state")
    sources = opponent_slimy_sliding_sources(projected.opponent_board)
    if not sources:
        return (GoodraRetreatOutcome(
            "unopposed", Fraction(1), transaction.state, True, (),
        ),)

    tails = _failed_retreat_spent_state(state)
    return (
        GoodraRetreatOutcome(
            "heads", Fraction(1, 2), transaction.state, True, sources,
        ),
        GoodraRetreatOutcome(
            "tails", Fraction(1, 2), tails, False, sources,
        ),
    )
