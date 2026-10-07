from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from tools.apex_dragon_discard_burden import build as build_basic_catalog
from tools.energy_discard_solver import (
    ENERGY_TYPES,
    all_basic_named_cards,
    all_cards_providing_type,
    all_energy_cards,
    minimum_basic_named_card_subsets,
    minimum_card_subsets_generic,
    minimum_card_subsets_typed,
)

BASIC_GGF = [
    {
        "name": "Basic Grass A",
        "units": 1,
        "types": ["Grass"],
        "basic": True,
        "basic_energy_name": "Grass",
    },
    {
        "name": "Basic Grass B",
        "units": 1,
        "types": ["Grass"],
        "basic": True,
        "basic_energy_name": "Grass",
    },
    {
        "name": "Basic Fire",
        "units": 1,
        "types": ["Fire"],
        "basic": True,
        "basic_energy_name": "Fire",
    },
]

DDE_FIRE = [
    {
        "name": "Double Dragon Energy",
        "units": 2,
        "types": list(ENERGY_TYPES),
        "basic": False,
    },
    {
        "name": "Basic Fire",
        "units": 1,
        "types": ["Fire"],
        "basic": True,
        "basic_energy_name": "Fire",
    },
]


def _unit_range(
    cards: list[dict[str, Any]],
    subsets: list[list[int]],
) -> list[int]:
    values = [
        sum(cards[index]["units"] for index in subset)
        for subset in subsets
    ]
    return [min(values), max(values)] if values else [0, 0]


def solve_requirement(
    parsed: dict[str, Any],
    cards: list[dict[str, Any]],
) -> dict[str, Any] | None:
    kind = parsed["kind"]

    if kind == "generic_all":
        indexes = all_energy_cards(cards)
        units = sum(cards[index]["units"] for index in indexes)
        return {
            "full": True,
            "matched_units": units,
            "minimum_cards": len(indexes),
            "minimum_card_subsets": [indexes],
            "energy_units_lost_range_for_minimum_card_subsets": [units, units],
        }

    if kind == "generic_count":
        result = minimum_card_subsets_generic(cards, parsed["count"])
    elif kind == "typed_count":
        energy_type = parsed["energy_type"]
        basic_named = bool(parsed.get("basic_only", False))
        if parsed["count"] == "all":
            indexes = (
                all_basic_named_cards(cards, energy_type)
                if basic_named
                else all_cards_providing_type(cards, energy_type)
            )
            units = sum(cards[index]["units"] for index in indexes)
            return {
                "full": True,
                "matched_units": units,
                "matched_cards": len(indexes) if basic_named else None,
                "requirement_basis": (
                    "basic_named_cards" if basic_named else "provided_energy_units"
                ),
                "minimum_cards": len(indexes),
                "minimum_card_subsets": [indexes],
                "energy_units_lost_range_for_minimum_card_subsets": [units, units],
            }
        if basic_named:
            result = minimum_basic_named_card_subsets(
                cards,
                energy_type,
                parsed["count"],
            )
            subsets = result["subsets"]
            return {
                "full": result["full"],
                "matched_units": result["matched_cards"],
                "matched_cards": result["matched_cards"],
                "requirement_basis": "basic_named_cards",
                "minimum_cards": result["minimum_cards"],
                "minimum_card_subsets": subsets,
                "energy_units_lost_range_for_minimum_card_subsets": _unit_range(
                    cards,
                    subsets,
                ),
            }
        result = minimum_card_subsets_typed(
            cards,
            [energy_type] * parsed["count"],
        )
    elif kind == "typed_pair":
        result = minimum_card_subsets_typed(
            cards,
            parsed["energy_types"],
        )
    else:
        return None

    return {
        "full": result["full"],
        "matched_units": result["matched_units"],
        "minimum_cards": result["minimum_cards"],
        "minimum_card_subsets": result["subsets"],
        "energy_units_lost_range_for_minimum_card_subsets": _unit_range(
            cards,
            result["subsets"],
        ),
    }


def build(resources_root: Path) -> dict[str, Any]:
    catalog = build_basic_catalog(
        resources_root,
        {"Grass": 2, "Fire": 1},
    )

    rows = []
    for row in catalog["signatures"]:
        if row["first_discard"]["kind"] in {
            "choice_or_variable",
            "unsupported",
        }:
            continue

        output = {
            key: value
            for key, value in row.items()
            if key != "forced_discard_count"
        }
        output["basic_ggf"] = solve_requirement(
            row["first_discard"],
            BASIC_GGF,
        )
        output["dde_fire"] = solve_requirement(
            row["first_discard"],
            DDE_FIRE,
        )
        rows.append(output)

    def burden_summary(key: str) -> dict[str, int]:
        counts = Counter(row[key]["minimum_cards"] for row in rows)
        return {str(value): counts[value] for value in sorted(counts)}

    changed = [
        row
        for row in rows
        if (
            row["basic_ggf"]["minimum_cards"]
            != row["dde_fire"]["minimum_cards"]
            or row["basic_ggf"]["matched_units"]
            != row["dde_fire"]["matched_units"]
        )
    ]

    return {
        "scenarios": {
            "basic_ggf": BASIC_GGF,
            "dde_fire": DDE_FIRE,
        },
        "counts": {
            "signatures_compared": len(rows),
            "basic_ggf_minimum_card_burden": burden_summary("basic_ggf"),
            "dde_fire_minimum_card_burden": burden_summary("dde_fire"),
            "changed_signatures": len(changed),
        },
        "changed": changed,
        "signatures": rows,
    }
