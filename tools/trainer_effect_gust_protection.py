"""Conservative effect-protection gates for Trainer-sourced Bench gusts.

Each source profile is a manually audited English print. The source board
must already encode whether an Ability/Tool actually remains enabled.
"""
from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardState
from committed_play_event import PlayKind


@dataclass(frozen=True)
class TrainerEffectOrigin:
    kind: PlayKind
    played_from_hand: bool


@dataclass(frozen=True)
class ProtectionProfile:
    print_id: str
    source_name: str
    label: str
    kinds: frozenset[PlayKind]
    target_scope: str
    provider_active: bool


@dataclass(frozen=True)
class ProtectionResult:
    target_id: str
    allowed: bool
    protectors: tuple[str, ...]


PROFILES = {
    "bw8-104": ProtectionProfile(
        "bw8-104", "Togekiss", "Bright Veil",
        frozenset({PlayKind.ITEM}), "all", True,
    ),
    "swsh10-68": ProtectionProfile(
        "swsh10-68", "Diancie", "Princess's Curtain",
        frozenset({PlayKind.SUPPORTER}), "benched_basic", True,
    ),
    "sm11-154": ProtectionProfile(
        "sm11-154", "Axew", "Unnerve",
        frozenset({PlayKind.ITEM, PlayKind.SUPPORTER}), "self", False,
    ),
    "sm9-32": ProtectionProfile(
        "sm9-32", "Articuno", "Blizzard Veil",
        frozenset({PlayKind.SUPPORTER}), "benched_water", True,
    ),
    "sv10-65": ProtectionProfile(
        "sv10-65", "Cetitan ex", "Snow Camouflage",
        frozenset({PlayKind.ITEM, PlayKind.SUPPORTER}), "self", False,
    ),
    "sv7-76": ProtectionProfile(
        "sv7-76", "Rhyperior", "Wide Wall",
        frozenset({PlayKind.SUPPORTER}), "all", True,
    ),
}


def _matches(
    scope: str,
    *,
    source_id: str,
    target_id: str,
    target_tags: frozenset[str],
) -> bool:
    if scope == "self":
        return source_id == target_id
    if scope == "all":
        return True
    if scope == "benched_basic":
        return "Basic" in target_tags
    if scope == "benched_water":
        return "Water" in target_tags
    raise ValueError(f"unsupported audited target scope {scope!r}")


def evaluate_bench_gust_protection(
    defending_board: BoardState,
    target_id: str,
    effect: TrainerEffectOrigin,
) -> ProtectionResult | None:
    """Return only target effect eligibility, not Trainer source-play legality.

    None means there is no opposing Bench object with this target ID.
    """
    defending_board.validate()
    if target_id not in defending_board.bench_ids:
        return None
    if not effect.played_from_hand:
        return ProtectionResult(target_id, True, ())

    target = defending_board.get(target_id)
    sources: list[str] = []
    for provider in defending_board.objects:
        profile = PROFILES.get(provider.print_id or "")
        if (
            profile is None
            or profile.source_name != provider.card_name
            or not provider.abilities_enabled
            or effect.kind not in profile.kinds
            or (profile.provider_active and provider.object_id != defending_board.active_id)
        ):
            continue
        if _matches(
            profile.target_scope, source_id=provider.object_id,
            target_id=target_id, target_tags=target.tags,
        ):
            sources.append(f"{provider.object_id}:{profile.label}")

    tool = target.tool
    if (
        tool is not None
        and tool.card_name == "Leafy Camo Poncho"
        and tool.print_id in {"swsh12-160", "swsh12-214"}
        and target.pokemon_state.tool_effect_enabled
        and effect.kind is PlayKind.SUPPORTER
        and bool(target.tags & {"VSTAR", "VMAX"})
    ):
        sources.append(f"{target_id}:Leafy Camo Poncho")

    return ProtectionResult(target_id, not sources, tuple(sorted(sources)))
