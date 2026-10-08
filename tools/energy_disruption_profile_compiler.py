"""Compile a conservative one-card opponent Energy-discard semantic island."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


class EnergyRestriction(str, Enum):
    ANY = "any_energy"
    SPECIAL = "special_energy"


class OpponentTargetScope(str, Enum):
    ACTIVE = "active"
    SELECTED_POKEMON = "selected_pokemon"


@dataclass(frozen=True)
class EnergyDisruptionProfile:
    card_id: str
    name: str
    source_kind: str
    action_class: str
    source_name: str | None
    energy_restriction: EnergyRestriction
    target_scope: OpponentTargetScope
    coin_heads_required: bool
    effect_text: str
    attack_cost: tuple[str, ...] = ()
    attack_damage: str | None = None
    attack_index: int | None = None

    def __post_init__(self) -> None:
        if self.source_kind not in {"trainer", "attack"}:
            raise ValueError("unsupported source_kind")
        if self.source_kind == "attack" and not self.source_name:
            raise ValueError("attack profile requires source_name")
        if self.source_kind == "attack" and self.attack_index is None:
            raise ValueError("attack profile requires attack_index")
        if self.source_kind == "trainer" and self.source_name is not None:
            raise ValueError("Trainer profile cannot have source_name")
        if self.source_kind == "trainer" and self.attack_index is not None:
            raise ValueError("Trainer profile cannot have attack_index")


_COIN_PREFIX = "Flip a coin. If heads, "

_BODY_MAP = {
    "Discard an Energy from your opponent's Active Pokémon.": (
        EnergyRestriction.ANY,
        OpponentTargetScope.ACTIVE,
    ),
    "Discard an Energy attached to your opponent's Active Pokémon.": (
        EnergyRestriction.ANY,
        OpponentTargetScope.ACTIVE,
    ),
    "Discard an Energy from 1 of your opponent's Pokémon.": (
        EnergyRestriction.ANY,
        OpponentTargetScope.SELECTED_POKEMON,
    ),
    "Discard an Energy attached to 1 of your opponent's Pokémon.": (
        EnergyRestriction.ANY,
        OpponentTargetScope.SELECTED_POKEMON,
    ),
    "Discard a Special Energy from your opponent's Active Pokémon.": (
        EnergyRestriction.SPECIAL,
        OpponentTargetScope.ACTIVE,
    ),
    "Discard a Special Energy attached to your opponent's Active Pokémon.": (
        EnergyRestriction.SPECIAL,
        OpponentTargetScope.ACTIVE,
    ),
    "Discard a Special Energy from 1 of your opponent's Pokémon.": (
        EnergyRestriction.SPECIAL,
        OpponentTargetScope.SELECTED_POKEMON,
    ),
    "Discard a Special Energy attached to 1 of your opponent's Pokémon.": (
        EnergyRestriction.SPECIAL,
        OpponentTargetScope.SELECTED_POKEMON,
    ),
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _legal_expanded_cards(resources_root: Path) -> tuple[dict[str, Any], ...]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if classify_effective_legality(card)[0] == "Legal":
                cards.append(card)
    return tuple(cards)


def _parse(text: str) -> tuple[EnergyRestriction, OpponentTargetScope, bool] | None:
    normalized = _normalized(text)
    direct = _BODY_MAP.get(normalized)
    if direct is not None:
        return direct[0], direct[1], False
    if normalized.startswith(_COIN_PREFIX):
        body = normalized[len(_COIN_PREFIX):]
        if body:
            body = body[0].upper() + body[1:]
        gated = _BODY_MAP.get(body)
        if gated is not None:
            return gated[0], gated[1], True
    return None


def parse_exact_attack_energy_disruption_text(
    text: str,
) -> tuple[EnergyRestriction, OpponentTargetScope, bool] | None:
    """Parse one complete attack body in the supported one-Energy family."""

    return _parse(text)


def _trainer_action_class(card: dict[str, Any]) -> str | None:
    subtypes = tuple(card.get("subtypes") or ())
    for candidate in ("Item", "Supporter", "Stadium", "Pokémon Tool"):
        if candidate in subtypes:
            return candidate
    return None


def _is_reminder_rule(rule: str) -> bool:
    lower = rule.casefold()
    return (
        lower.startswith("you may play any number of item cards")
        or lower.startswith("you may play as many item cards as you like")
        or lower.startswith("you may play only 1 supporter card")
        or lower.startswith("ace spec:")
    )


def _trainer_profile(card: dict[str, Any]) -> EnergyDisruptionProfile | None:
    action_class = _trainer_action_class(card)
    if action_class is None:
        return None
    rules = tuple(_normalized(rule) for rule in (card.get("rules") or ()))
    matches = tuple(
        (rule, parsed)
        for rule in rules
        if (parsed := _parse(rule)) is not None
    )
    if len(matches) != 1:
        return None
    effect_text, (restriction, target_scope, coin) = matches[0]
    other = tuple(
        rule
        for rule in rules
        if rule != effect_text and not _is_reminder_rule(rule)
    )
    if other:
        return None
    return EnergyDisruptionProfile(
        card_id=card["id"],
        name=card["name"],
        source_kind="trainer",
        action_class=action_class,
        source_name=None,
        energy_restriction=restriction,
        target_scope=target_scope,
        coin_heads_required=coin,
        effect_text=effect_text,
    )


def _attack_profiles(card: dict[str, Any]) -> tuple[EnergyDisruptionProfile, ...]:
    if card.get("supertype") != "Pokémon":
        return ()
    rows: list[EnergyDisruptionProfile] = []
    for attack_index, attack in enumerate(card.get("attacks") or ()):
        text = _normalized(attack.get("text") or "")
        parsed = _parse(text)
        if parsed is None:
            continue
        restriction, target_scope, coin = parsed
        rows.append(EnergyDisruptionProfile(
            card_id=card["id"],
            name=card["name"],
            source_kind="attack",
            action_class="Attack",
            source_name=attack["name"],
            energy_restriction=restriction,
            target_scope=target_scope,
            coin_heads_required=coin,
            effect_text=text,
            attack_cost=tuple(attack.get("cost") or ()),
            attack_damage=attack.get("damage"),
            attack_index=attack_index,
        ))
    return tuple(rows)


def compile_energy_disruption_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[EnergyDisruptionProfile, ...]:
    rows: list[EnergyDisruptionProfile] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") == "Trainer":
            profile = _trainer_profile(card)
            if profile is not None:
                rows.append(profile)
        rows.extend(_attack_profiles(card))
    return tuple(sorted(
        rows,
        key=lambda row: (
            row.energy_restriction.value,
            row.target_scope.value,
            row.coin_heads_required,
            row.source_kind,
            row.name,
            row.card_id,
            row.source_name or "",
        ),
    ))
