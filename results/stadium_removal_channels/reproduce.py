from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from stadium_removal_catalog import build


def main() -> None:
    result = build(ROOT / "resources")
    counts = result["counts"]
    assert counts["effect_prints"] == 121
    assert counts["effect_text_variants"] == 71
    assert counts["unique_names"] == 66
    assert counts["unique_names_by_action_class"] == {
        "Ability": 5,
        "Attack": 51,
        "Item": 6,
        "Supporter": 4,
    }
    assert counts["bench_entry_ability_names"] == 2

    by_class = result["names_by_action_class"]
    assert {"Field Blower", "Lost Vacuum", "Paint Roller"} <= set(by_class["Item"])
    assert {"Worker", "Faba", "Flannery", "Bonnie"} == set(by_class["Supporter"])
    assert {"Pumpkaboo", "Chien-Pao"} <= set(by_class["Ability"])

    entry_names = {
        row["name"] for row in result["variants"] if row["requires_bench_entry"]
    }
    assert entry_names == {"Pumpkaboo", "Chien-Pao"}

    assert all(
        row["ends_turn"] for row in result["variants"] if row["action_class"] == "Attack"
    )
    assert all(
        row["consumes_supporter_window"]
        for row in result["variants"]
        if row["action_class"] == "Supporter"
    )

    print("stadium_removal_channels: all checks passed")
    print(counts)


if __name__ == "__main__":
    main()
