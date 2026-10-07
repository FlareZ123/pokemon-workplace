"""Compile and execute a conservative literal healing-text semantic island."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any

from board_position_state import BoardState, replace_pokemon
from build_expanded_legality_baseline import classify_effective_legality


class HealingTarget(str, Enum):
    SOURCE_POKEMON = "source_pokemon"
    SELECTED_OWN_POKEMON = "selected_own_pokemon"


@dataclass(frozen=True)
class HealingProfile:
    card_id: str
    name: str
    source_kind: str
    action_class: str
    source_name: str | None
    target: HealingTarget
    heal_damage: int
    effect_text: str
    attack_cost: tuple[str, ...] = ()
    attack_damage: str | None = None

    def __post_init__(self) -> None:
        if self.source_kind not in {"trainer", "attack"}:
            raise ValueError("unsupported source_kind")
        if self.heal_damage <= 0 or self.heal_damage % 10:
            raise ValueError("heal_damage must be a positive multiple of 10")
        if self.source_kind == "attack" and not self.source_name:
            raise ValueError("attack profile requires source_name")
        if self.source_kind == "trainer" and self.source_name is not None:
            raise ValueError("Trainer profile cannot have source_name")


_HEAL_SELF = re.compile(r"^Heal (\d+) damage from this Pokémon\.$")
_HEAL_SELECTED = re.compile(r"^Heal (\d+) damage from 1 of your Pokémon\.$")


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


def _parse_healing(text: str) -> tuple[HealingTarget, int] | None:
    normalized = _normalized(text)
    match = _HEAL_SELF.fullmatch(normalized)
    if match is not None:
        return HealingTarget.SOURCE_POKEMON, int(match.group(1))
    match = _HEAL_SELECTED.fullmatch(normalized)
    if match is not None:
        return HealingTarget.SELECTED_OWN_POKEMON, int(match.group(1))
    return None


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


def _trainer_profile(card: dict[str, Any]) -> HealingProfile | None:
    action_class = _trainer_action_class(card)
    if action_class is None:
        return None

    rules = tuple(_normalized(rule) for rule in (card.get("rules") or ()))
    matches = tuple(
        (rule, parsed)
        for rule in rules
        if (parsed := _parse_healing(rule)) is not None
    )
    if len(matches) != 1:
        return None
    effect_text, (target, amount) = matches[0]
    if target != HealingTarget.SELECTED_OWN_POKEMON:
        return None

    other = tuple(
        rule
        for rule in rules
        if rule != effect_text and not _is_reminder_rule(rule)
    )
    if other:
        return None

    return HealingProfile(
        card_id=card["id"],
        name=card["name"],
        source_kind="trainer",
        action_class=action_class,
        source_name=None,
        target=target,
        heal_damage=amount,
        effect_text=effect_text,
    )


def _attack_profiles(card: dict[str, Any]) -> tuple[HealingProfile, ...]:
    if card.get("supertype") != "Pokémon":
        return ()

    rows: list[HealingProfile] = []
    for attack in card.get("attacks") or ():
        effect_text = _normalized(attack.get("text") or "")
        parsed = _parse_healing(effect_text)
        if parsed is None:
            continue
        target, amount = parsed
        if target != HealingTarget.SOURCE_POKEMON:
            continue
        rows.append(
            HealingProfile(
                card_id=card["id"],
                name=card["name"],
                source_kind="attack",
                action_class="Attack",
                source_name=attack["name"],
                target=target,
                heal_damage=amount,
                effect_text=effect_text,
                attack_cost=tuple(attack.get("cost") or ()),
                attack_damage=attack.get("damage"),
            )
        )
    return tuple(rows)


def compile_healing_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[HealingProfile, ...]:
    rows: list[HealingProfile] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") == "Trainer":
            profile = _trainer_profile(card)
            if profile is not None:
                rows.append(profile)
        rows.extend(_attack_profiles(card))
    return tuple(sorted(
        rows,
        key=lambda row: (
            row.source_kind,
            row.name,
            row.card_id,
            row.source_name or "",
        ),
    ))


def apply_healing_profile(
    profile: HealingProfile,
    state: BoardState,
    *,
    source_pokemon_id: str | None = None,
    selected_pokemon_id: str | None = None,
) -> BoardState | None:
    """Apply only the compiled healing effect to one board state."""

    if profile.target == HealingTarget.SOURCE_POKEMON:
        if source_pokemon_id is None or selected_pokemon_id is not None:
            raise ValueError("source healing requires exactly source_pokemon_id")
        target_id = source_pokemon_id
    else:
        if selected_pokemon_id is None or source_pokemon_id is not None:
            raise ValueError("selected healing requires exactly selected_pokemon_id")
        target_id = selected_pokemon_id

    try:
        pokemon = state.get(target_id)
    except StopIteration:
        return None

    if profile.source_kind == "trainer" and pokemon.damage_counters == 0:
        return None

    remove_counters = profile.heal_damage // 10
    updated = replace(
        pokemon,
        damage_counters=max(0, pokemon.damage_counters - remove_counters),
    )
    return replace_pokemon(state, updated)
