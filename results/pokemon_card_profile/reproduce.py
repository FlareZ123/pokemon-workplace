from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon  # noqa: E402
from pokemon_card_profile import (  # noqa: E402
    build_pokemon_card_profile_index,
    compile_pokemon_card_profile,
    hp_by_board_object,
)
from type_modifier_catalog import TypeModifierKind  # noqa: E402


def card(set_id: str, card_id: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def main() -> None:
    profiles = build_pokemon_card_profile_index(ROOT / "resources")
    assert len(profiles) == 12504

    dragapult = profiles["sv6-130"]
    assert dragapult.name == "Dragapult ex"
    assert dragapult.hp == 320
    assert dragapult.types == ("Dragon",)
    assert dragapult.prize_value == 2

    dialga = profiles["sm5-100"]
    assert dialga.hp == 180
    assert dialga.prize_value == 2
    assert dialga.weaknesses[0].energy_type == "Fairy"
    assert dialga.weaknesses[0].modifier.kind == TypeModifierKind.MULTIPLY
    assert dialga.weaknesses[0].modifier.amount == 2

    flying = profiles["cel25-7"]
    assert flying.hp == 310
    assert flying.prize_value == 3
    assert flying.resistances[0].modifier.kind == TypeModifierKind.SUBTRACT
    assert flying.resistances[0].modifier.amount == 30

    uxie = compile_pokemon_card_profile(card("me55c", "me55c-43"))
    assert uxie.weaknesses[0].modifier.kind == TypeModifierKind.ADD
    assert uxie.weaknesses[0].modifier.amount == 20

    murkrow = compile_pokemon_card_profile(card("me55", "me55-93"))
    assert murkrow.resistances[0].energy_type == "Fighting"
    assert murkrow.resistances[0].modifier.kind == TypeModifierKind.SUBTRACT
    assert murkrow.resistances[0].modifier.amount == 30

    board = make_board(
        make_pokemon(
            "active",
            "Dialga-GX",
            print_id="sm5-100",
        ),
        (
            make_pokemon(
                "bench",
                "Dragapult ex",
                print_id="sv6-130",
            ),
        ),
    )
    assert hp_by_board_object(board, profiles) == {
        "active": 180,
        "bench": 320,
    }

    print(
        {
            "profiles": len(profiles),
            "dragapult": dragapult,
            "dialga": dialga,
            "flying_pikachu_vmax": flying,
            "uxie": uxie,
            "murkrow": murkrow,
        }
    )


if __name__ == "__main__":
    main()
