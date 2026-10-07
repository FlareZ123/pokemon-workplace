from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from damage_calculation_kernel import AttackDamage, DamageContext, calculate_damage  # noqa: E402
from damage_reaction_special_condition_bridge import (  # noqa: E402
    apply_damage_triggered_condition,
)
from special_condition_state import (  # noqa: E402
    ConditionKind,
    SpecialConditionState,
    apply_condition,
    regular_condition,
)


def card(set_id: str, card_id: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def main() -> None:
    armarouge = card("sv3", "sv3-44")
    scorching = next(
        ability for ability in armarouge["abilities"]
        if ability["name"] == "Scorching Armor"
    )
    assert "Attacking Pokémon is now Burned" in scorching["text"]

    hypnotizer = card("me2pt5", "me2pt5-206")
    assert "Attacking Pokémon is now Asleep" in hypnotizer["rules"][0]

    damage = calculate_damage(
        DamageContext(attack=AttackDamage(50))
    )
    prevented = calculate_damage(
        DamageContext(
            attack=AttackDamage(50),
            prevent_all_damage=True,
        )
    )

    initial = apply_condition(
        SpecialConditionState(),
        regular_condition(ConditionKind.CONFUSED),
    )
    burned = apply_damage_triggered_condition(
        initial,
        damage,
        ConditionKind.BURNED,
        source_label="Scorching Armor",
    )
    assert burned.triggered
    assert burned.state.get(ConditionKind.BURNED) is not None
    assert burned.state.get(ConditionKind.CONFUSED) is not None

    asleep = apply_damage_triggered_condition(
        burned.state,
        damage,
        ConditionKind.ASLEEP,
        source_label="Team Rocket's Hypnotizer",
    )
    assert asleep.triggered
    assert asleep.state.get(ConditionKind.BURNED) is not None
    assert asleep.state.get(ConditionKind.ASLEEP) is not None
    assert asleep.state.get(ConditionKind.CONFUSED) is None

    blocked = apply_damage_triggered_condition(
        initial,
        prevented,
        ConditionKind.POISONED,
    )
    assert not blocked.triggered
    assert blocked.state == initial

    print(
        {
            "after_burn": tuple(
                row.kind.value for row in burned.state.conditions
            ),
            "after_sleep": tuple(
                row.kind.value for row in asleep.state.conditions
            ),
            "prevented_trigger": blocked.triggered,
        }
    )


if __name__ == "__main__":
    main()
