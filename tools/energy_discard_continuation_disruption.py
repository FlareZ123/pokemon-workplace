"""Opponent-response stress test for continuation-aware DDE payments.

This deliberately evaluates a one-opponent-action abstraction immediately
after copying Salamence ex's Dragon Impact, before any new attachments.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.energy_discard_continuation_frontier import DRAGON_ENERGIES, build as build_base
from tools.energy_discard_solver import max_typed_match


def response_state(
    remaining: list[dict[str, Any]],
    response: str,
) -> tuple[list[dict[str, Any]], bool]:
    """Return post-response providers and whether the response can act here."""
    if response == "none":
        return remaining, True

    if response == "enhanced_hammer":
        # Source text: discard a Special Energy from an opponent's Pokemon.
        for index, card in enumerate(remaining):
            if card["name"] == "Double Dragon Energy":
                return [c for j, c in enumerate(remaining) if j != index], True
        return remaining, False

    if response == "temple_of_sinnoh":
        # Stadium continuous effect suppresses Special Energy text.
        # Its mandatory provision becomes one Colorless unit.
        replacement = []
        for card in remaining:
            if card["name"] == "Double Dragon Energy":
                replacement.append({
                    "name": card["name"], "types": ["Colorless"], "units": 1,
                    "basic": False,
                })
            else:
                replacement.append(card)
        return replacement, True

    raise ValueError("Unrecognized response")


def build(resources_root: Path) -> dict[str, Any]:
    original = build_base(resources_root)
    from tools.energy_discard_continuation_frontier import _load_card

    hammer = _load_card(resources_root, "sv6-148")
    temple = _load_card(resources_root, "swsh10-155")
    assert hammer["name"] == "Enhanced Hammer"
    assert "Discard a Special Energy from" in " ".join(hammer.get("rules") or ())
    assert temple["name"] == "Temple of Sinnoh"
    assert "provide Colorless Energy and have no other effect" in " ".join(temple.get("rules") or ())

    cost = original["future_attack"]["cost"]
    rows = []
    for payment in original["payments"]:
        discard_set = set(payment["discard_indices"])
        remaining = [c for i, c in enumerate(DRAGON_ENERGIES) if i not in discard_set]
        responses: dict[str, dict[str, Any]] = {}
        for label in ("none", "enhanced_hammer", "temple_of_sinnoh"):
            resulting_cards, action_available = response_state(remaining, label)
            ready = max_typed_match(resulting_cards, cost) == len(cost)
            responses[label] = {
                "available": action_available,
                "next_apex_energy_ready": ready,
                "remaining_basic_cards": sum(bool(c.get("basic")) for c in resulting_cards),
                "remaining_special_cards": sum(not bool(c.get("basic")) for c in resulting_cards),
                "remaining_energy_units": sum(int(c["units"]) for c in resulting_cards),
            }
        rows.append({
            "payment": payment["discard_names"],
            "physical_cards_discarded": payment["physical_cards_discarded"],
            "responses": responses,
        })
    assert len(rows) == 4
    first = next(row for row in rows if row["physical_cards_discarded"] == 1)
    more = [row for row in rows if row["physical_cards_discarded"] == 2]
    assert first["responses"]["none"]["next_apex_energy_ready"] is False
    assert first["responses"]["enhanced_hammer"]["available"] is False
    for row in more:
        assert row["responses"]["none"]["next_apex_energy_ready"] is True
        assert row["responses"]["enhanced_hammer"]["available"] is True
    for row in rows:
        assert row["responses"]["enhanced_hammer"]["next_apex_energy_ready"] is False
        assert row["responses"]["temple_of_sinnoh"]["next_apex_energy_ready"] is False
    return {
        "source_cards": {
            "regidrago": "swsh12-136",
            "salamence": "sv9-114",
            "double_dragon": "xy6-97",
            "enhanced_hammer": "sv6-148",
            "temple_of_sinnoh": "swsh10-155",
        },
        "response_timing": "one opponent action after current attack, before another attachment",
        "next_attack_cost": cost,
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build(Path("resources")), indent=2))
