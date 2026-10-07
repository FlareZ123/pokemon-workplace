"""Build conservative semantic tags for legal Expanded search targets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import (
    classify_effective_legality,
    load_json,
)
from typed_search_target_allocator import (
    BASIC_ENERGY,
    BASIC_POKEMON,
    ENERGY,
    EVOLUTION_POKEMON,
    ITEM,
    POKEMON,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
    STAGE_1_POKEMON,
    STAGE_2_POKEMON,
    SUPPORTER,
    TEAM_PREFIX,
    TRAINER,
    TYPE_PREFIX,
    SearchSelector,
    close_tags,
    selector_from_label,
    validate_closed_tags,
)


_ENERGY_TYPE_NAMES = {
    "Grass": "grass",
    "Fire": "fire",
    "Water": "water",
    "Lightning": "lightning",
    "Psychic": "psychic",
    "Fighting": "fighting",
    "Darkness": "darkness",
    "Metal": "metal",
    "Fairy": "fairy",
}


@dataclass(frozen=True)
class TargetCandidate:
    card_id: str
    name: str
    supertype: str
    tags: frozenset[str]

    def matches(self, selector: SearchSelector) -> bool:
        return selector.required_tags <= self.tags


def semantic_tags_for_card(card: dict[str, Any]) -> frozenset[str]:
    """Return conservative deck-zone semantic tags from database metadata."""

    supertype = card.get("supertype")
    subtypes = set(card.get("subtypes") or [])
    tags: set[str] = set()

    if supertype == "Pokémon":
        tags.add(POKEMON)
        if "Basic" in subtypes:
            tags.add(BASIC_POKEMON)
        if "Stage 1" in subtypes:
            tags.add(STAGE_1_POKEMON)
        if "Stage 2" in subtypes:
            tags.add(STAGE_2_POKEMON)
        if (
            "Basic" not in subtypes
            and (
                card.get("evolvesFrom") is not None
                or "Stage 1" in subtypes
                or "Stage 2" in subtypes
            )
        ):
            tags.add(EVOLUTION_POKEMON)

        for type_name in card.get("types") or []:
            tags.add(f"{TYPE_PREFIX}{type_name.casefold()}")

        name = card.get("name") or ""
        if name.startswith("Team Aqua's "):
            tags.add(f"{TEAM_PREFIX}team_aqua")
        if name.startswith("Team Magma's "):
            tags.add(f"{TEAM_PREFIX}team_magma")

    elif supertype == "Trainer":
        tags.add(TRAINER)

        # Current rules treat Pokémon Tools as their own Trainer type even for
        # older prints whose historical top line said Item.
        if "Pokémon Tool" in subtypes:
            tags.add(POKEMON_TOOL)
        elif "Item" in subtypes:
            tags.add(ITEM)

        if "Supporter" in subtypes:
            tags.add(SUPPORTER)
        if "Stadium" in subtypes:
            tags.add(STADIUM)

    elif supertype == "Energy":
        tags.add(ENERGY)
        if "Basic" in subtypes:
            tags.add(BASIC_ENERGY)
            energy_type = _ENERGY_TYPE_NAMES.get(
                (card.get("name") or "").removesuffix(" Energy")
            )
            if energy_type is not None:
                tags.add(f"{TYPE_PREFIX}{energy_type}")
        if "Special" in subtypes:
            tags.add(SPECIAL_ENERGY)

    closed = close_tags(tags)
    validate_closed_tags(closed)
    return closed


def load_legal_target_candidates(
    resources_root: Path = Path("resources"),
) -> tuple[TargetCandidate, ...]:
    """Load effectively legal prints from sets in the Expanded scope."""

    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    candidates: list[TargetCandidate] = []
    for path in sorted(
        (resources_root / "cards" / "en").glob("*.json")
    ):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            tags = semantic_tags_for_card(card)
            if not tags:
                continue
            candidates.append(
                TargetCandidate(
                    card_id=card["id"],
                    name=card["name"],
                    supertype=card["supertype"],
                    tags=tags,
                )
            )

    return tuple(candidates)


def matching_candidates(
    label: str,
    candidates: tuple[TargetCandidate, ...],
) -> tuple[TargetCandidate, ...]:
    selector = selector_from_label(label)
    return tuple(
        candidate
        for candidate in candidates
        if candidate.matches(selector)
    )
