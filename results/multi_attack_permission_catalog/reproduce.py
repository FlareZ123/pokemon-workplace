"""Reproduce the Expanded multi-attack permission catalog."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from multi_attack_permission_catalog import build  # noqa: E402


EXPECTED_PRINTS = {
    "sv6-18",
    "sv6-44",
    "sv6-89",
    "sv6-170",
    "sv8pt5-10",
    "sv8pt5-20",
    "sv8pt5-21",
    "swsh7-4",
    "xy5-26",
    "xy5-69",
    "xy5-81",
    "xy5-97",
    "xy5-121",
}


def main() -> None:
    result = build(ROOT / "resources")
    counts = result["counts"]
    assert counts == {
        "print_effect_instances": 13,
        "distinct_signatures": 3,
        "distinct_card_names": 10,
        "source_kinds": {"ability": 8, "ancient_trait": 5},
        "festival_condition_instances": 7,
    }

    assert {row["print_id"] for row in result["instances"]} == EXPECTED_PRINTS

    signatures = {row["effect_name"]: row for row in result["signatures"]}
    assert set(signatures) == {"Festival Lead", "Fluffy Barrage", "Ω Barrage"}

    festival = signatures["Festival Lead"]
    assert festival["source_kind"] == "ability"
    assert festival["ability_suppression_sensitive"]
    assert festival["requires_festival_grounds"]
    assert set(festival["card_names"]) == {"Dipplin", "Goldeen", "Seaking", "Swirlix"}

    fluffy = signatures["Fluffy Barrage"]
    assert fluffy["source_kind"] == "ability"
    assert fluffy["ability_suppression_sensitive"]
    assert not fluffy["requires_festival_grounds"]

    omega = signatures["Ω Barrage"]
    assert omega["source_kind"] == "ancient_trait"
    assert not omega["ability_suppression_sensitive"]
    assert not omega["requires_festival_grounds"]

    print("multi-attack permission catalog regression: PASS")
    print(counts)


if __name__ == "__main__":
    main()
