"""Generic per-turn action-budget state for Pokémon TCG planners.

The model captures mechanical action channels that are globally limited during
one player's turn:

- one Supporter play;
- one Stadium play;
- one normal Energy attachment from hand;
- one normal Retreat;
- one attack, which ends the turn;
- voluntary turn end, which likewise closes the action window.

Card-specific legality, first-turn restrictions, attack eligibility, locks,
and effect-based extra actions remain upstream. This module only tracks whether
the generic turn resource is still available.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class TurnAction(str, Enum):
    SUPPORTER = "supporter"
    STADIUM_PLAY = "stadium_play"
    MANUAL_ENERGY_ATTACHMENT = "manual_energy_attachment"
    RETREAT = "retreat"
    ATTACK = "attack"
    END_TURN = "end_turn"


@dataclass(frozen=True)
class TurnActionBudget:
    supporter_used: bool = False
    stadium_play_used: bool = False
    manual_energy_attachment_used: bool = False
    retreat_used: bool = False
    turn_ended: bool = False

    def can(self, action: TurnAction) -> bool:
        """Return whether this generic action channel is still available."""

        if self.turn_ended:
            return False
        if action is TurnAction.SUPPORTER:
            return not self.supporter_used
        if action is TurnAction.STADIUM_PLAY:
            return not self.stadium_play_used
        if action is TurnAction.MANUAL_ENERGY_ATTACHMENT:
            return not self.manual_energy_attachment_used
        if action is TurnAction.RETREAT:
            return not self.retreat_used
        if action in {TurnAction.ATTACK, TurnAction.END_TURN}:
            return True
        raise ValueError(f"Unsupported turn action: {action!r}")

    def consume(self, action: TurnAction) -> "TurnActionBudget | None":
        """Consume one generic action channel, or return None if unavailable."""

        if not self.can(action):
            return None
        if action is TurnAction.SUPPORTER:
            return replace(self, supporter_used=True)
        if action is TurnAction.STADIUM_PLAY:
            return replace(self, stadium_play_used=True)
        if action is TurnAction.MANUAL_ENERGY_ATTACHMENT:
            return replace(self, manual_energy_attachment_used=True)
        if action is TurnAction.RETREAT:
            return replace(self, retreat_used=True)
        if action in {TurnAction.ATTACK, TurnAction.END_TURN}:
            return replace(self, turn_ended=True)
        raise ValueError(f"Unsupported turn action: {action!r}")

    def next_turn(self) -> "TurnActionBudget":
        """Return a fresh budget for the next player's turn."""

        return TurnActionBudget()


def budget_from_flags(
    *,
    supporter_used: bool = False,
    stadium_play_used: bool = False,
    manual_energy_attachment_used: bool = False,
    retreat_used: bool = False,
    turn_ended: bool = False,
) -> TurnActionBudget:
    """Adapter for kernels that currently store these flags separately."""

    return TurnActionBudget(
        supporter_used=supporter_used,
        stadium_play_used=stadium_play_used,
        manual_energy_attachment_used=manual_energy_attachment_used,
        retreat_used=retreat_used,
        turn_ended=turn_ended,
    )
