"""Temple of Sinnoh + one Grass attachment reverses Regidrago's DDE choice.

After a source-verified Dragon Impact generic two-Energy discard, the
opponent plays Temple. The player's next turn has one manual Basic Grass
attachment, and no Stadium replacement or other acceleration.
"""
from __future__ import annotations

import json
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

from tools.energy_discard_continuation_frontier import (
    DRAGON_ENERGIES, _load_card, build as base_build,
)
from tools.energy_discard_continuation_disruption import response_state
from tools.energy_discard_solver import ENERGY_TYPES, attack_cost_ready


def basic_attachment_frontier(
    cards: list[dict[str, Any]],
    attack_cost: list[str],
) -> tuple[int, list[tuple[str, ...]]]:
    """Minimum extra Basic cards from hand for cost, ignoring turn timing."""
    basic_types = tuple(t for t in ENERGY_TYPES if t != "Colorless")
    for count in range(len(attack_cost) + 1):
        successful = []
        for kinds in combinations_with_replacement(basic_types, count):
            added = cards + [
                {"name": f"Basic {kind} Energy", "types": [kind], "units": 1, "basic": True}
                for kind in kinds
            ]
            if attack_cost_ready(added, attack_cost):
                successful.append(kinds)
        if successful:
            return count, successful
    raise AssertionError("Three Basic Energy cards must be sufficient for a three-cost attack")


def build(resources_root: Path) -> dict[str, Any]:
    source = base_build(resources_root)
    temple = _load_card(resources_root, "swsh10-155")
    regidrago = _load_card(resources_root, "swsh12-136")
    assert temple["name"] == "Temple of Sinnoh"
    assert "provide Colorless Energy and have no other effect" in " ".join(temple.get("rules") or ())
    assert regidrago["types"] == ["Dragon"]
    cost = source["future_attack"]["cost"]
    added_grass = {"name": "Extra Basic Grass Energy", "types": ["Grass"], "units": 1, "basic": True}

    rows = []
    for payment in source["payments"]:
        removed = set(payment["discard_indices"])
        remaining = [c for i, c in enumerate(DRAGON_ENERGIES) if i not in removed]
        after_temple, available = response_state(remaining, "temple_of_sinnoh")
        assert available
        without_manual = attack_cost_ready(after_temple, cost)
        with_grass = attack_cost_ready(after_temple + [added_grass], cost)
        minimum, combinations = basic_attachment_frontier(after_temple, cost)
        rows.append({
            "discard_payment": payment["discard_names"],
            "physical_cards_discarded": payment["physical_cards_discarded"],
            "after_temple_immediate_ready": without_manual,
            "after_temple_plus_one_grass_ready": with_grass,
            "minimum_new_basic_attachments": minimum,
            "minimal_basic_type_combinations": [list(group) for group in combinations],
        })

    assert len(rows) == 4
    one = [r for r in rows if r["physical_cards_discarded"] == 1]
    two = [r for r in rows if r["physical_cards_discarded"] == 2]
    assert len(one) == 1 and len(two) == 3
    assert one[0]["minimum_new_basic_attachments"] == 1
    assert one[0]["minimal_basic_type_combinations"] == [["Grass"]]
    assert one[0]["after_temple_plus_one_grass_ready"]
    assert all(r["minimum_new_basic_attachments"] == 2 for r in two)
    assert all(not r["after_temple_plus_one_grass_ready"] for r in two)
    assert all(not r["after_temple_immediate_ready"] for r in rows)

    return {
        "source_cards": {"regidrago": "swsh12-136", "salamence": "sv9-114",
                         "double_dragon": "xy6-97", "temple": "swsh10-155"},
        "sequence": ["Apex Dragon copies Dragon Impact",
                     "discard two generic Energy",
                     "opponent plays Temple of Sinnoh",
                     "next turn attach exactly one Basic Grass from hand"],
        "next_attack_cost": cost,
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build(Path("resources")), indent=2))
