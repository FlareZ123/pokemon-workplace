"""Compose copied-attack damage with the step-6 damage reaction phase."""

from __future__ import annotations

from dataclasses import dataclass

from attack_copy_damage_bridge import AttackCopyBoardResolution
from attack_copy_turn_boundary_bridge import close_declared_attack
from board_object_kernel import BoardState
from canonical_turn_sequence_owner import TurnScheduleState
from damage_calculation_kernel import DamageResult
from damage_reaction_kernel import (
    DamageReaction,
    DamageReactionResult,
    resolve_damage_reactions,
)
from unified_state_kernel import UnifiedState


@dataclass(frozen=True)
class AttackCopyReactionResolution:
    board_resolution: AttackCopyBoardResolution
    body_event: str
    damage_result: DamageResult
    reaction_result: DamageReactionResult


def resolve_copy_damage_reactions(
    board_resolution: AttackCopyBoardResolution,
    attacker_board: BoardState,
    *,
    body_event: str,
    reactions: tuple[DamageReaction, ...],
    attacker_hp_by_object_id: dict[str, int],
    defender_hp_by_object_id: dict[str, int],
) -> AttackCopyReactionResolution:
    """Resolve post-damage reactions for one executed copied body event.

    The board-resolution input has already replayed the full declared-attack
    event stream, including outer copy continuations. Reactions are therefore
    applied before the shared Knock Out phase while all zero-HP Pokemon remain
    present.
    """

    matches = tuple(
        result
        for event, result in board_resolution.damage_results
        if event == body_event
    )
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one damage result for {body_event!r}; "
            f"found {len(matches)}"
        )
    damage_result = matches[0]

    reaction_result = resolve_damage_reactions(
        attacker_board,
        board_resolution.board,
        damage_result,
        reactions=reactions,
        attacker_hp_by_object_id=attacker_hp_by_object_id,
        defender_hp_by_object_id=defender_hp_by_object_id,
    )
    return AttackCopyReactionResolution(
        board_resolution=board_resolution,
        body_event=body_event,
        damage_result=damage_result,
        reaction_result=reaction_result,
    )


def close_copy_attack_after_reactions_if_no_knockouts(
    schedule: TurnScheduleState,
    current_state: UnifiedState,
    reaction_resolution: AttackCopyReactionResolution,
) -> tuple[TurnScheduleState, UnifiedState] | None:
    """Hand off to the turn scheduler only if the KO phase is empty."""

    result = reaction_resolution.reaction_result
    if result.attacker_knocked_out_ids or result.defender_knocked_out_ids:
        return None
    return close_declared_attack(
        schedule,
        current_state,
        reaction_resolution.board_resolution.resolution,
    )
