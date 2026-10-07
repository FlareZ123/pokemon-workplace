from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attached_energy_cards import (
    AttachedEnergyCard,
    attack_ready,
    minimum_basic_named_discard_outcomes,
    minimum_generic_discard_outcomes,
)
from energy_action_budget import WILDCARD


def main() -> None:
    dde = AttachedEnergyCard(
        key="dde-1",
        card_name="Double Dragon Energy",
        units=2,
        provided_symbols=frozenset({WILDCARD}),
    )
    fire = AttachedEnergyCard(
        key="fire-1",
        card_name="Basic Fire Energy",
        units=1,
        provided_symbols=frozenset({"R"}),
        basic_energy_name="Fire",
    )
    regidrago = (dde, fire)

    assert attack_ready(("G", "G", "R"), regidrago)

    generic_two = minimum_generic_discard_outcomes(regidrago, 2)
    assert generic_two["full"] is True
    assert generic_two["minimum_cards"] == 1
    assert generic_two["subsets"] == [[0]]
    assert [
        card.card_name for card in generic_two["remaining_states"][0]
    ] == ["Basic Fire Energy"]

    basic_fire = minimum_basic_named_discard_outcomes(
        regidrago,
        "Fire",
        1,
    )
    assert basic_fire["full"] is True
    assert basic_fire["subsets"] == [[1]]
    assert [
        card.card_name for card in basic_fire["remaining_states"][0]
    ] == ["Double Dragon Energy"]

    basic_psychic = minimum_basic_named_discard_outcomes(
        regidrago,
        "Psychic",
        1,
    )
    assert basic_psychic["full"] is False
    assert basic_psychic["minimum_cards"] == 0
    assert basic_psychic["remaining_states"] == (regidrago,)

    burned_grass = AttachedEnergyCard(
        key="grass-1",
        card_name="Basic Grass Energy",
        units=2,
        provided_symbols=frozenset({"R"}),
        basic_energy_name="Grass",
    )
    assert attack_ready(("R", "R"), (burned_grass,))
    assert burned_grass.matches_basic_named("Grass")
    assert not burned_grass.matches_basic_named("Fire")

    grass_discard = minimum_basic_named_discard_outcomes(
        (burned_grass,),
        "Grass",
        1,
    )
    assert grass_discard["full"] is True
    assert grass_discard["minimum_cards"] == 1
    assert grass_discard["remaining_states"] == ((),)

    fire_named_discard = minimum_basic_named_discard_outcomes(
        (burned_grass,),
        "Fire",
        1,
    )
    assert fire_named_discard["full"] is False
    assert fire_named_discard["minimum_cards"] == 0
    assert fire_named_discard["remaining_states"] == ((burned_grass,),)

    dce = AttachedEnergyCard(
        key="dce-1",
        card_name="Double Colorless Energy",
        units=2,
        provided_symbols=frozenset({"C"}),
    )
    assert attack_ready(
        ("L", "C", "C"),
        (dce,),
        reductions=(("L", 1),),
        target_tags={"Lightning"},
    )
    dce_discard = minimum_generic_discard_outcomes((dce,), 2)
    assert dce_discard["minimum_cards"] == 1
    assert dce_discard["remaining_states"] == ((),)

    print({
        "regidrago_ggf_ready": True,
        "generic_two_discards": ["Double Dragon Energy"],
        "basic_fire_discards": ["Basic Fire Energy"],
        "basic_psychic_discards": [],
        "burned_basic_grass": {
            "provides": "2 Fire Energy",
            "matches_basic_grass": True,
            "matches_basic_fire": False,
        },
        "dce_two_unit_discard_physical_cards": 1,
    })


if __name__ == "__main__":
    main()
