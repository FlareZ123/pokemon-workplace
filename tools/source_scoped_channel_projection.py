"""Project source-scoped hand restrictions into coarse PlayerChannels safely."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from lock_state_kernel import PlayerChannels, apply_play_lock
from source_scoped_action_restrictions import (
    CardActionAttempt,
    SourceScopedActionRestriction,
    restrictions_block_attempt,
)


RICH_DIMENSIONS = frozenset(
    {"ace_spec", "ability_pokemon_play", "evolution", "energy_attach_to_target"}
)
CHANNEL_DIMENSION_MAP = {
    "all_cards_from_hand": ("all_cards_from_hand",),
    "trainer": ("trainer",),
    "item": ("item",),
    "tool": ("tool",),
    "tool_attach": ("tool",),
    "supporter": ("supporter",),
    "stadium": ("stadium",),
    "special_energy_play": ("special_energy_play",),
    "special_energy_attach": ("special_energy_play",),
}


@dataclass(frozen=True)
class SourceScopedPermissionProjection:
    channels: PlayerChannels
    exact_restrictions: tuple[SourceScopedActionRestriction, ...]
    residual_restrictions: tuple[SourceScopedActionRestriction, ...]
    restrictions: tuple[SourceScopedActionRestriction, ...]


def projection_reasons(
    restriction: SourceScopedActionRestriction,
) -> tuple[str, ...]:
    reasons: set[str] = set()
    if restriction.prohibited_source_zone != "hand":
        reasons.add("source_zone")
    if restriction.exclusive_dimension_options:
        reasons.add("exclusive_choice")
    reasons.update(restriction.dimensions & RICH_DIMENSIONS)
    if restriction.required_target_relation is not None:
        reasons.add("target_relation")
    if restriction.excluded_card_tags:
        reasons.add("card_exception")
    unknown = restriction.dimensions - set(CHANNEL_DIMENSION_MAP) - RICH_DIMENSIONS
    if unknown:
        reasons.update(f"unknown_dimension:{row}" for row in unknown)
    return tuple(sorted(reasons))


def project_source_scoped_permissions(
    restrictions: Iterable[SourceScopedActionRestriction],
    *,
    base_channels: PlayerChannels | None = None,
) -> SourceScopedPermissionProjection:
    rows = tuple(restrictions)
    channels = base_channels if base_channels is not None else PlayerChannels()
    exact: list[SourceScopedActionRestriction] = []
    residual: list[SourceScopedActionRestriction] = []

    for restriction in rows:
        if projection_reasons(restriction):
            residual.append(restriction)
            continue
        exact.append(restriction)
        for dimension in sorted(restriction.dimensions):
            for channel_dimension in CHANNEL_DIMENSION_MAP[dimension]:
                channels = apply_play_lock(channels, channel_dimension)

    return SourceScopedPermissionProjection(
        channels=channels,
        exact_restrictions=tuple(exact),
        residual_restrictions=tuple(residual),
        restrictions=rows,
    )


def channel_allows_hand_attempt(
    channels: PlayerChannels,
    attempt: CardActionAttempt,
) -> bool:
    if attempt.source_zone != "hand":
        raise ValueError("coarse PlayerChannels only project hand-sourced actions")
    if attempt.card_kind == "item":
        return channels.item_play
    if attempt.card_kind == "tool":
        return channels.tool_play
    if attempt.card_kind == "supporter":
        return channels.supporter_play
    if attempt.card_kind == "stadium":
        return channels.stadium_play
    if attempt.card_kind == "pokemon":
        return channels.pokemon_play
    if attempt.card_kind == "basic_energy":
        return channels.basic_energy_play
    if attempt.card_kind == "special_energy":
        return channels.special_energy_play
    raise ValueError(f"unsupported card kind: {attempt.card_kind!r}")


def action_allowed(
    projection: SourceScopedPermissionProjection,
    attempt: CardActionAttempt,
) -> bool:
    """Evaluate one action while using channels only where the projection is exact."""

    if attempt.source_zone == "hand":
        if not channel_allows_hand_attempt(projection.channels, attempt):
            return False
        return not restrictions_block_attempt(
            projection.residual_restrictions,
            attempt,
        )
    return not restrictions_block_attempt(projection.restrictions, attempt)
