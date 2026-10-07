from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from damage_reaction_catalog import build_damage_reaction_catalog  # noqa: E402


def main() -> None:
    result = build_damage_reaction_catalog(ROOT / "resources")
    assert result["print_rows"] == 89
    assert result["unique_text_signatures"] == 40
    assert result["rows_by_category"] == {
        "discard_attacker_energy": 2,
        "discard_opponent_hand": 1,
        "draw": 3,
        "fixed_damage_counters": 50,
        "mirror_damage_counters": 12,
        "move_attacker_energy": 1,
        "return_attacker_energy": 2,
        "scaled_damage_counters": 5,
        "search": 1,
        "special_condition": 12,
    }
    assert result["signatures_by_category"] == {
        "discard_attacker_energy": 1,
        "discard_opponent_hand": 1,
        "draw": 3,
        "fixed_damage_counters": 20,
        "mirror_damage_counters": 5,
        "move_attacker_energy": 1,
        "return_attacker_energy": 1,
        "scaled_damage_counters": 3,
        "search": 1,
        "special_condition": 4,
    }
    assert result["unclassified"] == []
    print(result)


if __name__ == "__main__":
    main()
