"""Source-grounded reproduction for the champion Shadow Rider connector fork."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY, POKEMON, PRINT_IDS, TRAINERS,
)
from tools.shadow_rider_dialga_connector_fork import (
    champion_results, validate_toy_worlds,
)


def card(root: Path, name: str) -> dict:
    card_id = PRINT_IDS[name]
    set_id = card_id.rsplit("-", 1)[0]
    collection = json.loads(
        (root / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(record for record in collection if record["id"] == card_id)


def reproduce() -> None:
    root = Path(__file__).resolve().parents[3]
    assert sum(POKEMON.values()) == 18
    assert sum(TRAINERS.values()) == 31
    assert sum(ENERGY.values()) == 11
    assert POKEMON["Dialga-GX"] == POKEMON["Mimikyu"] == 1
    assert POKEMON["Radiant Eternatus"] == 1
    assert POKEMON["Shadow Rider Calyrex VMAX"] == 4
    assert TRAINERS["Mysterious Treasure"] == TRAINERS["Fog Crystal"] == 4
    b = sum(POKEMON.values()) - 4 - 1 - 1 - 1
    excluded = b + 4 + 4 + 4 + 3
    assert (b, 60 - excluded) == (11, 34)
    assert card(root, "Dialga-GX")["types"] == ["Dragon"]
    assert "Basic" in card(root, "Dialga-GX")["subtypes"]
    assert any(a["name"] == "Timeless-GX" for a in card(root, "Dialga-GX")["attacks"])
    mimikyu = card(root, "Mimikyu")
    assert "Basic" in mimikyu["subtypes"] and mimikyu["types"] == ["Psychic"]
    assert any(a["name"] == "Copycat" for a in mimikyu["attacks"])
    radiant = card(root, "Radiant Eternatus")
    assert any(
        a["name"] == "Climactic Gate" and "your turn ends" in a["text"]
        for a in radiant["abilities"]
    )
    treasure = card(root, "Mysterious Treasure")["rules"][0]
    assert "Discard a card from your hand" in treasure
    assert "Psychic or Dragon Pokémon" in treasure
    fog = card(root, "Fog Crystal")["rules"][0]
    assert "Basic Psychic Pokémon" in fog

    validate_toy_worlds()
    actual = champion_results()
    basic_valid = Fraction(9797437, 11703240)
    expected_unconditional = {
        "fork": Fraction(58613434588753, 2525562843410880),
        "fog_available": Fraction(6503254679603, 789238388565900),
        "single_treasure_no_fog": Fraction(117252153997, 9395695101975),
        "single_treasure_with_fog": Fraction(3777849144421, 526158925710600),
        "dialga_draw": Fraction(122752793977, 39461919428295),
        "dialga_initial": Fraction(12394934255, 616743063104),
    }
    for key, expected in expected_unconditional.items():
        assert actual[key] == expected / basic_valid, (key, actual[key])
        print(f"{key}: {100*float(actual[key]):.9f}% of Basic-valid openings")
    print("SOURCE CHECKS AND ALL EXACT FRACTIONS PASSED")


if __name__ == "__main__":
    reproduce()
