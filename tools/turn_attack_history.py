"""Turn-scoped attack provenance for paper Expanded research.

This module records every declared attack in a turn and keeps the most recently
completed turn for each player. It intentionally records attack history without
deciding how many attacks a card effect permits.
"""

from __future__ import annotations

from dataclasses import dataclass


class LossyLastAttackProjectionError(ValueError):
    """Raised when a scalar last-attack projection would discard turn history."""


@dataclass(frozen=True)
class CompletedTurnAttacks:
    player_id: str
    turn_index: int
    declared_attack_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")
        if self.turn_index < 0:
            raise ValueError("turn_index must be non-negative")
        if any(not attack_id for attack_id in self.declared_attack_ids):
            raise ValueError("attack IDs must be non-empty")


@dataclass(frozen=True)
class TurnAttackHistory:
    current_player: str
    turn_index: int = 0
    current_turn_attack_ids: tuple[str, ...] = ()
    last_completed_turns: tuple[CompletedTurnAttacks, ...] = ()

    def __post_init__(self) -> None:
        if not self.current_player:
            raise ValueError("current_player must be non-empty")
        if self.turn_index < 0:
            raise ValueError("turn_index must be non-negative")
        if any(not attack_id for attack_id in self.current_turn_attack_ids):
            raise ValueError("attack IDs must be non-empty")

        players = [record.player_id for record in self.last_completed_turns]
        if len(players) != len(set(players)):
            raise ValueError("last_completed_turns must contain at most one record per player")

    def last_turn_for(self, player_id: str) -> CompletedTurnAttacks | None:
        for record in self.last_completed_turns:
            if record.player_id == player_id:
                return record
        return None

    def last_turn_attacks_for(self, player_id: str) -> tuple[str, ...]:
        record = self.last_turn_for(player_id)
        if record is None:
            return ()
        return record.declared_attack_ids


def record_attack(
    history: TurnAttackHistory,
    declared_attack_id: str,
) -> TurnAttackHistory:
    """Append one declared attack to the current turn in execution order."""

    if not declared_attack_id:
        raise ValueError("declared_attack_id must be non-empty")
    return TurnAttackHistory(
        current_player=history.current_player,
        turn_index=history.turn_index,
        current_turn_attack_ids=history.current_turn_attack_ids + (declared_attack_id,),
        last_completed_turns=history.last_completed_turns,
    )


def advance_turn(
    history: TurnAttackHistory,
    *,
    next_player: str,
) -> TurnAttackHistory:
    """Finish the current turn and begin the next chronological turn.

    The completed record is written even when the turn contained zero attacks.
    This overwrites that player's older last-turn record, which prevents stale
    attack provenance after a later turn ends without attacking.
    """

    if not next_player:
        raise ValueError("next_player must be non-empty")

    completed = CompletedTurnAttacks(
        player_id=history.current_player,
        turn_index=history.turn_index,
        declared_attack_ids=history.current_turn_attack_ids,
    )
    by_player = {record.player_id: record for record in history.last_completed_turns}
    by_player[history.current_player] = completed

    return TurnAttackHistory(
        current_player=next_player,
        turn_index=history.turn_index + 1,
        current_turn_attack_ids=(),
        last_completed_turns=tuple(by_player[player] for player in sorted(by_player)),
    )


def copy_kernel_last_attack_projection(
    history: TurnAttackHistory,
) -> tuple[tuple[str, str], ...]:
    """Project last-turn provenance into attack_copy_kernel's scalar interface.

    A blank last turn contributes no attack. A one-attack turn projects exactly.
    A turn with multiple attacks cannot be represented without losing history,
    so callers must keep the richer turn record.
    """

    projected: list[tuple[str, str]] = []
    for record in history.last_completed_turns:
        count = len(record.declared_attack_ids)
        if count == 0:
            continue
        if count > 1:
            raise LossyLastAttackProjectionError(
                f"{record.player_id}'s last turn contains {count} attacks"
            )
        projected.append((record.player_id, record.declared_attack_ids[0]))
    return tuple(projected)
