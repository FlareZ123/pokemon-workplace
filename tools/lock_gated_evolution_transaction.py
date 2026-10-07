"""Compose ordinary physical evolution with live source-scoped lock state."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from ability_lock_causal_state import AbilityLockCausalState, advance_lock_state
from attack_restriction_turn_windows import AttackRestrictionWindow
from board_derived_action_permissions import (
    BoardDerivedActionPermission,
    evaluate_board_derived_action_permission,
)
from board_object_kernel import BoardState
from card_action_metadata import CardActionMetadata
from evolution_stack_binding import EvolutionTransition, ordinary_evolve
from evolution_stack_state import EvolutionState, StackCard
from identity_materialization import IdentityLedger
from source_scoped_restriction_activation import RestrictionActivationProfile
from target_bound_attack_restrictions import (
    TargetBoundAttackRestrictionWindow,
    advance_target_binding,
)


@dataclass(frozen=True)
class LockGatedEvolutionResult:
    permission: BoardDerivedActionPermission
    transition: EvolutionTransition | None
    lock_state: AbilityLockCausalState
    target_bound_windows: tuple[TargetBoundAttackRestrictionWindow, ...]


def _advance_bound_windows(
    windows: Sequence[TargetBoundAttackRestrictionWindow],
    *,
    actor: str,
    previous_board: BoardState,
    current_board: BoardState,
) -> tuple[TargetBoundAttackRestrictionWindow, ...]:
    rows: list[TargetBoundAttackRestrictionWindow] = []
    for bound in windows:
        if bound.window.other_player == actor:
            rows.append(
                advance_target_binding(
                    bound,
                    previous_board,
                    current_board,
                )
            )
        else:
            rows.append(bound)
    return tuple(rows)


def execute_lock_gated_evolution(
    state: EvolutionState,
    ledger: IdentityLedger,
    object_id: str,
    card: StackCard,
    *,
    actor: str,
    player_board: BoardState,
    opponent_board: BoardState,
    profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    action_metadata: CardActionMetadata,
    stadium_name: str | None = None,
    player_id: str = "player",
    opponent_id: str = "opponent",
    attack_windows: Sequence[AttackRestrictionWindow] = (),
    target_bound_attack_windows: Sequence[TargetBoundAttackRestrictionWindow] = (),
) -> LockGatedEvolutionResult:
    """Attempt one ordinary hand evolution under current lock state."""

    if action_metadata.card_id != card.print_id:
        raise ValueError("evolution card metadata does not match StackCard print")
    if action_metadata.card_kind != "pokemon":
        raise ValueError("evolution action metadata must describe a Pokemon")

    if actor == player_id:
        actor_board = player_board
        if state.board != player_board:
            raise ValueError("EvolutionState board does not match actor board")
    elif actor == opponent_id:
        actor_board = opponent_board
        if state.board != opponent_board:
            raise ValueError("EvolutionState board does not match actor board")
    else:
        raise ValueError("unknown actor")

    permission = evaluate_board_derived_action_permission(
        action_metadata.attempt("hand", mode="evolve"),
        player=actor,
        player_board=player_board,
        opponent_board=opponent_board,
        profiles=profiles,
        lock_state=lock_state,
        stadium_name=stadium_name,
        player_id=player_id,
        opponent_id=opponent_id,
        attack_windows=attack_windows,
        target_bound_attack_windows=target_bound_attack_windows,
        target_object_id=object_id,
    )
    if not permission.allowed:
        return LockGatedEvolutionResult(
            permission=permission,
            transition=None,
            lock_state=lock_state,
            target_bound_windows=tuple(target_bound_attack_windows),
        )

    transition = ordinary_evolve(state, ledger, object_id, card)
    if transition is None:
        return LockGatedEvolutionResult(
            permission=permission,
            transition=None,
            lock_state=lock_state,
            target_bound_windows=tuple(target_bound_attack_windows),
        )

    next_actor_board = transition.state.board
    next_windows = _advance_bound_windows(
        target_bound_attack_windows,
        actor=actor,
        previous_board=actor_board,
        current_board=next_actor_board,
    )

    if actor == player_id:
        next_player_board = next_actor_board
        next_opponent_board = opponent_board
    else:
        next_player_board = player_board
        next_opponent_board = next_actor_board

    next_lock_state = advance_lock_state(
        lock_state,
        next_player_board,
        next_opponent_board,
        stadium_name=stadium_name,
    )
    return LockGatedEvolutionResult(
        permission=permission,
        transition=transition,
        lock_state=next_lock_state,
        target_bound_windows=next_windows,
    )
