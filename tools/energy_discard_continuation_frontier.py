"""Indivisible Energy-card payment frontier and one-step attack readiness witness.

Run from repository root: python -m tools.energy_discard_continuation_frontier
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Any

from tools.energy_discard_solver import ENERGY_TYPES, max_typed_match


# The two-unit effect of Double Dragon Energy applies while attached to a Dragon.
DRAGON_ENERGIES = [
    {"name": "Double Dragon Energy", "units": 2, "types": list(ENERGY_TYPES)},
    {"name": "Basic Grass Energy", "units": 1, "types": ["Grass"]},
    {"name": "Basic Fire Energy A", "units": 1, "types": ["Fire"]},
    {"name": "Basic Fire Energy B", "units": 1, "types": ["Fire"]},
]


def irredundant_discard_sets(cards: list[dict[str, Any]], required_units: int) -> list[tuple[int, ...]]:
    """Enumerate sufficient payments with no redundant physical Energy card.

    A multi-unit provider is indivisible and may exceed the requirement by
    itself, as with the rulebook's Ignition Energy example. A payment with a
    redundant extra card is excluded. This is a controlled payment model, not
    a complete interpreter for typed / named-card / conditional effect text.
    """
    if required_units < 0:
        raise ValueError("required_units must be nonnegative")
    if required_units == 0:
        return [()]
    full = sum(card["units"] for card in cards)
    target = min(required_units, full)
    payments: list[tuple[int, ...]] = []
    for count in range(1, len(cards) + 1):
        for indexes in combinations(range(len(cards)), count):
            units = sum(cards[i]["units"] for i in indexes)
            if units < target:
                continue
            if any(units - cards[i]["units"] >= target for i in indexes):
                continue
            payments.append(indexes)
    return payments


def continuation_frontier(
    cards: list[dict[str, Any]],
    discard_units: int,
    next_attack_cost: list[str],
) -> list[dict[str, Any]]:
    rows = []
    for payment in irredundant_discard_sets(cards, discard_units):
        remaining = [c for i, c in enumerate(cards) if i not in payment]
        matched = max_typed_match(remaining, next_attack_cost)
        rows.append({
            "discard_indices": list(payment),
            "discard_names": [cards[i]["name"] for i in payment],
            "physical_cards_discarded": len(payment),
            "energy_units_discarded": sum(cards[i]["units"] for i in payment),
            "remaining_energy_units": sum(c["units"] for c in remaining),
            "next_attack_cost_satisfied": matched == len(next_attack_cost),
            "next_attack_matched_slots": matched,
        })
    return rows


def _load_card(resources_root: Path, card_id: str) -> dict[str, Any]:
    set_id = card_id.partition("-")[0]
    cards = json.loads((resources_root / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def build(resources_root: Path) -> dict[str, Any]:
    regidrago = _load_card(resources_root, "swsh12-136")
    salamence = _load_card(resources_root, "sv9-114")
    double_dragon = _load_card(resources_root, "xy6-97")
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded = {s["id"] for s in sets if (s.get("legalities") or {}).get("expanded") == "Legal"}
    assert {"swsh12", "sv9", "xy6"} <= expanded
    apex = next(a for a in regidrago["attacks"] if a["name"] == "Apex Dragon")
    impact = next(a for a in salamence["attacks"] if a["name"] == "Dragon Impact")
    assert apex["cost"] == ["Grass", "Grass", "Fire"]
    assert "Choose an attack from a Dragon Pokémon in your discard pile" in apex["text"]
    assert impact["text"] == "Discard 2 Energy from this Pokémon."
    assert impact["damage"] == "300"
    assert "provides every type of Energy" in " ".join(double_dragon["rules"])
    assert "provides only 2 Energy at a time" in " ".join(double_dragon["rules"])
    assert max_typed_match(DRAGON_ENERGIES, apex["cost"]) == 3

    payments = continuation_frontier(DRAGON_ENERGIES, 2, apex["cost"])
    min_cards = min(row["physical_cards_discarded"] for row in payments)
    cheapest = [r for r in payments if r["physical_cards_discarded"] == min_cards]
    ready = [r for r in payments if r["next_attack_cost_satisfied"]]
    assert len(payments) == 4
    assert len(cheapest) == 1 and not cheapest[0]["next_attack_cost_satisfied"]
    assert len(ready) == 3 and all(r["physical_cards_discarded"] == 2 for r in ready)
    return {
        "source_card_ids": {"apex_dragon": "swsh12-136", "dragon_impact": "sv9-114", "double_dragon_energy": "xy6-97"},
        "starting_attachment_state": DRAGON_ENERGIES,
        "copied_attack": {"name": impact["name"], "damage": impact["damage"], "text": impact["text"]},
        "future_attack": {"name": apex["name"], "cost": apex["cost"]},
        "payments": payments,
        "summary": {"total_irredundant_payments": len(payments), "minimum_physical_discard_count": min_cards,
                    "minimum_card_payments_retaining_apex": sum(r["next_attack_cost_satisfied"] for r in cheapest),
                    "two_card_payments_retaining_apex": len(ready)},
    }


def main() -> None:
    result = build(Path("resources"))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
