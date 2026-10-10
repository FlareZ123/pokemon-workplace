"""Exact one-turn Legacy Star recovery witness after Dragon Impact.

Assumptions: no lock effects, no other Energy in hand, >=7 inert deck cards,
one eligible VSTAR Power remains if flag is true, unused normal attachment if
flag is true. Model only recovering the previously discarded DDE.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.energy_discard_continuation_frontier import (
    DRAGON_ENERGIES,
    _load_card,
    build as base_build,
)
from tools.energy_discard_solver import max_typed_match

DDE_INDEX = 0


def recovery_requirement(
    source_payment: list[int],
    attack_cost: list[str],
    *,
    vstar_available: bool,
    manual_attach_available: bool,
    ability_enabled: bool,
) -> dict[str, Any]:
    paid = set(source_payment)
    active = [c for i, c in enumerate(DRAGON_ENERGIES) if i not in paid]
    if max_typed_match(active, attack_cost) == len(attack_cost):
        return {"ready": True, "actions": [], "vstar_spent": 0, "manual_attachments_spent": 0}

    if DDE_INDEX not in paid:
        return {"ready": False, "actions": [], "vstar_spent": 0, "manual_attachments_spent": 0}

    if not (vstar_available and manual_attach_available and ability_enabled):
        return {"ready": False, "actions": [], "vstar_spent": 0, "manual_attachments_spent": 0}

    # Legacy Star's printed effect can put the discarded DDE into hand.
    # Normal turn attachment then moves this Special Energy onto Regidrago.
    restored = active + [DRAGON_ENERGIES[DDE_INDEX]]
    if max_typed_match(restored, attack_cost) != len(attack_cost):
        return {"ready": False, "actions": [], "vstar_spent": 0, "manual_attachments_spent": 0}
    return {
        "ready": True,
        "actions": ["Legacy Star (recover DDE)", "normal attachment (attach DDE)"],
        "vstar_spent": 1,
        "manual_attachments_spent": 1,
    }


def build(resources_root: Path) -> dict[str, Any]:
    source = base_build(resources_root)
    regidrago = _load_card(resources_root, "swsh12-136")
    power = next(a for a in regidrago["abilities"] if a["name"] == "Legacy Star")
    assert "discard the top 7 cards of your deck" in power["text"]
    assert "put up to 2 cards from your discard pile into your hand" in power["text"]
    assert "VSTAR Power" in power["text"]
    iron_thorns = _load_card(resources_root, "sv6-77")
    assert iron_thorns["name"] == "Iron Thorns ex"
    initialization = next(a for a in iron_thorns["abilities"]
                          if a["name"] == "Initialization")
    assert "Pokémon with a Rule Box in play" in initialization["text"]
    assert "have no Abilities, except for Future Pokémon" in initialization["text"]
    assert any("VSTAR rule" in rule for rule in regidrago.get("rules") or ())
    assert "Future" not in (regidrago.get("subtypes") or ())

    cost = source["future_attack"]["cost"]
    variants = {
        "power_available": (True, True, True),
        "power_already_used": (False, True, True),
        "manual_attachment_spent": (True, False, True),
        "ability_suppressed": (True, True, False),
    }
    rows = []
    for payment in source["payments"]:
        outputs = {}
        for name, (vstar, manual, enabled) in variants.items():
            outputs[name] = recovery_requirement(
                payment["discard_indices"], cost,
                vstar_available=vstar,
                manual_attach_available=manual,
                ability_enabled=enabled,
            )
        rows.append({
            "payment": payment["discard_names"],
            "physical_cards_discarded": payment["physical_cards_discarded"],
            "recovery": outputs,
        })

    assert len(rows) == 4
    one = next(r for r in rows if r["physical_cards_discarded"] == 1)
    two = [r for r in rows if r["physical_cards_discarded"] == 2]
    assert one["recovery"]["power_available"]["ready"]
    assert one["recovery"]["power_available"]["vstar_spent"] == 1
    assert one["recovery"]["power_available"]["manual_attachments_spent"] == 1
    assert not one["recovery"]["power_already_used"]["ready"]
    assert not one["recovery"]["manual_attachment_spent"]["ready"]
    assert not one["recovery"]["ability_suppressed"]["ready"]
    assert all(r["recovery"]["power_already_used"]["ready"] for r in two)
    assert all(not r["recovery"]["power_available"]["actions"] for r in two)

    return {
        "sources": {"regidrago_vstar": "swsh12-136", "dragon_impact": "sv9-114",
                    "double_dragon_energy": "xy6-97", "iron_thorns_ex": "sv6-77"},
        "deck_after_legacy_star": "at least seven inert deck cards before ability, all seven discarded",
        "recovery_scope": "previously discarded DDE only, then normal hand attachment",
        "next_attack_cost": cost,
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(build(Path("resources")), indent=2))
