from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from damage_calculation_kernel import AttackDamage, DamageContext, calculate_damage  # noqa: E402
from pokemon_card_profile import build_pokemon_card_profile_index  # noqa: E402
from profile_damage_context import resolve_printed_type_stages  # noqa: E402


def damage(base: int, stages) -> int:
    return calculate_damage(
        DamageContext(
            attack=AttackDamage(base),
            weakness_multiplier=stages.weakness_multiplier,
            weakness_addition=stages.weakness_addition,
            resistance_reduction=stages.resistance_reduction,
        )
    ).final_damage


def main() -> None:
    profiles = build_pokemon_card_profile_index(ROOT / "resources")

    uxie = profiles["me55c-43"]
    uxie_stages = resolve_printed_type_stages(("Psychic",), uxie)
    assert uxie_stages.weakness_multiplier is None
    assert uxie_stages.weakness_addition == 20
    assert damage(100, uxie_stages) == 120

    dialga = profiles["sm5-100"]
    dialga_stages = resolve_printed_type_stages(("Fairy",), dialga)
    assert dialga_stages.weakness_multiplier == 2
    assert dialga_stages.weakness_addition == 0
    assert damage(100, dialga_stages) == 200

    flying = profiles["cel25-7"]
    flying_stages = resolve_printed_type_stages(("Fighting",), flying)
    assert flying_stages.resistance_reduction == 30
    assert damage(100, flying_stages) == 70

    no_match = resolve_printed_type_stages(("Water",), flying)
    assert no_match.weakness_multiplier is None
    assert no_match.weakness_addition == 0
    assert no_match.resistance_reduction == 0
    assert damage(100, no_match) == 100

    resistance_removed = resolve_printed_type_stages(
        ("Fighting",),
        flying,
        resistance_enabled=False,
    )
    assert resistance_removed.resistance_reduction == 0
    assert damage(100, resistance_removed) == 100

    murkrow = profiles["me55-93"]
    murkrow_stages = resolve_printed_type_stages(("Fighting",), murkrow)
    assert murkrow_stages.resistance_reduction == 30
    assert damage(100, murkrow_stages) == 70

    print(
        {
            "uxie_psychic": damage(100, uxie_stages),
            "dialga_fairy": damage(100, dialga_stages),
            "flying_pikachu_fighting": damage(100, flying_stages),
            "murkrow_fighting": damage(100, murkrow_stages),
        }
    )


if __name__ == "__main__":
    main()
