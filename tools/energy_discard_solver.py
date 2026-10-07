from __future__ import annotations

from itertools import combinations
from typing import Any

ENERGY_TYPES = (
    "Grass",
    "Fire",
    "Water",
    "Lightning",
    "Psychic",
    "Fighting",
    "Darkness",
    "Metal",
    "Fairy",
    "Colorless",
)


def generic_units(cards: list[dict[str, Any]]) -> int:
    return sum(int(card["units"]) for card in cards)


def _typed_slots(
    cards: list[dict[str, Any]],
    *,
    basic_only: bool = False,
) -> list[frozenset[str]]:
    slots: list[frozenset[str]] = []
    for card in cards:
        if basic_only and not bool(card.get("basic", False)):
            continue
        types = frozenset(card["types"])
        slots.extend([types] * int(card["units"]))
    return slots


def max_typed_match(
    cards: list[dict[str, Any]],
    demand_types: list[str],
    *,
    basic_only: bool = False,
) -> int:
    slots = _typed_slots(cards, basic_only=basic_only)
    states = {0}

    for slot_types in slots:
        new_states = set(states)
        for mask in states:
            for index, energy_type in enumerate(demand_types):
                if (mask >> index) & 1:
                    continue
                if energy_type in slot_types:
                    new_states.add(mask | (1 << index))
        states = new_states

    return max(mask.bit_count() for mask in states)


def minimum_card_subsets_generic(
    cards: list[dict[str, Any]],
    required_units: int,
) -> dict[str, Any]:
    max_possible = min(required_units, generic_units(cards))

    for card_count in range(len(cards) + 1):
        subsets = []
        for indexes in combinations(range(len(cards)), card_count):
            subset = [cards[index] for index in indexes]
            score = min(required_units, generic_units(subset))
            if score == max_possible:
                subsets.append(list(indexes))

        if subsets:
            return {
                "required_units": required_units,
                "matched_units": max_possible,
                "full": max_possible == required_units,
                "minimum_cards": card_count,
                "subsets": subsets,
            }

    raise AssertionError("At least the empty subset must be available")


def minimum_card_subsets_typed(
    cards: list[dict[str, Any]],
    demand_types: list[str],
    *,
    basic_only: bool = False,
) -> dict[str, Any]:
    max_possible = max_typed_match(
        cards,
        demand_types,
        basic_only=basic_only,
    )

    for card_count in range(len(cards) + 1):
        subsets = []
        for indexes in combinations(range(len(cards)), card_count):
            subset = [cards[index] for index in indexes]
            if (
                max_typed_match(
                    subset,
                    demand_types,
                    basic_only=basic_only,
                )
                == max_possible
            ):
                subsets.append(list(indexes))

        if subsets:
            return {
                "demand_types": list(demand_types),
                "matched_units": max_possible,
                "full": max_possible == len(demand_types),
                "minimum_cards": card_count,
                "subsets": subsets,
            }

    raise AssertionError("At least the empty subset must be available")


def all_cards_providing_type(
    cards: list[dict[str, Any]],
    energy_type: str,
    *,
    basic_only: bool = False,
) -> list[int]:
    return [
        index
        for index, card in enumerate(cards)
        if (
            (not basic_only or bool(card.get("basic", False)))
            and energy_type in card["types"]
        )
    ]


def all_energy_cards(cards: list[dict[str, Any]]) -> list[int]:
    return list(range(len(cards)))
