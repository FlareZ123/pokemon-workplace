"""Evaluate continuous source-scoped Ability restrictions from board context."""

from __future__ import annotations

from dataclasses import dataclass

from source_scoped_restriction_activation import RestrictionActivationProfile


@dataclass(frozen=True)
class ContinuousRestrictionContext:
    source_in_play: bool
    ability_enabled: bool
    source_active: bool = False
    tool_attached: bool = False
    stadium_in_play: bool = False
    player_pokemon_in_play: int | None = None
    opponent_pokemon_in_play: int | None = None

    def __post_init__(self) -> None:
        for value in (
            self.player_pokemon_in_play,
            self.opponent_pokemon_in_play,
        ):
            if value is not None and value < 0:
                raise ValueError("Pokemon counts must be non-negative")


def continuous_restriction_active(
    profile: RestrictionActivationProfile,
    context: ContinuousRestrictionContext,
) -> bool:
    """Return whether one continuous Ability restriction is currently active."""

    if profile.duration_family != "continuous":
        raise ValueError("profile is not a continuous restriction")
    if not profile.requires_source_in_play or not profile.requires_ability_enabled:
        raise ValueError("continuous profile has inconsistent requirements")
    if not context.source_in_play or not context.ability_enabled:
        return False

    family = profile.activation_family
    if family == "in_play":
        return True
    if family == "active_spot":
        return context.source_active
    if family == "tool_attached":
        return context.tool_attached
    if family == "stadium_required":
        return context.stadium_in_play
    if family == "relative_pokemon_count":
        if (
            context.player_pokemon_in_play is None
            or context.opponent_pokemon_in_play is None
        ):
            raise ValueError(
                "relative Pokemon-count restriction requires both counts"
            )
        return (
            context.player_pokemon_in_play
            < context.opponent_pokemon_in_play
        )
    raise ValueError(f"unsupported continuous activation family: {family!r}")
