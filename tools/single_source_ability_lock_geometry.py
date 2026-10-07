"""Single-source continuous Ability-lock geometry over physical boards.

This layer deliberately evaluates one continuous Ability-lock source at a time.
That avoids pretending that mutually suppressing sources have already been
given a general fixed-point or ordering semantics.
"""

from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardPokemon, BoardState
from garbotoxin_suppression import (
    GARBOTOXIN_PRINT_IDS,
    stealthy_hood_protects_from_opponent,
)


@dataclass(frozen=True)
class AbilityLockProfile:
    name: str
    print_ids: frozenset[str]
    activation: str
    scope: str
    required_target_tags: frozenset[str] = frozenset()
    excluded_target_tags: frozenset[str] = frozenset()
    target_position: str = "any"
    exempt_print_ids: frozenset[str] = frozenset()
    requires_damage_counters: bool = False


POWER_OF_ALCHEMY = AbilityLockProfile(
    name="Power of Alchemy",
    print_ids=frozenset({"sm1-58"}),
    activation="in_play",
    scope="both",
    required_target_tags=frozenset({"Basic"}),
)

BIDE_BARRICADE = AbilityLockProfile(
    name="Bide Barricade",
    print_ids=frozenset({"xy4-36", "g1-RC11"}),
    activation="active",
    scope="both",
    excluded_target_tags=frozenset({"Psychic"}),
)

EMPERORS_EYES = AbilityLockProfile(
    name="Emperor's Eyes",
    print_ids=frozenset({"swsh5-40", "swsh5-145", "swsh5-146", "swshp-SWSH108"}),
    activation="active",
    scope="opponent",
    required_target_tags=frozenset({"Basic"}),
    excluded_target_tags=frozenset({"RuleBox"}),
)

NEUTRALIZING_GAS = AbilityLockProfile(
    name="Neutralizing Gas",
    print_ids=frozenset({"swsh2-113", "swsh45-42", "swsh45sv-SV077"}),
    activation="active",
    scope="opponent",
)

LAZY = AbilityLockProfile(
    name="Lazy",
    print_ids=frozenset({"sm7-115"}),
    activation="active",
    scope="opponent",
)

CURSED_LAND = AbilityLockProfile(
    name="Cursed Land",
    print_ids=frozenset({"sv2-127", "sv2-243", "sv2-263", "sv2-275", "sv4pt5-244"}),
    activation="active",
    scope="opponent",
    excluded_target_tags=frozenset({"ex"}),
    requires_damage_counters=True,
)

STICKY_BIND = AbilityLockProfile(
    name="Sticky Bind",
    print_ids=frozenset({"sv8-107"}),
    activation="bench",
    scope="both",
    required_target_tags=frozenset({"Stage2"}),
    target_position="bench",
)

GARBOTOXIN = AbilityLockProfile(
    name="Garbotoxin",
    print_ids=GARBOTOXIN_PRINT_IDS,
    activation="tool_attached",
    scope="both",
    exempt_print_ids=GARBOTOXIN_PRINT_IDS,
)

PROFILES = (
    POWER_OF_ALCHEMY,
    BIDE_BARRICADE,
    EMPERORS_EYES,
    NEUTRALIZING_GAS,
    LAZY,
    CURSED_LAND,
    STICKY_BIND,
    GARBOTOXIN,
)

_PROFILE_BY_PRINT = {
    print_id: profile
    for profile in PROFILES
    for print_id in profile.print_ids
}


def profile_for_source(source: BoardPokemon) -> AbilityLockProfile | None:
    if source.print_id is None:
        return None
    return _PROFILE_BY_PRINT.get(source.print_id)


def source_profile_active(
    profile: AbilityLockProfile,
    source: BoardPokemon,
    source_board: BoardState,
) -> bool:
    """Return whether this source's positional/attachment condition is live."""

    if not source.abilities_enabled:
        return False
    if profile.activation == "in_play":
        return True
    if profile.activation == "active":
        return source_board.active_id == source.object_id
    if profile.activation == "bench":
        return source.object_id in source_board.bench_ids
    if profile.activation == "tool_attached":
        return source.tool is not None
    raise ValueError(f"unsupported activation geometry: {profile.activation}")


def _target_position_matches(
    profile: AbilityLockProfile,
    target: BoardPokemon,
    target_board: BoardState,
) -> bool:
    if profile.target_position == "any":
        return True
    if profile.target_position == "active":
        return target_board.active_id == target.object_id
    if profile.target_position == "bench":
        return target.object_id in target_board.bench_ids
    raise ValueError(f"unsupported target position: {profile.target_position}")


def single_source_suppressed_object_ids(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    source_owner: str,
    source_object_id: str,
    stadium_name: str | None = None,
) -> frozenset[str]:
    """Return player-board objects suppressed by one verified live source."""

    if source_owner not in {"player", "opponent"}:
        raise ValueError("source_owner must be 'player' or 'opponent'")

    source_board = player_board if source_owner == "player" else opponent_board
    source = source_board.get(source_object_id)
    profile = profile_for_source(source)
    if profile is None or not source_profile_active(profile, source, source_board):
        return frozenset()

    source_is_opponent = source_owner == "opponent"
    if profile.scope == "opponent" and not source_is_opponent:
        return frozenset()
    if profile.scope not in {"opponent", "both"}:
        raise ValueError(f"unsupported target scope: {profile.scope}")

    suppressed: set[str] = set()
    for target in player_board.objects:
        if target.print_id in profile.exempt_print_ids:
            continue
        if not profile.required_target_tags.issubset(target.tags):
            continue
        if profile.excluded_target_tags & target.tags:
            continue
        if profile.requires_damage_counters and target.damage_counters == 0:
            continue
        if not _target_position_matches(profile, target, player_board):
            continue

        if (
            source_is_opponent
            and stealthy_hood_protects_from_opponent(
                target,
                stadium_name=stadium_name,
            )
        ):
            continue
        suppressed.add(target.object_id)

    return frozenset(suppressed)
