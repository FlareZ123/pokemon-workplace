from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from bench_capacity_model import Occupant, effective_capacity, optimal_forced_discard, route_trace
from bench_resource_catalog import build


def main() -> None:
    catalog = build(ROOT / "resources")

    capacity = {row["name"]: row for row in catalog["capacity_effects"]}
    expected = {
        "Area Zero Underdepths": (8, "both"),
        "Collapsed Stadium": (4, "both"),
        "Eternatus VMAX": (8, "self"),
        "Glimmora ex": (3, "opponent"),
        "Parallel City": (3, "chosen_side"),
        "Sky Field": (8, "both"),
        "Sudowoodo": (4, "opponent"),
    }
    assert set(expected) <= set(capacity)
    for name, (cap, target) in expected.items():
        assert capacity[name]["cap"] == cap
        assert capacity[name]["target"] == target

    access_names = {row["name"] for row in catalog["bench_entry_resource_access"]}
    assert {"Tapu Lele-GX", "Dedenne-GX", "Crobat V", "Jirachi-EX", "Lumineon V"} <= access_names

    cleanup_names = {row["name"] for row in catalog["cleanup_trainers"]}
    assert "Scoop Up Net" not in cleanup_names
    assert {"AZ", "Scoop Up Cyclone", "Super Scoop Up", "Giovanni's Exile"} <= cleanup_names

    assert effective_capacity() == 5
    assert effective_capacity(extension_caps=(8,)) == 8
    assert effective_capacity(extension_caps=(8,), restriction_caps=(4,)) == 4
    assert effective_capacity(extension_caps=(8,), restriction_caps=(3,)) == 3

    default_line = route_trace(4, 5, (1, 1, -1))
    assert default_line["final_occupancy"] == 5
    assert default_line["peak_occupancy"] == 6
    assert default_line["feasible"] is False
    assert default_line["first_overflow_step"] == 2

    expanded_line = route_trace(4, 8, (1, 1, -1))
    assert expanded_line["feasible"] is True

    board = (
        Occupant("spent two-Prize search support", -2.0),
        Occupant("spent one-shot utility", 0.0),
        Occupant("pivot", 3.0),
        Occupant("secondary attacker", 6.0),
        Occupant("primary setup piece", 10.0),
    )
    shrink = optimal_forced_discard(board, 3)
    assert [row["name"] for row in shrink["discarded"]] == [
        "spent two-Prize search support",
        "spent one-shot utility",
    ]
    assert shrink["affected_player_continuation_loss"] == -2.0

    print("bench_capacity_geometry: all checks passed")
    print(catalog["counts"])


if __name__ == "__main__":
    main()
