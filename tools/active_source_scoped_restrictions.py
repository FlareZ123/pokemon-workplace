"""Aggregate continuous and temporal source-scoped restrictions by player."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from attack_restriction_turn_windows import (
    AttackRestrictionWindow,
    restriction_affects_player,
)
from continuous_source_scoped_restrictions import (
    ContinuousRestrictionContext,
    continuous_restriction_active,
)
from source_scoped_action_restrictions import SourceScopedActionRestriction
from source_scoped_restriction_activation import RestrictionActivationProfile


@dataclass(frozen=True)
class ContinuousRestrictionSource:
    profile: RestrictionActivationProfile
    context: ContinuousRestrictionContext
    source_player: str
    other_player: str

    def __post_init__(self) -> None:
        if not self.source_player or not self.other_player:
            raise ValueError("player identifiers must be non-empty")
        if self.source_player == self.other_player:
            raise ValueError("players must be distinct")
        if self.profile.duration_family != "continuous":
            raise ValueError("source profile is not continuous")


def _continuous_affects_player(
    source: ContinuousRestrictionSource,
    player: str,
) -> bool:
    if player not in {source.source_player, source.other_player}:
        raise ValueError("unknown player")
    if not continuous_restriction_active(source.profile, source.context):
        return False
    scope = source.profile.restriction.target_scope
    if scope == "both":
        return True
    if scope == "opponent":
        return player == source.other_player
    raise ValueError(f"unsupported target scope: {scope!r}")


def active_restrictions_for_player(
    player: str,
    *,
    continuous_sources: Sequence[ContinuousRestrictionSource] = (),
    attack_windows: Sequence[AttackRestrictionWindow] = (),
) -> tuple[SourceScopedActionRestriction, ...]:
    """Return unique active restrictions currently affecting one player."""

    active: list[SourceScopedActionRestriction] = []
    for source in continuous_sources:
        if _continuous_affects_player(source, player):
            active.append(source.profile.restriction)
    for window in attack_windows:
        if restriction_affects_player(window, player):
            active.append(window.restriction)

    return tuple(dict.fromkeys(active))
