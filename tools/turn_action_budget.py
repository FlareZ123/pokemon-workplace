"""Generic per-turn action-budget state for Pokémon TCG planners.

The basic rules give ordinary per-turn limits for Supporter play, Stadium play,
manual Energy attachment, and Retreat. Card effects can modify at least some of
those limits, so the canonical representation stores integer usage and limits
rather than only spent/unspent booleans.

Attack and voluntary turn end close the ordinary action window.
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


@dataclass(frozen=True, init=False)
class TurnActionBudget:
    supporter_plays_used: int
    supporter_play_limit: int
    stadium_plays_used: int
    stadium_play_limit: int
    manual_energy_attachments_used: int
    manual_energy_attachment_limit: int
    retreats_used: int
    retreat_limit: int
    turn_ended: bool

    def __init__(
        self,
        supporter_plays_used: int = 0,
        supporter_play_limit: int = 1,
        stadium_plays_used: int = 0,
        stadium_play_limit: int = 1,
        manual_energy_attachments_used: int = 0,
        manual_energy_attachment_limit: int = 1,
        retreats_used: int = 0,
        retreat_limit: int = 1,
        turn_ended: bool = False,
        *,
        supporter_used: bool | None = None,
        stadium_play_used: bool | None = None,
        manual_energy_attachment_used: bool | None = None,
        retreat_used: bool | None = None,
    ) -> None:
        """Build a budget, accepting legacy boolean aliases during migration."""

        if supporter_used is not None:
            supporter_plays_used = max(supporter_plays_used, int(supporter_used))
        if stadium_play_used is not None:
            stadium_plays_used = max(stadium_plays_used, int(stadium_play_used))
        if manual_energy_attachment_used is not None:
            manual_energy_attachments_used = max(
                manual_energy_attachments_used,
                int(manual_energy_attachment_used),
            )
        if retreat_used is not None:
            retreats_used = max(retreats_used, int(retreat_used))

        numeric = {
            "supporter_plays_used": supporter_plays_used,
            "supporter_play_limit": supporter_play_limit,
            "stadium_plays_used": stadium_plays_used,
            "stadium_play_limit": stadium_play_limit,
            "manual_energy_attachments_used": manual_energy_attachments_used,
            "manual_energy_attachment_limit": manual_energy_attachment_limit,
            "retreats_used": retreats_used,
            "retreat_limit": retreat_limit,
        }
        for name, value in numeric.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

        object.__setattr__(self, "supporter_plays_used", supporter_plays_used)
        object.__setattr__(self, "supporter_play_limit", supporter_play_limit)
        object.__setattr__(self, "stadium_plays_used", stadium_plays_used)
        object.__setattr__(self, "stadium_play_limit", stadium_play_limit)
        object.__setattr__(
            self,
            "manual_energy_attachments_used",
            manual_energy_attachments_used,
        )
        object.__setattr__(
            self,
            "manual_energy_attachment_limit",
            manual_energy_attachment_limit,
        )
        object.__setattr__(self, "retreats_used", retreats_used)
        object.__setattr__(self, "retreat_limit", retreat_limit)
        object.__setattr__(self, "turn_ended", turn_ended)

    @property
    def supporter_used(self) -> bool:
        return self.supporter_plays_used > 0

    @property
    def stadium_play_used(self) -> bool:
        return self.stadium_plays_used > 0

    @property
    def manual_energy_attachment_used(self) -> bool:
        return self.manual_energy_attachments_used > 0

    @property
    def retreat_used(self) -> bool:
        return self.retreats_used > 0

    def can(self, action: TurnAction) -> bool:
        """Return whether this action has remaining generic turn quota."""

        if self.turn_ended:
            return False
        if action is TurnAction.SUPPORTER:
            return self.supporter_plays_used < self.supporter_play_limit
        if action is TurnAction.STADIUM_PLAY:
            return self.stadium_plays_used < self.stadium_play_limit
        if action is TurnAction.MANUAL_ENERGY_ATTACHMENT:
            return (
                self.manual_energy_attachments_used
                < self.manual_energy_attachment_limit
            )
        if action is TurnAction.RETREAT:
            return self.retreats_used < self.retreat_limit
        if action in {TurnAction.ATTACK, TurnAction.END_TURN}:
            return True
        raise ValueError(f"Unsupported turn action: {action!r}")

    def remaining(self, action: TurnAction) -> int:
        """Return remaining uses for one action in the current turn."""

        if self.turn_ended:
            return 0
        if action is TurnAction.SUPPORTER:
            return max(0, self.supporter_play_limit - self.supporter_plays_used)
        if action is TurnAction.STADIUM_PLAY:
            return max(0, self.stadium_play_limit - self.stadium_plays_used)
        if action is TurnAction.MANUAL_ENERGY_ATTACHMENT:
            return max(
                0,
                self.manual_energy_attachment_limit
                - self.manual_energy_attachments_used,
            )
        if action is TurnAction.RETREAT:
            return max(0, self.retreat_limit - self.retreats_used)
        if action in {TurnAction.ATTACK, TurnAction.END_TURN}:
            return 1
        raise ValueError(f"Unsupported turn action: {action!r}")

    def consume(self, action: TurnAction) -> "TurnActionBudget | None":
        """Consume one unit of an action quota, or return None if unavailable."""

        if not self.can(action):
            return None
        if action is TurnAction.SUPPORTER:
            return replace(
                self,
                supporter_plays_used=self.supporter_plays_used + 1,
            )
        if action is TurnAction.STADIUM_PLAY:
            return replace(
                self,
                stadium_plays_used=self.stadium_plays_used + 1,
            )
        if action is TurnAction.MANUAL_ENERGY_ATTACHMENT:
            return replace(
                self,
                manual_energy_attachments_used=(
                    self.manual_energy_attachments_used + 1
                ),
            )
        if action is TurnAction.RETREAT:
            return replace(self, retreats_used=self.retreats_used + 1)
        if action in {TurnAction.ATTACK, TurnAction.END_TURN}:
            return replace(self, turn_ended=True)
        raise ValueError(f"Unsupported turn action: {action!r}")

    def with_limit(self, action: TurnAction, limit: int) -> "TurnActionBudget":
        """Return a budget with one action limit replaced by card/effect state."""

        if limit < 0:
            raise ValueError("action limit must be non-negative")
        if action is TurnAction.SUPPORTER:
            return replace(self, supporter_play_limit=limit)
        if action is TurnAction.STADIUM_PLAY:
            return replace(self, stadium_play_limit=limit)
        if action is TurnAction.MANUAL_ENERGY_ATTACHMENT:
            return replace(self, manual_energy_attachment_limit=limit)
        if action is TurnAction.RETREAT:
            return replace(self, retreat_limit=limit)
        raise ValueError("attack/end-turn are not quota-limited channels")

    def next_turn(self) -> "TurnActionBudget":
        """Reset usage while preserving currently derived action limits."""

        return TurnActionBudget(
            supporter_play_limit=self.supporter_play_limit,
            stadium_play_limit=self.stadium_play_limit,
            manual_energy_attachment_limit=self.manual_energy_attachment_limit,
            retreat_limit=self.retreat_limit,
        )


def budget_from_flags(
    *,
    supporter_used: bool = False,
    stadium_play_used: bool = False,
    manual_energy_attachment_used: bool = False,
    retreat_used: bool = False,
    turn_ended: bool = False,
) -> TurnActionBudget:
    """Adapter for legacy kernels whose ordinary limits are all one."""

    return TurnActionBudget(
        supporter_used=supporter_used,
        stadium_play_used=stadium_play_used,
        manual_energy_attachment_used=manual_energy_attachment_used,
        retreat_used=retreat_used,
        turn_ended=turn_ended,
    )
