"""Compile activation and duration geometry for source-scoped restrictions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality, load_json
from source_scoped_action_restrictions import (
    SourceScopedActionRestriction,
    build_source_scoped_action_restrictions,
)


@dataclass(frozen=True)
class RestrictionActivationProfile:
    restriction: SourceScopedActionRestriction
    activation_family: str
    duration_family: str
    application_gate: str
    requires_source_in_play: bool
    requires_ability_enabled: bool


_ACTIVE_RE = re.compile(
    r"as long as this Pok[eé]mon is (?:your )?Active Pok[eé]mon|"
    r"as long as this Pok[eé]mon is in the Active Spot|"
    r"if this Pok[eé]mon is your Active Pok[eé]mon",
    flags=re.IGNORECASE,
)
_TOOL_ATTACHED_RE = re.compile(
    r"if this Pok[eé]mon has (?:a Pok[eé]mon Tool(?: card)?|a Memory Capsule) attached",
    flags=re.IGNORECASE,
)
_STADIUM_REQUIRED_RE = re.compile(
    r"if you have a Stadium card in play",
    flags=re.IGNORECASE,
)
_FEWER_POKEMON_RE = re.compile(
    r"as long as you have fewer Pok[eé]mon in play than your opponent",
    flags=re.IGNORECASE,
)


def _card_index(resources_root: Path) -> dict[str, dict]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    rows: dict[str, dict] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if classify_effective_legality(card)[0] != "Legal":
                continue
            rows[card["id"]] = card
    return rows


def _ability_activation(text: str) -> str:
    if _ACTIVE_RE.search(text):
        return "active_spot"
    if _TOOL_ATTACHED_RE.search(text):
        return "tool_attached"
    if _STADIUM_REQUIRED_RE.search(text):
        return "stadium_required"
    if _FEWER_POKEMON_RE.search(text):
        return "relative_pokemon_count"
    return "in_play"


def _attack_duration(text: str) -> str:
    lowered = text.lower()
    if "until the end of your next turn" in lowered:
        return "until_end_of_own_next_turn"
    if (
        "during your opponent's next turn" in lowered
        or "during his or her next turn" in lowered
        or "during their next turn" in lowered
    ):
        return "opponent_next_turn"
    raise ValueError(f"unparsed attack lock duration: {text!r}")


def _attack_application_gate(
    restriction: SourceScopedActionRestriction,
) -> str:
    text = restriction.text.lower()
    if restriction.exclusive_dimension_options:
        return "coin_branch" if "flip a coin" in text else "player_choice"
    if "flip a coin. if heads" in text:
        return "coin_heads"
    if "if your opponent has a stadium in play, discard it. if you do" in text:
        return "stadium_discard_if_you_do"
    return "unconditional"


def build_restriction_activation_profiles(
    resources_root: Path,
) -> tuple[RestrictionActivationProfile, ...]:
    restrictions = build_source_scoped_action_restrictions(resources_root)
    cards = _card_index(resources_root)
    profiles: list[RestrictionActivationProfile] = []
    for restriction in restrictions:
        source_kind = restriction.source.split(":", 1)[0]
        if source_kind == "attack":
            profiles.append(
                RestrictionActivationProfile(
                    restriction=restriction,
                    activation_family="attack_applied",
                    duration_family=_attack_duration(restriction.text),
                    application_gate=_attack_application_gate(restriction),
                    requires_source_in_play=False,
                    requires_ability_enabled=False,
                )
            )
            continue
        if source_kind != "ability":
            raise ValueError(
                f"unsupported restriction source kind: {source_kind!r}"
            )
        if restriction.card_id not in cards:
            raise ValueError(f"missing legal source card: {restriction.card_id}")
        profiles.append(
            RestrictionActivationProfile(
                restriction=restriction,
                activation_family=_ability_activation(restriction.text),
                duration_family="continuous",
                application_gate="continuous_condition",
                requires_source_in_play=True,
                requires_ability_enabled=True,
            )
        )
    return tuple(profiles)
