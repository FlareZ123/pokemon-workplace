"""Compile direct source-scoped card-action prohibitions in paper Expanded.

The represented family is deliberately conservative. It covers literal card text
that prevents playing or attaching specified card classes from hand. Callers
supply only restrictions that are currently active; this module answers whether
a concrete attempted card action falls under the restriction's source, selector,
and target scope.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
from typing import Iterable

from build_expanded_legality_baseline import classify_effective_legality


PLAY_LOCK_RE = re.compile(
    r"\bcan't play any (?P<categories>[^.]{1,160}?) from "
    r"(?:their|his or her|your) hand\b",
    flags=re.IGNORECASE,
)
CHOSEN_TRAINER_LOCK_RE = re.compile(
    r"Choose Item cards or Supporter cards\.[^.]*can't play any of the chosen "
    r"cards from their hand",
    flags=re.IGNORECASE,
)
ALLERGY_STORM_RE = re.compile(
    r"Flip a coin\. If heads,.*?can't play any Supporter cards from their hand\. "
    r"If tails,.*?can't play any Item cards from their hand",
    flags=re.IGNORECASE,
)
SPECIAL_ENERGY_ATTACH_RE = re.compile(
    r"\bcan't attach any Special Energy cards? from "
    r"(?:their|his or her|your) hand\b",
    flags=re.IGNORECASE,
)
ENERGY_ATTACH_TO_TARGET_RE = re.compile(
    r"\bcan't attach Energy from (?:their|his or her|your) hand\b",
    flags=re.IGNORECASE,
)
TOOL_ATTACH_RE = re.compile(
    r"\bcan't attach any Pok[eé]mon Tool cards? from "
    r"(?:their|his or her|your) hand\b",
    flags=re.IGNORECASE,
)
EVOLUTION_RE = re.compile(
    r"\bcan't play any Pok[eé]mon from (?:their|his or her|your) hand to evolve\b",
    flags=re.IGNORECASE,
)
DIRECT_HAND_RESTRICTION_RE = re.compile(
    r"\bcan't (?:play any|attach any|attach Energy)[^.]{0,220}? "
    r"from (?:their|his or her|your) hand\b",
    flags=re.IGNORECASE,
)

TRAINER_KINDS = frozenset({"item", "tool", "supporter", "stadium"})
CARD_KINDS = frozenset(
    {
        "item",
        "tool",
        "supporter",
        "stadium",
        "pokemon",
        "basic_energy",
        "special_energy",
    }
)
ACTION_MODES = frozenset({"play", "attach", "evolve"})


@dataclass(frozen=True)
class SourceScopedActionRestriction:
    card_id: str
    card_name: str
    source: str
    text: str
    prohibited_source_zone: str
    dimensions: frozenset[str]
    target_scope: str
    required_target_relation: str | None = None
    excluded_card_tags: frozenset[str] = frozenset()
    exclusive_dimension_options: tuple[frozenset[str], ...] = ()


@dataclass(frozen=True)
class CardActionAttempt:
    card_kind: str
    source_zone: str
    mode: str = "play"
    card_tags: frozenset[str] = frozenset()
    target_relation: str = "any"

    def __post_init__(self) -> None:
        if self.card_kind not in CARD_KINDS:
            raise ValueError(f"unsupported card_kind: {self.card_kind!r}")
        if not self.source_zone:
            raise ValueError("source_zone must be non-empty")
        if self.mode not in ACTION_MODES:
            raise ValueError(f"unsupported action mode: {self.mode!r}")
        if not self.target_relation:
            raise ValueError("target_relation must be non-empty")


def _effect_rows(card: dict):
    for index, rule in enumerate(card.get("rules") or []):
        yield f"rule:{index}", rule
    for attack in card.get("attacks") or []:
        text = attack.get("text") or ""
        if text:
            yield f"attack:{attack.get('name', '')}", text
    for ability in card.get("abilities") or []:
        text = ability.get("text") or ""
        if text:
            yield f"ability:{ability.get('name', '')}", text


def _categories_to_dimensions(categories: str) -> set[str]:
    lowered = categories.lower()
    compact = re.sub(r"\s+", " ", lowered).strip()
    dimensions: set[str] = set()
    if compact in {"card", "cards"}:
        dimensions.add("all_cards_from_hand")
    if "trainer" in lowered:
        dimensions.add("trainer")
    if "item" in lowered:
        dimensions.add("item")
    if "supporter" in lowered:
        dimensions.add("supporter")
    if "ace spec" in lowered:
        dimensions.add("ace_spec")
    if "pokémon tool" in lowered or "pokemon tool" in lowered:
        dimensions.add("tool")
    if "stadium" in lowered:
        dimensions.add("stadium")
    if "special energy" in lowered:
        dimensions.add("special_energy_play")
    if (
        ("pokémon" in lowered or "pokemon" in lowered)
        and "ability" in lowered
    ):
        dimensions.add("ability_pokemon_play")
    return dimensions


def _dimensions(text: str) -> frozenset[str]:
    dimensions: set[str] = set()
    for match in PLAY_LOCK_RE.finditer(text):
        dimensions.update(_categories_to_dimensions(match.group("categories")))
    if CHOSEN_TRAINER_LOCK_RE.search(text):
        dimensions.update({"item", "supporter"})
    if SPECIAL_ENERGY_ATTACH_RE.search(text):
        dimensions.add("special_energy_attach")
    if ENERGY_ATTACH_TO_TARGET_RE.search(text):
        dimensions.add("energy_attach_to_target")
    if TOOL_ATTACH_RE.search(text):
        dimensions.add("tool_attach")
    if EVOLUTION_RE.search(text):
        dimensions.add("evolution")
    return frozenset(dimensions)


def _exclusive_dimension_options(text: str) -> tuple[frozenset[str], ...]:
    if CHOSEN_TRAINER_LOCK_RE.search(text):
        return (frozenset({"item"}), frozenset({"supporter"}))
    if ALLERGY_STORM_RE.search(text):
        return (frozenset({"supporter"}), frozenset({"item"}))
    return ()


def _target_scope(text: str) -> str:
    lowered = text.lower()
    if "each player can't" in lowered:
        return "both"
    if "your opponent can't" in lowered or "they can't" in lowered:
        return "opponent"
    return "opponent"


def _required_target_relation(
    text: str,
    dimensions: frozenset[str],
) -> str | None:
    lowered = text.lower()
    if (
        dimensions & {"evolution", "energy_attach_to_target"}
        and ("defending pokémon" in lowered or "defending pokemon" in lowered)
    ):
        return "defending_pokemon"
    return None


def _excluded_card_tags(text: str) -> frozenset[str]:
    if re.search(
        r"except for Team Rocket's Pok[eé]mon",
        text,
        flags=re.IGNORECASE,
    ):
        return frozenset({"team_rocket"})
    return frozenset()


def build_source_scoped_action_restrictions(
    resources_root: Path,
) -> tuple[SourceScopedActionRestriction, ...]:
    """Return legal direct play/attach prohibitions with explicit hand source."""

    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[SourceScopedActionRestriction] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            for source, raw_text in _effect_rows(card):
                text = " ".join(raw_text.split())
                dimensions = _dimensions(text)
                if not dimensions:
                    if DIRECT_HAND_RESTRICTION_RE.search(text):
                        raise ValueError(
                            "unparsed direct hand-scoped restriction: "
                            f"{card['id']} {text!r}"
                        )
                    continue
                rows.append(
                    SourceScopedActionRestriction(
                        card_id=card["id"],
                        card_name=card["name"],
                        source=source,
                        text=text,
                        prohibited_source_zone="hand",
                        dimensions=dimensions,
                        target_scope=_target_scope(text),
                        required_target_relation=_required_target_relation(
                            text,
                            dimensions,
                        ),
                        excluded_card_tags=_excluded_card_tags(text),
                        exclusive_dimension_options=_exclusive_dimension_options(text),
                    )
                )

    return tuple(
        sorted(
            rows,
            key=lambda row: (row.card_id, row.source, row.text),
        )
    )


def _attempt_dimensions(attempt: CardActionAttempt) -> frozenset[str]:
    dimensions = {"all_cards_from_hand"}
    if attempt.card_kind in TRAINER_KINDS:
        dimensions.add("trainer")
    if attempt.card_kind == "item":
        dimensions.add("item")
    elif attempt.card_kind == "tool":
        dimensions.update({"tool", "tool_attach"})
    elif attempt.card_kind == "supporter":
        dimensions.add("supporter")
    elif attempt.card_kind == "stadium":
        dimensions.add("stadium")
    elif attempt.card_kind == "special_energy":
        dimensions.update({"special_energy_play", "special_energy_attach"})

    if "ace_spec" in attempt.card_tags:
        dimensions.add("ace_spec")
    if (
        attempt.card_kind == "pokemon"
        and "has_ability" in attempt.card_tags
    ):
        dimensions.add("ability_pokemon_play")
    if attempt.card_kind == "pokemon" and attempt.mode == "evolve":
        dimensions.add("evolution")
    if (
        attempt.card_kind in {"basic_energy", "special_energy"}
        and attempt.mode == "attach"
        and attempt.target_relation == "defending_pokemon"
    ):
        dimensions.add("energy_attach_to_target")
    return frozenset(dimensions)


def resolve_exclusive_restriction(
    restriction: SourceScopedActionRestriction,
    selected_dimensions: frozenset[str],
) -> SourceScopedActionRestriction:
    """Bind one printed exclusive branch before using the restriction."""

    if not restriction.exclusive_dimension_options:
        raise ValueError("restriction has no exclusive dimension choice")
    if selected_dimensions not in restriction.exclusive_dimension_options:
        raise ValueError("selected dimensions are not a legal printed branch")
    return replace(
        restriction,
        dimensions=selected_dimensions,
        exclusive_dimension_options=(),
    )


def restriction_blocks_attempt(
    restriction: SourceScopedActionRestriction,
    attempt: CardActionAttempt,
) -> bool:
    """Return whether one already-active restriction prohibits this attempt."""

    if restriction.exclusive_dimension_options:
        raise ValueError("exclusive restriction branch is unresolved")
    if restriction.prohibited_source_zone != attempt.source_zone:
        return False
    if restriction.excluded_card_tags & attempt.card_tags:
        return False
    if (
        restriction.required_target_relation is not None
        and restriction.required_target_relation != attempt.target_relation
    ):
        return False
    return bool(restriction.dimensions & _attempt_dimensions(attempt))


def restrictions_block_attempt(
    restrictions: Iterable[SourceScopedActionRestriction],
    attempt: CardActionAttempt,
) -> bool:
    return any(
        restriction_blocks_attempt(restriction, attempt)
        for restriction in restrictions
    )
