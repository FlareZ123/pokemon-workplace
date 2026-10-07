from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.damage_calculation_kernel import (  # noqa: E402
    AttackDamage,
    AttackDamageMode,
    DamageContext,
    calculate_damage,
)


def main() -> None:
    ordered = calculate_damage(
        DamageContext(
            attack=AttackDamage(100),
            attacker_effect_modifiers=(30,),
            weakness_multiplier=2,
            resistance_reduction=30,
            defender_effect_modifiers=(-30,),
        )
    )
    assert ordered.step1_attack_damage == 100
    assert ordered.step2_attacker_effects == 130
    assert ordered.step3_weakness == 260
    assert ordered.step4_resistance == 230
    assert ordered.step5_defender_effects == 200
    assert ordered.final_damage == 200

    minus_zero = calculate_damage(
        DamageContext(
            attack=AttackDamage(20, AttackDamageMode.MINUS, 20),
            attacker_effect_modifiers=(30,),
        )
    )
    assert minus_zero.final_damage == 0
    assert minus_zero.stopped_after_step == 1
    assert minus_zero.step2_attacker_effects is None

    times_zero = calculate_damage(
        DamageContext(
            attack=AttackDamage(10, AttackDamageMode.TIMES, 0),
            attacker_effect_modifiers=(30,),
        )
    )
    assert times_zero.final_damage == 0
    assert times_zero.stopped_after_step == 1

    resistance_zero = calculate_damage(
        DamageContext(
            attack=AttackDamage(30),
            resistance_reduction=30,
            defender_effect_modifiers=(50,),
        )
    )
    assert resistance_zero.final_damage == 0
    assert resistance_zero.stopped_after_step == 4
    assert resistance_zero.step5_defender_effects is None

    benched = calculate_damage(
        DamageContext(
            attack=AttackDamage(50),
            weakness_multiplier=2,
            resistance_reduction=30,
            ignore_weakness_resistance=True,
        )
    )
    assert benched.final_damage == 50

    prevented = calculate_damage(
        DamageContext(
            attack=AttackDamage(80),
            defender_effect_modifiers=(-30,),
            prevent_all_damage=True,
        )
    )
    assert prevented.step5_defender_effects == 50
    assert prevented.final_damage == 0
    assert prevented.prevention_applied
    assert prevented.stopped_after_step == 6

    sonic_edge = calculate_damage(
        DamageContext(
            attack=AttackDamage(100),
            defender_effect_modifiers=(-30,),
            prevent_all_damage=True,
            ignore_defender_effects=True,
        )
    )
    assert sonic_edge.step5_defender_effects == 100
    assert sonic_edge.final_damage == 100
    assert not sonic_edge.prevention_applied

    weakness_still_exists = calculate_damage(
        DamageContext(
            attack=AttackDamage(100),
            weakness_multiplier=2,
            defender_effect_modifiers=(-30,),
            ignore_defender_effects=True,
        )
    )
    assert weakness_still_exists.final_damage == 200

    weakness_removed_upstream = calculate_damage(
        DamageContext(
            attack=AttackDamage(100),
            weakness_multiplier=None,
            ignore_defender_effects=True,
        )
    )
    assert weakness_removed_upstream.final_damage == 100

    print(
        {
            "ordered": ordered.final_damage,
            "minus_zero": minus_zero.final_damage,
            "times_zero": times_zero.final_damage,
            "benched": benched.final_damage,
            "prevented": prevented.final_damage,
            "sonic_edge": sonic_edge.final_damage,
        }
    )


if __name__ == "__main__":
    main()
