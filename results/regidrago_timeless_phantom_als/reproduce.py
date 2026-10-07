from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon  # noqa: E402
from position_effect_profile_compiler import (  # noqa: E402
    PositionEffectKind,
    compile_position_effect_profiles,
)
from regidrago_timeless_phantom_als import (  # noqa: E402
    execute_timeless_phantom_line,
)


def card(set_id: str, card_id: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def opponent_board():
    return make_board(
        make_pokemon("second", "Second Target"),
        (make_pokemon("first", "First Target"),),
    )


def main() -> None:
    regidrago = card("swsh12", "swsh12-136")
    dialga = card("sm5", "sm5-100")
    dragapult = card("sv6", "sv6-130")

    apex = next(
        attack for attack in regidrago["attacks"]
        if attack["name"] == "Apex Dragon"
    )
    timeless = next(
        attack for attack in dialga["attacks"]
        if attack["name"] == "Timeless-GX"
    )
    phantom = next(
        attack for attack in dragapult["attacks"]
        if attack["name"] == "Phantom Dive"
    )

    assert (regidrago.get("legalities") or {}).get("expanded") == "Legal"
    assert (dialga.get("legalities") or {}).get("expanded") == "Legal"
    assert (dragapult.get("legalities") or {}).get("expanded") == "Legal"
    assert regidrago["types"] == ["Dragon"]
    assert dialga["types"] == ["Dragon"]
    assert dragapult["types"] == ["Dragon"]
    assert apex["text"] == (
        "Choose an attack from a Dragon Pokémon in your discard pile "
        "and use it as this attack."
    )
    assert timeless["damage"] == "150"
    assert "Take another turn after this one." in timeless["text"]
    assert "Skip the between-turns step." in timeless["text"]
    assert phantom["damage"] == "200"
    assert "Put 6 damage counters" in phantom["text"]

    profiles = compile_position_effect_profiles(ROOT / "resources")
    boss = next(profile for profile in profiles if profile.card_id == "swsh2-154")
    assert boss.action_class == "Supporter"
    assert boss.kind == PositionEffectKind.TARGETED_GUST

    actor_board = make_board(make_pokemon("regidrago", "Regidrago VSTAR"))

    witness = execute_timeless_phantom_line(
        actor_board,
        opponent_board(),
        first_target_id="first",
        second_target_id="second",
        hp_by_object_id={"first": 180, "second": 200},
        boss_profile=boss,
    )
    assert witness is not None
    assert witness.extra_turn_supporter_available
    assert witness.first_attack_knocked_out_ids == ()
    assert witness.board_after_timeless.active_id == "first"
    assert witness.board_after_timeless.get("first").damage_counters == 15
    assert witness.board_after_second_gust.active_id == "second"
    assert witness.board_after_second_gust.get("first").damage_counters == 15
    assert set(witness.final_attack_knocked_out_ids) == {"first", "second"}
    assert witness.final_board.get("first").damage_counters == 21
    assert witness.final_board.get("second").damage_counters == 20

    double_ko_pairs = 0
    for first_hp in range(10, 321, 10):
        for second_hp in range(10, 321, 10):
            result = execute_timeless_phantom_line(
                actor_board,
                opponent_board(),
                first_target_id="first",
                second_target_id="second",
                hp_by_object_id={
                    "first": first_hp,
                    "second": second_hp,
                },
                boss_profile=boss,
            )
            actual = (
                result is not None
                and {"first", "second"}.issubset(
                    result.final_attack_knocked_out_ids
                )
            )
            expected = 160 <= first_hp <= 210 and second_hp <= 200
            assert actual == expected, (first_hp, second_hp, result)
            if actual:
                double_ko_pairs += 1

    assert double_ko_pairs == 120

    too_small = execute_timeless_phantom_line(
        actor_board,
        opponent_board(),
        first_target_id="first",
        second_target_id="second",
        hp_by_object_id={"first": 150, "second": 200},
        boss_profile=boss,
    )
    assert too_small is None

    too_large = execute_timeless_phantom_line(
        actor_board,
        opponent_board(),
        first_target_id="first",
        second_target_id="second",
        hp_by_object_id={"first": 220, "second": 200},
        boss_profile=boss,
    )
    assert too_large is not None
    assert too_large.final_attack_knocked_out_ids == ("second",)

    print(
        {
            "double_ko_hp_pairs": double_ko_pairs,
            "first_target_hp_window": [160, 210],
            "second_target_hp_ceiling": 200,
        }
    )


if __name__ == "__main__":
    main()
