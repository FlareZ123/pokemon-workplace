"""Reproduce temporal asymmetry among Special Conditions."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from special_condition_state import (  # noqa: E402
    ConditionInstance,
    ConditionKind,
    regular_condition,
)
from timed_special_conditions import (  # noqa: E402
    TimedConditionState,
    apply_timed_condition,
    resolve_basic_checkup,
)


def main() -> None:
    paralyzed = apply_timed_condition(
        TimedConditionState("A"),
        regular_condition(ConditionKind.PARALYZED),
        applied_turn_serial=10,
    )
    immediate = resolve_basic_checkup(
        paralyzed,
        completed_turn_player="B",
        completed_turn_serial=10,
    )
    assert immediate.next_state.get(ConditionKind.PARALYZED) is not None

    after_owner_turn = resolve_basic_checkup(
        immediate.next_state,
        completed_turn_player="A",
        completed_turn_serial=11,
    )
    assert after_owner_turn.next_state.get(ConditionKind.PARALYZED) is None

    self_paralyzed = apply_timed_condition(
        TimedConditionState("A"),
        regular_condition(ConditionKind.PARALYZED),
        applied_turn_serial=20,
    )
    same_turn_checkup = resolve_basic_checkup(
        self_paralyzed,
        completed_turn_player="A",
        completed_turn_serial=20,
    )
    assert same_turn_checkup.next_state.get(ConditionKind.PARALYZED) is not None
    later_owner_checkup = resolve_basic_checkup(
        same_turn_checkup.next_state,
        completed_turn_player="A",
        completed_turn_serial=22,
    )
    assert later_owner_checkup.next_state.get(ConditionKind.PARALYZED) is None

    status = TimedConditionState("A")
    status = apply_timed_condition(
        status,
        regular_condition(ConditionKind.POISONED),
        applied_turn_serial=30,
    )
    status = apply_timed_condition(
        status,
        regular_condition(ConditionKind.BURNED),
        applied_turn_serial=30,
    )
    status = apply_timed_condition(
        status,
        regular_condition(ConditionKind.ASLEEP),
        applied_turn_serial=30,
    )
    first_checkup = resolve_basic_checkup(
        status,
        completed_turn_player="B",
        completed_turn_serial=30,
        burn_coin_heads=True,
        asleep_coin_heads=True,
    )
    assert first_checkup.damage_counter_events == (
        (ConditionKind.POISONED, 1),
        (ConditionKind.BURNED, 2),
    )
    assert first_checkup.total_damage_counters == 3
    assert first_checkup.next_state.get(ConditionKind.POISONED) is not None
    assert first_checkup.next_state.get(ConditionKind.BURNED) is None
    assert first_checkup.next_state.get(ConditionKind.ASLEEP) is None

    confused = apply_timed_condition(
        TimedConditionState("A"),
        ConditionInstance(ConditionKind.CONFUSED, base_damage_counters=3),
        applied_turn_serial=40,
    )
    confused_checkup = resolve_basic_checkup(
        confused,
        completed_turn_player="B",
        completed_turn_serial=40,
    )
    assert confused_checkup.damage_counter_events == ()
    assert confused_checkup.next_state.get(ConditionKind.CONFUSED) is not None

    print("timed Special Condition regressions passed")


if __name__ == "__main__":
    main()
