from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.before_damage_timing_catalog import build  # noqa: E402


def main() -> None:
    result = build(ROOT / "resources")

    assert result["counts"] == {
        "print_instances": 54,
        "distinct_signatures": 34,
        "categories": {
            "coin_before_damage": 1,
            "opponent_special_energy_removal": 1,
            "opponent_switch_before_damage": 1,
            "opponent_tool_and_special_energy_removal": 1,
            "opponent_tool_removal": 25,
            "own_tool_variable_damage": 3,
            "self_energy_attach_before_damage": 1,
            "self_tool_gate": 1,
        },
        "dragon_signatures": 1,
    }

    dragon = result["dragon_signatures"]
    assert len(dragon) == 1
    assert dragon[0]["card_id"] == "swsh9-114"
    assert dragon[0]["card_name"] == "Dracovish V"
    assert dragon[0]["attack_name"] == "Slosh 'n' Crash"
    assert dragon[0]["damage"] == "60+"
    assert dragon[0]["category"] == "opponent_tool_removal"
    assert "120 more damage" in dragon[0]["text"]

    print(result["counts"])
    print(dragon[0])


if __name__ == "__main__":
    main()
