"""Reproduce the dynamic Special Energy unit-count catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from special_energy_unit_count_catalog import build, provider_unit_counts


EXPECTED_IDS = {
    "swsh2-174",
    "swsh2-209",
    "sv5-162",
    "sm5-136",
    "rsv10pt5-86",
    "me2-124",
    "sv2-192",
    "sv4-266",
    "sm4-100",
    "sm4-122",
}

EXPECTED_NAMES = {
    "Twin Energy",
    "Neo Upper Energy",
    "Super Boost Energy ◇",
    "Ignition Energy",
    "Reversal Energy",
    "Counter Energy",
}


def main() -> None:
    assert provider_unit_counts(
        "This card provides Colorless Energy. "
        "If a condition is true, it provides ColorlessColorlessColorless Energy instead."
    ) == (1, 3)
    assert provider_unit_counts(
        "This card provides Colorless Energy. "
        "If a condition is true, it provides every type of Energy "
        "but provides only 2 Energy at a time."
    ) == (1, 2)

    report = build(ROOT / "resources")
    rows = report["rows"]

    assert report["print_rows"] == 10
    assert report["distinct_names"] == 6
    assert set(report["names"]) == EXPECTED_NAMES
    assert {row["card_id"] for row in rows} == EXPECTED_IDS
    assert report["profiles"] == {
        "1,2": 5,
        "1,3": 4,
        "1,4": 1,
    }

    by_name = {}
    for row in rows:
        by_name.setdefault(row["card_name"], set()).add(
            tuple(row["unit_counts"])
        )

    assert by_name["Twin Energy"] == {(1, 2)}
    assert by_name["Counter Energy"] == {(1, 2)}
    assert by_name["Neo Upper Energy"] == {(1, 2)}
    assert by_name["Ignition Energy"] == {(1, 3)}
    assert by_name["Reversal Energy"] == {(1, 3)}
    assert by_name["Super Boost Energy ◇"] == {(1, 4)}

    print(json.dumps({
        "print_rows": report["print_rows"],
        "distinct_names": report["distinct_names"],
        "profiles": report["profiles"],
        "names": report["names"],
    }, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
