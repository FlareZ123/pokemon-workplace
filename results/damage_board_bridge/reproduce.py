from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon  # noqa: E402
from damage_board_bridge import (  # noqa: E402
    EffectCounterPlacement,
    resolve_attack_damage_phase,
)
from damage_calculation_kernel import AttackDamage, DamageContext  # noqa: E402


def phantom_dive_card() -> dict:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sv6.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == "sv6-130")


def make_target_board():
    return make_board(
        make_pokemon("active", "Target Active"),
        (
            make_pokemon("bench60", "60 HP Bench"),
            make_pokemon("bench100", "100 HP Bench"),
        ),
    )


def main() -> None:
    dragapult = phantom_dive_card()
    phantom = next(
        attack
        for attack in dragapult["attacks"]
        if attack["name"] == "Phantom Dive"
    )
    assert dragapult["hp"] == "320"
    assert (dragapult.get("legalities") or {}).get("expanded") == "Legal"
    assert phantom["damage"] == "200"
    assert phantom["text"] == (
        "Put 6 damage counters on your opponent's Benched Pokémon "
        "in any way you like."
    )

    hp = {"active": 200, "bench60": 60, "bench100": 100}
    baseline = resolve_attack_damage_phase(
        make_target_board(),
        damage_target_id="active",
        damage_context=DamageContext(attack=AttackDamage(200)),
        counter_placements=(EffectCounterPlacement("bench60", 6),),
        hp_by_object_id=hp,
    )
    assert baseline.board.get("active").damage_counters == 20
    assert baseline.board.get("bench60").damage_counters == 6
    assert baseline.knocked_out_ids == ("active", "bench60")

    immune_bench = resolve_attack_damage_phase(
        make_target_board(),
        damage_target_id="active",
        damage_context=DamageContext(attack=AttackDamage(200)),
        counter_placements=(
            EffectCounterPlacement(
                "bench60",
                6,
                prevent_effects_of_attacks=True,
            ),
        ),
        hp_by_object_id=hp,
    )
    assert immune_bench.board.get("bench60").damage_counters == 0
    assert immune_bench.counter_outcomes[0].requested == 6
    assert immune_bench.counter_outcomes[0].placed == 0
    assert immune_bench.knocked_out_ids == ("active",)

    prevent_active_damage = resolve_attack_damage_phase(
        make_target_board(),
        damage_target_id="active",
        damage_context=DamageContext(
            attack=AttackDamage(200),
            prevent_all_damage=True,
        ),
        counter_placements=(EffectCounterPlacement("bench60", 6),),
        hp_by_object_id=hp,
    )
    assert prevent_active_damage.damage_result.final_damage == 0
    assert prevent_active_damage.board.get("active").damage_counters == 0
    assert prevent_active_damage.board.get("bench60").damage_counters == 6
    assert prevent_active_damage.knocked_out_ids == ("bench60",)

    ignore_active_effects = resolve_attack_damage_phase(
        make_target_board(),
        damage_target_id="active",
        damage_context=DamageContext(
            attack=AttackDamage(200),
            prevent_all_damage=True,
            ignore_defender_effects=True,
        ),
        counter_placements=(EffectCounterPlacement("bench60", 6),),
        hp_by_object_id=hp,
    )
    assert ignore_active_effects.damage_result.final_damage == 200
    assert ignore_active_effects.knocked_out_ids == ("active", "bench60")

    print(
        {
            "phantom_dive": {
                "damage": phantom["damage"],
                "counter_text": phantom["text"],
            },
            "baseline_kos": baseline.knocked_out_ids,
            "immune_bench_kos": immune_bench.knocked_out_ids,
            "prevent_active_damage_kos": prevent_active_damage.knocked_out_ids,
        }
    )


if __name__ == "__main__":
    main()
