"""Reproduce the conservative multi-output Trainer search catalog."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from multi_output_search_catalog import (  # noqa: E402
    catalog_multi_output_trainers,
)


EXPECTED_FIXED_AXES = {
    "Arven",
    "Colress's Tenacity",
    "Dawn",
    "Hilda",
    "Irida",
    "Korrina",
    "Larry's Skill",
    "Piers",
    "Rosa",
    "Secret Box",
    "Steven",
    "Team Aqua's Great Ball",
    "Team Magma's Great Ball",
    "Volkner",
}

EXPECTED_CONDITIONAL_ADDITIONAL = {
    "Guzma & Hala",
    "Sabrina & Brycen",
}

EXPECTED_UNBOUNDED = {
    "Energy Search Pro",
    "Precious Trolley",
}


def main() -> None:
    result = catalog_multi_output_trainers(ROOT / "resources")
    summary = result["summary"]

    expected_summary = {
        "union_unique_names": 90,
        "union_prints": 202,
        "class_print_counts": {
            "conditional_additional": 3,
            "fixed_axes": 37,
            "numeric_multi": 161,
            "unbounded_multi": 2,
        },
        "class_unique_name_counts": {
            "conditional_additional": 2,
            "fixed_axes": 14,
            "numeric_multi": 73,
            "unbounded_multi": 2,
        },
    }
    if summary != expected_summary:
        raise AssertionError(
            (summary, expected_summary)
        )

    names_by_class: dict[str, set[str]] = defaultdict(set)
    rows_by_name: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in result["rows"]:
        rows_by_name[row["name"]].append(row)
        for classification in row["classifications"]:
            names_by_class[classification].add(row["name"])

    if names_by_class["fixed_axes"] != EXPECTED_FIXED_AXES:
        raise AssertionError(
            names_by_class["fixed_axes"]
        )
    if (
        names_by_class["conditional_additional"]
        != EXPECTED_CONDITIONAL_ADDITIONAL
    ):
        raise AssertionError(
            names_by_class["conditional_additional"]
        )
    if names_by_class["unbounded_multi"] != EXPECTED_UNBOUNDED:
        raise AssertionError(
            names_by_class["unbounded_multi"]
        )

    secret_box = rows_by_name["Secret Box"]
    if not secret_box:
        raise AssertionError("Secret Box missing")
    if not any(
        row["fixed_axes_clause"]
        == (
            "an Item card, a Pokémon Tool card, "
            "a Supporter card, and a Stadium card"
        )
        for row in secret_box
    ):
        raise AssertionError(secret_box)

    guzma_hala = rows_by_name["Guzma & Hala"]
    if not guzma_hala:
        raise AssertionError("Guzma & Hala missing")
    if not all(
        "conditional_additional" in row["classifications"]
        for row in guzma_hala
    ):
        raise AssertionError(guzma_hala)

    print(summary)
    print(
        "fixed-axis names:",
        ", ".join(sorted(EXPECTED_FIXED_AXES)),
    )
    print(
        "conditional additional-search names:",
        ", ".join(sorted(EXPECTED_CONDITIONAL_ADDITIONAL)),
    )
    print(
        "unbounded-search names:",
        ", ".join(sorted(EXPECTED_UNBOUNDED)),
    )


if __name__ == "__main__":
    main()
