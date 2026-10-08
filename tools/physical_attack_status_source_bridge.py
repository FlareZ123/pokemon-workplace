"""Apply a verified copied-attack source status in the attack-effect step.

The function consumes a completed copy-body physical replay before damage
reactions and Knock Out disposal. It preserves the card-instance ledger and
requires explicit coin and attack-effect immunity inputs.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from attack_status_text_contracts import AttackStatusSourceContract
from board_position_state import replace_pokemon
from special_condition_state import (
    ConditionKind,
    SpecialConditionState,
    apply_condition,
    legacy_name_projection,
    regular_condition,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class PhysicalAttackStatusApplication:
    state: StackBoardMaterialState
    typed_active_conditions: SpecialConditionState
    target_id: str
    condition: ConditionKind
    applied: bool
    body_event: str


def apply_physical_attack_source_status(
    replay: AttackCopyPhysicalBoardResolution,
    contract: AttackStatusSourceContract,
    *,
    coin_heads: bool | None = None,
    prevent_effects_of_attacks: bool = False,
    typed_current: SpecialConditionState | None = None,
) -> PhysicalAttackStatusApplication:
    """Apply ordinary status on opponent Active after source attack damage.

    The caller supplies an authoritative typed state when a Pokémon already
    has conditions, avoiding lossy reconstruction of irregular Poison/Burn.
    """
    body_event = f"body:{contract.attack_id}"
    if body_event not in replay.resolution.state.events:
        raise ValueError("copy-body trace did not execute this source attack")
    board = replay.state.board
    if board is None:
        raise ValueError("source effect requires an in-play physical board")
    if contract.target_scope != "opponent_active":
        raise ValueError("unsupported attack status target scope")
    target = board.get(board.active_id)
    if typed_current is None:
        if target.special_conditions:
            raise ValueError("existing status requires a lossless typed payload")
        typed_current = SpecialConditionState()
    if legacy_name_projection(typed_current) != target.special_conditions:
        raise ValueError("typed and physical conditions disagree")

    if contract.requires_coin_result is None:
        if coin_heads is not None:
            raise ValueError("unconditional source status has no coin branch")
        branch_satisfied = True
    else:
        if coin_heads is None:
            raise ValueError("coin-gated source status requires a coin result")
        observed = "heads" if coin_heads else "tails"
        branch_satisfied = observed == contract.requires_coin_result

    kind = ConditionKind(contract.special_condition)
    applied = branch_satisfied and not prevent_effects_of_attacks
    next_typed = (
        apply_condition(
            typed_current,
            regular_condition(kind, source_label=contract.attack_id),
        )
        if applied else typed_current
    )
    if applied:
        updated = replace(
            target, special_conditions=legacy_name_projection(next_typed),
        )
        state = StackBoardMaterialState(
            replay.state.ledger,
            replace_pokemon(board, updated),
        )
    else:
        state = replay.state

    return PhysicalAttackStatusApplication(
        state=state,
        typed_active_conditions=next_typed,
        target_id=board.active_id,
        condition=kind,
        applied=applied,
        body_event=body_event,
    )
