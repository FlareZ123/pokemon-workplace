from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.apex_dragon_special_energy_burden import build  # noqa: E402
from tools.energy_discard_solver import (  # noqa: E402
    ENERGY_TYPES,
    minimum_basic_named_card_subsets,
    minimum_card_subsets_generic,
    minimum_card_subsets_typed,
)


def main() -> None:
    dde = {
        "name": "Double Dragon Energy",
        "units": 2,
        "types": list(ENERGY_TYPES),
        "basic": False,
    }
    fire = {
        "name": "Basic Fire",
        "units": 1,
        "types": ["Fire"],
        "basic": True,
        "basic_energy_name": "Fire",
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

    basic_psychic = minimum_basic_named_card_subsets(
        [dde, fire],
        "Psychic",
        1,
    )
    assert basic_psychic["full"] is False
    assert basic_psychic["matched_cards"] == 0
    assert basic_psychic["minimum_cards"] == 0
    assert basic_psychic["subsets"] == [[]]

    burned_grass = {
        "name": "Basic Grass Energy",
        "units": 2,
        "types": ["Fire"],
        "basic": True,
        "basic_energy_name": "Grass",
    }
    basic_grass = minimum_basic_named_card_subsets(
        [burned_grass],
        "Grass",
        1,
    )
    assert basic_grass["full"] is True
    assert basic_grass["minimum_cards"] == 1

    basic_fire = minimum_basic_named_card_subsets(
        [burned_grass],
        "Fire",
        1,
    )
    assert basic_fire["full"] is False
    assert basic_fire["minimum_cards"] == 0

    converted_fire_units = minimum_card_subsets_typed(
        [burned_grass],
        ["Fire", "Fire"],
    )
    assert converted_fire_units["full"] is True
    assert converted_fire_units["minimum_cards"] == 1

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
            "0": 1,
            "1": 22,
            "2": 12,
        },
        "changed_signatures": 26,
    }

    zero_to_one = [
        row
        for row in result["signatures"]
        if row["basic_ggf"]["minimum_cards"] == 0
        and row["dde_fire"]["minimum_cards"] == 1
    ]
    assert len(zero_to_one) == 4

    hydreigon = [
        row
        for row in zero_to_one
        if row["card_name"] == "Hydreigon"
        and row["attack_name"] == "Dragonblast"
    ]
    assert len(hydreigon) == 1
    assert hydreigon[0]["dde_fire"]["matched_units"] == 2

    photon = [
        row
        for row in result["signatures"]
        if row["card_name"] == "Ultra Necrozma-GX"
        and row["attack_name"] == "Photon Geyser"
    ]
    assert len(photon) == 1
    assert photon[0]["first_discard"]["basic_only"] is True
    assert photon[0]["basic_ggf"]["minimum_cards"] == 0
    assert photon[0]["dde_fire"]["minimum_cards"] == 0
    assert photon[0]["dde_fire"]["matched_units"] == 0

    print(result["counts"])


if __name__ == "__main__":
    main()
