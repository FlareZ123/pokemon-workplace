from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.apex_dragon_special_energy_burden import build  # noqa: E402
from tools.energy_discard_solver import (  # noqa: E402
    ENERGY_TYPES,
    minimum_card_subsets_generic,
    minimum_card_subsets_typed,
)


def main() -> None:
    dde = {
        "name": "Double Dragon Energy",
        "units": 2,
        "types": list(ENERGY_TYPES),
    }
    fire = {
        "name": "Basic Fire",
        "units": 1,
        "types": ["Fire"],
    }

    generic_two = minimum_card_subsets_generic([dde, fire], 2)
    assert generic_two["full"] is True
    assert generic_two["minimum_cards"] == 1
    assert generic_two["subsets"] == [[0]]

    typed_pair = minimum_card_subsets_typed(
        [dde, fire],
        ["Water", "Lightning"],
    )
    assert typed_pair["full"] is True
    assert typed_pair["minimum_cards"] == 1
    assert typed_pair["subsets"] == [[0]]

    result = build(ROOT / "resources")
    assert result["counts"] == {
        "signatures_compared": 35,
        "basic_ggf_minimum_card_burden": {
            "0": 5,
            "1": 11,
            "2": 7,
            "3": 12,
        },
        "dde_fire_minimum_card_burden": {
            "1": 23,
            "2": 12,
        },
        "changed_signatures": 27,
    }

    zero_to_one = [
        row
        for row in result["signatures"]
        if row["basic_ggf"]["minimum_cards"] == 0
        and row["dde_fire"]["minimum_cards"] == 1
    ]
    assert len(zero_to_one) == 5

    hydreigon = [
        row
        for row in zero_to_one
        if row["card_name"] == "Hydreigon"
        and row["attack_name"] == "Dragonblast"
    ]
    assert len(hydreigon) == 1
    assert hydreigon[0]["dde_fire"]["matched_units"] == 2

    print(result["counts"])


if __name__ == "__main__":
    main()
