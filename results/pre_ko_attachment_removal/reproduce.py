"""Reproduce the pre-KO opposing-attachment removal inventory."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pre_ko_attachment_removal_catalog import build


def main() -> None:
    result = build(ROOT / "resources")
    counts = result["counts"]
    print("Observed pre-KO catalog counts", counts)

    assert counts == {
        "print_instances": 334,
        "distinct_signatures": 216,
        "categories": {
            "before_damage:energy": 1,
            "before_damage:energy+tool": 1,
            "before_damage:tool": 25,
            "effects_outside_damage:energy": 188,
            "effects_outside_damage:energy+tool": 1,
        },
    }

    by_id = {
        row["card_id"]: row
        for row in result["representatives"]
    }
    assert set(by_id) == {
        "sv1-94",
        "sv7-8",
        "swsh3-118",
        "swsh9-114",
        "swsh10tg-TG19",
    }

    assert by_id["sv1-94"]["attack_name"] == "Energy Munch"
    assert by_id["sv1-94"]["timing"] == "effects_outside_damage"
    assert by_id["sv1-94"]["resource_kinds"] == ["energy"]

    assert by_id["swsh10tg-TG19"]["attack_name"] == "Thunderous Kick"
    assert by_id["swsh10tg-TG19"]["timing"] == "before_damage"
    assert by_id["swsh10tg-TG19"]["resource_kinds"] == ["energy"]

    assert by_id["sv7-8"]["timing"] == "before_damage"
    assert by_id["sv7-8"]["resource_kinds"] == ["energy", "tool"]

    assert by_id["swsh3-118"]["timing"] == "effects_outside_damage"
    assert by_id["swsh3-118"]["resource_kinds"] == ["energy", "tool"]

    assert by_id["swsh9-114"]["timing"] == "before_damage"
    assert by_id["swsh9-114"]["resource_kinds"] == ["tool"]

    assert all(row["damage"] for row in result["signatures"])
    assert all(row["matching_clauses"] for row in result["signatures"])

    print("Pre-KO attachment-removal catalog regressions passed")


if __name__ == "__main__":
    main()
