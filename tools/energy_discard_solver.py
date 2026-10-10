from __future__ import annotations

from itertools import combinations
from typing import Any, Sequence

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



def attack_cost_ready(
    cards: list[dict[str, Any]],
    attack_cost: Sequence[str],
) -> bool:
    """Test an attack's Energy cost, where Colorless is a wildcard.

    This differs intentionally from `max_typed_match`, which performs
    strict Energy-type matching for effects such as 'discard Fire Energy'.
    Any attached Energy unit can pay a Colorless attack-cost symbol.
    """
    providers = [
        {
            "units": card["units"],
            "types": (*card["types"], "Colorless"),
        }
        for card in cards
    ]
    return max_typed_match(providers, list(attack_cost)) == len(attack_cost)


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


def all_basic_named_cards(
    cards: list[dict[str, Any]],
    energy_type: str,
) -> list[int]:
    """Return physical cards named Basic <type> Energy.

    This is intentionally independent of the Energy types the cards currently
    provide. Effects can change a Basic Energy card's provided type without
    changing its card name.
    """

    return [
        index
        for index, card in enumerate(cards)
        if card.get("basic_energy_name") == energy_type
    ]


def minimum_basic_named_card_subsets(
    cards: list[dict[str, Any]],
    energy_type: str,
    required_cards: int,
) -> dict[str, Any]:
    """Solve a fixed-count Basic <type> Energy *card* requirement."""

    if required_cards < 0:
        raise ValueError("required_cards must be non-negative")

    eligible = all_basic_named_cards(cards, energy_type)
    matched = min(required_cards, len(eligible))
    subsets = [
        list(indexes)
        for indexes in combinations(eligible, matched)
    ]
    return {
        "energy_type": energy_type,
        "required_cards": required_cards,
        "matched_cards": matched,
        "full": matched == required_cards,
        "minimum_cards": matched,
        "subsets": subsets,
    }


def all_energy_cards(cards: list[dict[str, Any]]) -> list[int]:
    return list(range(len(cards)))
