from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.apex_dragon_discard_burden import build  # noqa: E402


def main() -> None:
    result = build(ROOT / "resources", {"Grass": 2, "Fire": 1})
    assert result["scenario"]["attached_basic_energy_cards"] == {
        "Fire": 1,
        "Grass": 2,
    }
    assert result["counts"] == {
        "matching_print_instances": 71,
        "distinct_attack_signatures": 38,
        "deterministic_burden_signatures": 35,
        "choice_or_variable_signatures": 3,
        "forced_discard_burden": {
            "0": 5,
            "1": 11,
            "2": 7,
            "3": 12,
        },
        "zero_burden_independent_signatures": 4,
    }

    zero = {
        (row["card_name"], row["attack_name"], row["damage"])
        for row in result["zero_burden_independent"]
    }
    assert ("Hydreigon", "Dragonblast", "140") in zero
    assert ("Zygarde", "Core Enforcer", "150") in zero
    assert ("Kingdra", "Dragon Blast", "150") in zero

    photon = [
        row
        for row in result["signatures"]
        if row["card_name"] == "Ultra Necrozma-GX"
        and row["attack_name"] == "Photon Geyser"
    ]
    assert len(photon) == 1
    assert photon[0]["forced_discard_count"] == 0
    assert photon[0]["quantity_coupled"] is True

    print(result["counts"])


if __name__ == "__main__":
    main()
