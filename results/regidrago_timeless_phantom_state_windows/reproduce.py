"""Reproduce generalized damage-state windows for the Regidrago ALS."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon  # noqa: E402
from damage_calculation_kernel import AttackDamage, DamageContext  # noqa: E402
from position_effect_profile_compiler import (  # noqa: E402
    PositionEffectKind,
    compile_position_effect_profiles,
)
from regidrago_timeless_phantom_als import (  # noqa: E402
    derive_timeless_phantom_hp_window,
    derive_timeless_phantom_prior_damage_band,
    execute_timeless_phantom_line,
)


def _card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == card_id)


def _opponent_board(
    *,
    first_prior_damage: int = 0,
    second_prior_damage: int = 0,
):
    return make_board(
        make_pokemon(
            "second",
            "Second Target",
            damage_counters=second_prior_damage // 10,
        ),
        (
            make_pokemon(
                "first",
                "First Target",
                damage_counters=first_prior_damage // 10,
            ),
        ),
    )


def _double_ko(
    *,
    first_hp: int,
    second_hp: int,
    first_prior_damage: int,
    second_prior_damage: int,
    timeless_context: DamageContext | None,
    phantom_context: DamageContext | None,
    boss,
) -> bool:
    actor = make_board(make_pokemon("regidrago", "Regidrago VSTAR"))
    result = execute_timeless_phantom_line(
        actor,
        _opponent_board(
            first_prior_damage=first_prior_damage,
            second_prior_damage=second_prior_damage,
        ),
        first_target_id="first",
        second_target_id="second",
        hp_by_object_id={"first": first_hp, "second": second_hp},
        boss_profile=boss,
        timeless_damage_context=timeless_context,
        phantom_damage_context=phantom_context,
    )
    return (
        result is not None
        and {"first", "second"}.issubset(result.final_attack_knocked_out_ids)
    )


def main() -> None:
    profiles = compile_position_effect_profiles(ROOT / "resources")
    boss = next(profile for profile in profiles if profile.card_id == "swsh2-154")
    assert boss.kind == PositionEffectKind.TARGETED_GUST

    baseline = derive_timeless_phantom_hp_window()
    assert baseline.first_hp_survival_threshold == 150
    assert baseline.first_hp_ko_ceiling == 210
    assert baseline.second_hp_ko_ceiling == 200

    damaged = derive_timeless_phantom_hp_window(
        first_prior_damage=40,
        second_prior_damage=30,
    )
    assert damaged.first_hp_survival_threshold == 190
    assert damaged.first_hp_ko_ceiling == 250
    assert damaged.second_hp_ko_ceiling == 230

    timeless_minus_30 = DamageContext(
        attack=AttackDamage(150),
        defender_effect_modifiers=(-30,),
    )
    reduced = derive_timeless_phantom_hp_window(
        timeless_damage_context=timeless_minus_30,
    )
    assert reduced.first_hp_survival_threshold == 120
    assert reduced.first_hp_ko_ceiling == 180

    phantom_minus_40 = DamageContext(
        attack=AttackDamage(200),
        defender_effect_modifiers=(-40,),
    )
    reduced_second = derive_timeless_phantom_hp_window(
        phantom_damage_context=phantom_minus_40,
    )
    assert reduced_second.second_hp_ko_ceiling == 160

    cases = (
        (0, 0, None, None),
        (40, 30, None, None),
        (0, 0, timeless_minus_30, None),
        (40, 30, timeless_minus_30, phantom_minus_40),
    )

    for (
        first_prior_damage,
        second_prior_damage,
        timeless_context,
        phantom_context,
    ) in cases:
        window = derive_timeless_phantom_hp_window(
            first_prior_damage=first_prior_damage,
            second_prior_damage=second_prior_damage,
            timeless_damage_context=timeless_context,
            phantom_damage_context=phantom_context,
        )

        for first_hp in range(10, 361, 10):
            for second_hp in range(10, 361, 10):
                if (
                    first_hp <= first_prior_damage
                    or second_hp <= second_prior_damage
                ):
                    continue

                expected = (
                    window.first_hp_survival_threshold < first_hp
                    <= window.first_hp_ko_ceiling
                    and second_hp <= window.second_hp_ko_ceiling
                )
                actual = _double_ko(
                    first_hp=first_hp,
                    second_hp=second_hp,
                    first_prior_damage=first_prior_damage,
                    second_prior_damage=second_prior_damage,
                    timeless_context=timeless_context,
                    phantom_context=phantom_context,
                    boss=boss,
                )
                assert actual == expected, (
                    first_hp,
                    second_hp,
                    first_prior_damage,
                    second_prior_damage,
                    window,
                )

    targets = (
        ("Iron Thorns ex", "sv6-77", 230, (20, 70), 30),
        ("Regidrago VSTAR", "swsh12-136", 280, (70, 120), 80),
        ("Shadow Rider Calyrex VMAX", "swsh6-75", 320, (110, 160), 120),
    )
    for name, card_id, hp, first_band, second_min in targets:
        card = _card(card_id)
        assert card["name"] == name
        assert int(card["hp"]) == hp
        assert (card.get("legalities") or {}).get("expanded") == "Legal"

        band = derive_timeless_phantom_prior_damage_band(
            first_target_hp=hp,
            second_target_hp=hp,
        )
        assert band is not None
        assert (
            band.first_target_min,
            band.first_target_max,
        ) == first_band
        assert band.second_target_min == second_min

        assert _double_ko(
            first_hp=hp,
            second_hp=200,
            first_prior_damage=band.first_target_min,
            second_prior_damage=0,
            timeless_context=None,
            phantom_context=None,
            boss=boss,
        )
        assert _double_ko(
            first_hp=hp,
            second_hp=200,
            first_prior_damage=band.first_target_max,
            second_prior_damage=0,
            timeless_context=None,
            phantom_context=None,
            boss=boss,
        )
        if band.first_target_min >= 10:
            assert not _double_ko(
                first_hp=hp,
                second_hp=200,
                first_prior_damage=band.first_target_min - 10,
                second_prior_damage=0,
                timeless_context=None,
                phantom_context=None,
                boss=boss,
            )
        assert not _double_ko(
            first_hp=hp,
            second_hp=200,
            first_prior_damage=band.first_target_max + 10,
            second_prior_damage=0,
            timeless_context=None,
            phantom_context=None,
            boss=boss,
        )

        assert _double_ko(
            first_hp=180,
            second_hp=hp,
            first_prior_damage=0,
            second_prior_damage=band.second_target_min,
            timeless_context=None,
            phantom_context=None,
            boss=boss,
        )
        if band.second_target_min >= 10:
            assert not _double_ko(
                first_hp=180,
                second_hp=hp,
                first_prior_damage=0,
                second_prior_damage=band.second_target_min - 10,
                timeless_context=None,
                phantom_context=None,
                boss=boss,
            )

    actor = make_board(make_pokemon("regidrago", "Regidrago VSTAR"))
    immune = execute_timeless_phantom_line(
        actor,
        _opponent_board(),
        first_target_id="first",
        second_target_id="second",
        hp_by_object_id={"first": 180, "second": 200},
        boss_profile=boss,
        first_target_prevent_phantom_effects=True,
    )
    assert immune is not None
    assert immune.final_board.get("first").damage_counters == 15
    assert immune.final_attack_knocked_out_ids == ("second",)

    print(
        {
            "baseline_first_window": [
                baseline.first_hp_survival_threshold + 10,
                baseline.first_hp_ko_ceiling,
            ],
            "prior_damage_first_window": [
                damaged.first_hp_survival_threshold + 10,
                damaged.first_hp_ko_ceiling,
            ],
            "timeless_minus_30_first_window": [
                reduced.first_hp_survival_threshold + 10,
                reduced.first_hp_ko_ceiling,
            ],
            "phantom_minus_40_second_ceiling": (
                reduced_second.second_hp_ko_ceiling
            ),
            "effect_immunity_blocks_bench_counters": True,
            "named_target_prior_damage": {
                name: {
                    "hp": hp,
                    "first_target_band": list(first_band),
                    "second_target_min": second_min,
                }
                for name, _card_id, hp, first_band, second_min in targets
            },
        }
    )


if __name__ == "__main__":
    main()
