from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_state_kernel import (  # noqa: E402
    BenchState,
    add_core,
    add_support,
    change_capacity,
    next_turn,
    release_resident,
)


def with_four_core(capacity: int = 5) -> BenchState:
    state = BenchState(capacity=capacity)
    for i in range(4):
        next_state = add_core(state, name=f"core-{i}", retention_value=10.0)
        assert next_state is not None
        state = next_state
    return state


def main() -> None:
    base = with_four_core()

    hand = add_support(
        base,
        name="support-a",
        retention_value=2.0,
        trigger_name="bench-trigger",
        entry_mode="hand",
    )
    assert hand is not None
    assert hand.trigger_count("bench-trigger") == 1

    direct = add_support(
        base,
        name="support-direct",
        retention_value=2.0,
        trigger_name="bench-trigger",
        entry_mode="direct",
    )
    assert direct is not None
    assert direct.trigger_count("bench-trigger") == 0

    blocked = add_support(
        hand,
        name="support-b",
        retention_value=2.0,
        trigger_name="bench-trigger",
        entry_mode="hand",
    )
    assert blocked is None

    item_freed = release_resident(hand, resident_index=4, action_class="item")
    assert item_freed is not None
    second = add_support(
        item_freed,
        name="support-b",
        retention_value=2.0,
        trigger_name="bench-trigger",
        entry_mode="hand",
    )
    assert second is not None
    assert second.turn == 1
    assert second.trigger_count("bench-trigger") == 2

    supporter_freed = release_resident(hand, resident_index=4, action_class="supporter")
    assert supporter_freed is not None and supporter_freed.supporter_used
    second_after_supporter = add_support(
        supporter_freed,
        name="support-c",
        retention_value=2.0,
        trigger_name="bench-trigger",
        entry_mode="hand",
    )
    assert second_after_supporter is not None
    assert release_resident(
        second_after_supporter,
        resident_index=4,
        action_class="supporter",
    ) is None

    attack_freed = release_resident(hand, resident_index=4, action_class="attack")
    assert attack_freed is not None and attack_freed.turn_ended
    assert add_support(
        attack_freed,
        name="support-d",
        retention_value=2.0,
        trigger_name="bench-trigger",
        entry_mode="hand",
    ) is None
    attack_next = next_turn(attack_freed)
    after_attack = add_support(
        attack_next,
        name="support-d",
        retention_value=2.0,
        trigger_name="bench-trigger",
        entry_mode="hand",
    )
    assert after_attack is not None and after_attack.turn == 2

    expanded = with_four_core(capacity=8)
    for name in ("s1", "s2", "s3"):
        next_state = add_support(
            expanded,
            name=name,
            retention_value=2.0,
            trigger_name="bench-trigger",
            entry_mode="hand",
        )
        assert next_state is not None
        expanded = next_state
    assert len(expanded.residents) == 7
    assert expanded.trigger_count("bench-trigger") == 3

    five, discarded_five = change_capacity(expanded, new_capacity=5)
    assert [row.name for row in discarded_five] == ["s2", "s3"]
    assert len(five.residents) == 5
    four, discarded_four = change_capacity(five, new_capacity=4)
    assert [row.name for row in discarded_four] == ["s1"]
    assert all(row.role == "core" for row in four.residents)

    three, discarded_three = change_capacity(four, new_capacity=3)
    assert len(discarded_three) == 1
    assert discarded_three[0].role == "core"

    print("typed Bench-state regressions passed")
    print("hand triggers:", hand.trigger_counts)
    print("direct triggers:", direct.trigger_counts)
    print("item-chain triggers:", second.trigger_counts)
    print("expanded -> 5 discarded:", [row.name for row in discarded_five])
    print("5 -> 4 discarded:", [row.name for row in discarded_four])
    print("4 -> 3 discarded:", [row.name for row in discarded_three])


if __name__ == "__main__":
    main()
