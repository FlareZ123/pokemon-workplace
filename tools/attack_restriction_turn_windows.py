"""Turn-relative lifetime owner for concrete attack-applied restrictions."""

from __future__ import annotations

from dataclasses import dataclass, replace

from source_scoped_action_restrictions import SourceScopedActionRestriction
from source_scoped_restriction_activation import RestrictionActivationProfile


_WAITING = "waiting"
_ACTIVE = "active"
_EXPIRED = "expired"


@dataclass(frozen=True)
class AttackRestrictionWindow:
    restriction: SourceScopedActionRestriction
    source_player: str
    other_player: str
    duration_family: str
    phase: str
    expiring_player: str | None = None

    def __post_init__(self) -> None:
        if not self.source_player or not self.other_player:
            raise ValueError("player identifiers must be non-empty")
        if self.source_player == self.other_player:
            raise ValueError("players must be distinct")
        if self.phase not in {_WAITING, _ACTIVE, _EXPIRED}:
            raise ValueError(f"unsupported phase: {self.phase!r}")
        if self.phase != _ACTIVE and self.expiring_player is not None:
            raise ValueError("only an active window can have an expiring player")
        if (
            self.expiring_player is not None
            and self.expiring_player
            not in {self.source_player, self.other_player}
        ):
            raise ValueError("expiring player is outside this match")


def create_attack_restriction_window(
    profile: RestrictionActivationProfile,
    restriction: SourceScopedActionRestriction,
    *,
    source_player: str,
    other_player: str,
) -> AttackRestrictionWindow:
    """Create temporal state after an attack has materialized a restriction."""

    if profile.activation_family != "attack_applied":
        raise ValueError("profile is not attack-applied")
    if restriction.exclusive_dimension_options:
        raise ValueError("restriction branch must be resolved before scheduling")
    if profile.duration_family == "opponent_next_turn":
        phase = _WAITING
    elif profile.duration_family == "until_end_of_own_next_turn":
        phase = _ACTIVE
    else:
        raise ValueError(
            f"unsupported attack duration: {profile.duration_family!r}"
        )
    return AttackRestrictionWindow(
        restriction=restriction,
        source_player=source_player,
        other_player=other_player,
        duration_family=profile.duration_family,
        phase=phase,
    )


def begin_turn(
    window: AttackRestrictionWindow,
    player: str,
) -> AttackRestrictionWindow:
    """Advance one pending restriction to the start of a concrete player's turn."""

    if player not in {window.source_player, window.other_player}:
        raise ValueError("unknown player")
    if window.phase == _EXPIRED:
        return window
    if window.expiring_player is not None:
        raise ValueError("previous active turn has not ended")

    if window.duration_family == "opponent_next_turn":
        if window.phase == _WAITING:
            if player == window.other_player:
                return replace(
                    window,
                    phase=_ACTIVE,
                    expiring_player=player,
                )
            return window
        raise ValueError("opponent-next-turn window is active without turn owner")

    if window.duration_family == "until_end_of_own_next_turn":
        return replace(
            window,
            phase=_ACTIVE,
            expiring_player=(
                player if player == window.source_player else None
            ),
        )

    raise ValueError(f"unsupported duration: {window.duration_family!r}")


def end_turn(
    window: AttackRestrictionWindow,
    player: str,
) -> AttackRestrictionWindow:
    """Advance one pending restriction past the end of a concrete player's turn."""

    if player not in {window.source_player, window.other_player}:
        raise ValueError("unknown player")
    if window.phase == _EXPIRED:
        return window
    if window.expiring_player == player:
        return replace(
            window,
            phase=_EXPIRED,
            expiring_player=None,
        )
    if window.expiring_player is not None:
        raise ValueError("turn ended for the wrong player")
    return window


def restriction_affects_player(
    window: AttackRestrictionWindow,
    player: str,
) -> bool:
    """Return whether the temporal restriction currently applies to this player."""

    if player not in {window.source_player, window.other_player}:
        raise ValueError("unknown player")
    if window.phase != _ACTIVE:
        return False
    scope = window.restriction.target_scope
    if scope == "both":
        return True
    if scope == "opponent":
        return player == window.other_player
    raise ValueError(f"unsupported target scope: {scope!r}")
