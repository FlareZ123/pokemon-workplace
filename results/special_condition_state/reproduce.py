"""Reproduce typed Special Condition and Checkup scheduling regressions."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from special_condition_state import (  # noqa: E402
    CHECKUP_CONDITION_BLOCK,
    ConditionInstance,
    ConditionKind,
    ConditionModifier,
    ModifierMode,
    SpecialConditionState,
    apply_condition,
    checkup_conditions,
    effective_damage_counters,
    enumerate_checkup_schedules,
    expected_schedule_count,
    expand_checkup_schedule,
    legacy_name_projection,
    regular_condition,
)


def main() -> None:
    ordinary = apply_condition(
        SpecialConditionState(),
        regular_condition(ConditionKind.POISONED),
    )
    severe = apply_condition(
        SpecialConditionState(),
        ConditionInstance(
            ConditionKind.POISONED,
            base_damage_counters=4,
            source_label="Galarian Weezing — Severe Poison",
        ),
    )

    # The current board kernel's set-of-names representation aliases two
    # mechanically different Poisoned states.
    assert legacy_name_projection(ordinary) == frozenset({"Poisoned"})
    assert legacy_name_projection(severe) == frozenset({"Poisoned"})
    assert effective_damage_counters(ordinary, ConditionKind.POISONED) == 1
    assert effective_damage_counters(severe, ConditionKind.POISONED) == 4

    # Latest same-kind condition replaces the previous regular/irregular version.
    severe_then_regular = apply_condition(
        severe,
        regular_condition(ConditionKind.POISONED),
    )
    regular_then_severe = apply_condition(
        ordinary,
        ConditionInstance(ConditionKind.POISONED, base_damage_counters=4),
    )
    assert effective_damage_counters(severe_then_regular, ConditionKind.POISONED) == 1
    assert effective_damage_counters(regular_then_severe, ConditionKind.POISONED) == 4

    burned = apply_condition(
        SpecialConditionState(),
        regular_condition(ConditionKind.BURNED),
    )
    pyroar = ConditionModifier(
        ConditionKind.BURNED,
        4,
        ModifierMode.REPLACE_BASE,
        "Pyroar — Scorching Aura",
    )
    infernape = ConditionModifier(
        ConditionKind.BURNED,
        6,
        ModifierMode.REPLACE_BASE,
        "Infernape — Flaming Fighter",
    )
    magmortar = ConditionModifier(
        ConditionKind.BURNED,
        3,
        ModifierMode.ADD,
        "Magmortar — Magma Surge",
    )

    # Manual example: 4 base replacement + 3 additive = 7.
    assert effective_damage_counters(
        burned,
        ConditionKind.BURNED,
        (pyroar, magmortar),
    ) == 7

    # Highest base replacement applies once; additive modifiers remain additive.
    assert effective_damage_counters(
        burned,
        ConditionKind.BURNED,
        (pyroar, pyroar, infernape, magmortar),
    ) == 9

    mixed = SpecialConditionState()
    for kind in (
        ConditionKind.CONFUSED,
        ConditionKind.PARALYZED,
        ConditionKind.BURNED,
        ConditionKind.POISONED,
    ):
        mixed = apply_condition(mixed, regular_condition(kind))

    # Confused resolves on attack attempt rather than in the Checkup condition block.
    assert checkup_conditions(mixed) == (
        ConditionKind.POISONED,
        ConditionKind.BURNED,
        ConditionKind.PARALYZED,
    )

    effects = ("effect:A", "effect:B")
    schedules = enumerate_checkup_schedules(effects)
    assert len(schedules) == expected_schedule_count(len(effects)) == 6
    assert len(set(schedules)) == 6
    assert {schedule.index(CHECKUP_CONDITION_BLOCK) for schedule in schedules} == {0, 1, 2}

    # The condition block stays internally ordered and no effect can be inserted
    # between its condition steps by this timing rule.
    for schedule in schedules:
        expanded = expand_checkup_schedule(schedule, mixed)
        condition_positions = [
            index for index, token in enumerate(expanded)
            if token.startswith("condition:")
        ]
        assert condition_positions == list(
            range(condition_positions[0], condition_positions[0] + len(condition_positions))
        )
        condition_tokens = tuple(expanded[index] for index in condition_positions)
        assert condition_tokens == (
            "condition:Poisoned",
            "condition:Burned",
            "condition:Paralyzed",
        )

    three_effect_schedules = enumerate_checkup_schedules(("A", "B", "C"))
    assert len(three_effect_schedules) == expected_schedule_count(3) == 24

    print("special-condition payload and Checkup scheduling regressions passed")


if __name__ == "__main__":
    main()
