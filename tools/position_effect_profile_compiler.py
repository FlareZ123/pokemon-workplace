"""Compile a conservative paper-Expanded Active/Bench movement semantic island.

The compiler recognizes complete Trainer effect bodies and complete attack-text
bodies whose only outside-damage instruction is one of the rulebook's three
position-change families: self switch, opponent-chosen forced switch, or
actor-chosen targeted gust. Historical English wording and the current
Pokemon Catcher erratum are normalized before semantic compilation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


class PositionEffectKind(str, Enum):
    SELF_SWITCH = "self_switch"
    OPPONENT_FORCED_SWITCH = "opponent_forced_switch"
    TARGETED_GUST = "targeted_gust"


class ChoiceAuthority(str, Enum):
    ACTOR = "actor"
    OPPONENT = "opponent"


class EffectTargetGeometry(str, Enum):
    ACTOR_ACTIVE = "actor_active"
    OPPONENT_ACTIVE = "opponent_active"
    SELECTED_OPPONENT_BENCH = "selected_opponent_bench"


@dataclass(frozen=True)
class PositionEffectProfile:
    card_id: str
    name: str
    source_kind: str
    action_class: str
    source_name: str | None
    kind: PositionEffectKind
    chooser: ChoiceAuthority
    effect_target: EffectTargetGeometry
    effect_text: str
    play_condition: str | None = None
    attack_cost: tuple[str, ...] = ()
    attack_damage: str | None = None
    coin_heads_required: bool = False
    optional: bool = False

    def __post_init__(self) -> None:
        if self.source_kind not in {"trainer", "attack"}:
            raise ValueError("unsupported source_kind")
        if self.source_kind == "attack" and not self.source_name:
            raise ValueError("attack profiles require source_name")
        if self.source_kind == "trainer" and self.source_name is not None:
            raise ValueError("Trainer profiles do not use source_name")


@dataclass(frozen=True)
class _Meaning:
    kind: PositionEffectKind
    chooser: ChoiceAuthority
    target: EffectTargetGeometry


_MEANINGS: dict[str, _Meaning] = {
    "Switch your Active Pokémon with 1 of your Benched Pokémon.": _Meaning(
        PositionEffectKind.SELF_SWITCH,
        ChoiceAuthority.ACTOR,
        EffectTargetGeometry.ACTOR_ACTIVE,
    ),
    "Switch this Pokémon with 1 of your Benched Pokémon.": _Meaning(
        PositionEffectKind.SELF_SWITCH,
        ChoiceAuthority.ACTOR,
        EffectTargetGeometry.ACTOR_ACTIVE,
    ),
    "Your opponent switches their Active Pokémon with 1 of their Benched Pokémon.": _Meaning(
        PositionEffectKind.OPPONENT_FORCED_SWITCH,
        ChoiceAuthority.OPPONENT,
        EffectTargetGeometry.OPPONENT_ACTIVE,
    ),
    "Your opponent switches his or her Active Pokémon with 1 of his or her Benched Pokémon.": _Meaning(
        PositionEffectKind.OPPONENT_FORCED_SWITCH,
        ChoiceAuthority.OPPONENT,
        EffectTargetGeometry.OPPONENT_ACTIVE,
    ),
    "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)": _Meaning(
        PositionEffectKind.OPPONENT_FORCED_SWITCH,
        ChoiceAuthority.OPPONENT,
        EffectTargetGeometry.OPPONENT_ACTIVE,
    ),
    "Switch 1 of your opponent's Benched Pokémon with their Active Pokémon.": _Meaning(
        PositionEffectKind.TARGETED_GUST,
        ChoiceAuthority.ACTOR,
        EffectTargetGeometry.SELECTED_OPPONENT_BENCH,
    ),
    "Switch 1 of your opponent's Benched Pokémon with his or her Active Pokémon.": _Meaning(
        PositionEffectKind.TARGETED_GUST,
        ChoiceAuthority.ACTOR,
        EffectTargetGeometry.SELECTED_OPPONENT_BENCH,
    ),
    "Switch in 1 of your opponent's Benched Pokémon to the Active Spot.": _Meaning(
        PositionEffectKind.TARGETED_GUST,
        ChoiceAuthority.ACTOR,
        EffectTargetGeometry.SELECTED_OPPONENT_BENCH,
    ),
}

_COIN_HEADS_PREFIX = "Flip a coin. If heads, "
_OPTIONAL_SELF_SWITCH = "You may switch this Pokémon with 1 of your Benched Pokémon."
_GX_SELF_SWITCH = (
    "Switch this Pokémon with 1 of your Benched Pokémon. "
    "(You can't use more than 1 GX attack in a game.)"
)
_POKEMON_CATCHER_STALE = (
    "Switch your opponent's Active Pokémon with 1 of his or her Benched Pokémon."
)
_POKEMON_CATCHER_CURRENT = (
    "Flip a coin. If heads, switch 1 of your opponent's Benched Pokémon "
    "with his or her Active Pokémon."
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _current_rules(card: dict[str, Any]) -> tuple[str, ...]:
    """Apply the movement-relevant current-text erratum before compilation."""

    rules = tuple(_normalized(rule) for rule in (card.get("rules") or ()))
    if card.get("name") != "Pokémon Catcher":
        return rules
    return tuple(
        _POKEMON_CATCHER_CURRENT if rule == _POKEMON_CATCHER_STALE else rule
        for rule in rules
    )


def _parse_movement(text: str) -> tuple[_Meaning, bool, bool] | None:
    normalized = _normalized(text)

    if normalized == _OPTIONAL_SELF_SWITCH:
        return (
            _MEANINGS["Switch this Pokémon with 1 of your Benched Pokémon."],
            False,
            True,
        )
    if normalized == _GX_SELF_SWITCH:
        return (
            _MEANINGS["Switch this Pokémon with 1 of your Benched Pokémon."],
            False,
            False,
        )

    direct = _MEANINGS.get(normalized)
    if direct is not None:
        return direct, False, False

    if not normalized.startswith(_COIN_HEADS_PREFIX):
        return None
    body = normalized[len(_COIN_HEADS_PREFIX):]
    if not body:
        return None
    canonical_body = body[0].upper() + body[1:]
    gated = _MEANINGS.get(canonical_body)
    return None if gated is None else (gated, True, False)


def _legal_expanded_cards(resources_root: Path) -> tuple[dict[str, Any], ...]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if classify_effective_legality(card)[0] == "Legal":
                rows.append(card)
    return tuple(rows)


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


def _is_simple_play_condition(rule: str) -> bool:
    return rule.casefold().startswith(
        ("you can use this card only", "you can play this card only")
    )


def _trainer_profile(card: dict[str, Any]) -> PositionEffectProfile | None:
    action_class = _trainer_action_class(card)
    if action_class is None:
        return None

    rules = _current_rules(card)
    matched = tuple(
        (rule, parsed)
        for rule in rules
        if (parsed := _parse_movement(rule)) is not None
    )
    if len(matched) != 1:
        return None

    effect_text, (meaning, coin_heads_required, optional) = matched[0]
    other = tuple(
        rule
        for rule in rules
        if rule != effect_text and not _is_reminder_rule(rule)
    )
    if len(other) > 1 or any(not _is_simple_play_condition(rule) for rule in other):
        return None

    return PositionEffectProfile(
        card_id=card["id"],
        name=card["name"],
        source_kind="trainer",
        action_class=action_class,
        source_name=None,
        kind=meaning.kind,
        chooser=meaning.chooser,
        effect_target=meaning.target,
        effect_text=effect_text,
        play_condition=other[0] if other else None,
        coin_heads_required=coin_heads_required,
        optional=optional,
    )


def _attack_profiles(card: dict[str, Any]) -> tuple[PositionEffectProfile, ...]:
    if card.get("supertype") != "Pokémon":
        return ()

    profiles: list[PositionEffectProfile] = []
    for attack in card.get("attacks") or ():
        effect_text = _normalized(attack.get("text") or "")
        parsed = _parse_movement(effect_text)
        if parsed is None:
            continue
        meaning, coin_heads_required, optional = parsed
        profiles.append(
            PositionEffectProfile(
                card_id=card["id"],
                name=card["name"],
                source_kind="attack",
                action_class="Attack",
                source_name=attack["name"],
                kind=meaning.kind,
                chooser=meaning.chooser,
                effect_target=meaning.target,
                effect_text=effect_text,
                attack_cost=tuple(attack.get("cost") or ()),
                attack_damage=attack.get("damage"),
                coin_heads_required=coin_heads_required,
                optional=optional,
            )
        )
    return tuple(profiles)


def compile_position_effect_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[PositionEffectProfile, ...]:
    profiles: list[PositionEffectProfile] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") == "Trainer":
            profile = _trainer_profile(card)
            if profile is not None:
                profiles.append(profile)
        profiles.extend(_attack_profiles(card))

    return tuple(
        sorted(
            profiles,
            key=lambda row: (
                row.kind.value,
                row.name,
                row.card_id,
                row.source_kind,
                row.source_name or "",
            ),
        )
    )
