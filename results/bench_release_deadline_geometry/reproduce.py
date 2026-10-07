from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_release_deadline_geometry import build_result


def main() -> None:
    s = build_result()["scenarios"]
    assert s["same_turn_entry_item"] == (
        "deterministic Item releases spent support",
        "Bench required Pokémon",
    )
    assert s["same_turn_entry_supporter"] == (
        "Supporter pickup releases spent support",
        "Bench required Pokémon",
    )
    assert s["same_turn_entry_attack"] is None
    assert s["next_turn_entry_attack_plus_next_supporter"] == (
        "release attack releases spent support",
        "advance to next own turn",
        "play next-turn required Supporter",
        "Bench required Pokémon",
    )
    assert s["next_turn_entry_supporter_plus_next_supporter"] is not None
    assert s["next_turn_entry_attack_plus_distinct_current_attack"] is None
    assert s["next_turn_entry_aligned_attack_objective"] is not None
    assert s["next_turn_entry_item_plus_distinct_current_attack"] is not None
    print("bench_release_deadline_geometry regression passed")


if __name__ == "__main__":
    main()
