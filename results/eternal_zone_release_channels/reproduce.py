from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from bench_release_channel import eternal_zone_full_contraction_examples


def main() -> None:
    rows = {row["name"]: row for row in eternal_zone_full_contraction_examples()}

    assert rows["Field Blower"]["mechanically_usable"] is True
    assert rows["Field Blower"]["enables_same_turn_continuation"] is True

    assert rows["Lost Vacuum"]["mechanically_usable"] is True
    assert rows["Lost Vacuum"]["enables_same_turn_continuation"] is True

    assert rows["Worker"]["mechanically_usable"] is True
    assert rows["Worker"]["enables_same_turn_continuation"] is True

    entry = rows["Pumpkaboo / Chien-Pao"]
    assert entry["mechanically_usable"] is False
    assert "no open Bench slot" in entry["blocking_reasons"]

    stadium = rows["play another Stadium"]
    assert stadium["mechanically_usable"] is False
    assert "Stadium play already used" in stadium["blocking_reasons"]

    attack = rows["attack-based Stadium removal"]
    assert attack["mechanically_usable"] is True
    assert attack["enables_same_turn_continuation"] is False

    print("eternal_zone_release_channels: all checks passed")


if __name__ == "__main__":
    main()
