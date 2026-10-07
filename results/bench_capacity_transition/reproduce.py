from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_capacity_transition import (  # noqa: E402
    BenchOccupant,
    minimum_role_losses,
    resolve_capacity_transition,
)


def main() -> None:
    for core in range(0, 9):
        for support in range(0, 9 - core):
            occupants = tuple(
                [BenchOccupant(f"core-{i}", "core", 10.0) for i in range(core)]
                + [BenchOccupant(f"support-{i}", "support", 2.0) for i in range(support)]
            )
            old_capacity = max(8, len(occupants))
            for capacity in range(0, 9):
                result = resolve_capacity_transition(
                    occupants,
                    old_capacity=old_capacity,
                    new_capacity=capacity,
                )
                expected_core, expected_support = minimum_role_losses(
                    core_occupants=core,
                    support_occupants=support,
                    new_capacity=capacity,
                )
                actual_core = sum(row.role == "core" for row in result.discarded)
                actual_support = sum(row.role == "support" for row in result.discarded)
                assert (actual_core, actual_support) == (expected_core, expected_support)

    occupants = tuple(
        [BenchOccupant(f"core-{i}", "core", 10.0) for i in range(4)]
        + [BenchOccupant(f"support-{i}", "support", 2.0) for i in range(3)]
    )

    for capacity in (5, 4, 3):
        result = resolve_capacity_transition(
            occupants,
            old_capacity=8,
            new_capacity=capacity,
        )
        print(
            f"8 -> {capacity}: discarded={[row.name for row in result.discarded]} "
            f"discarded_value={result.discarded_value:g}"
        )

    five_slot = tuple(
        [BenchOccupant(f"core-{i}", "core", 10.0) for i in range(4)]
        + [BenchOccupant("support", "support", 2.0)]
    )
    collapsed = resolve_capacity_transition(
        five_slot,
        old_capacity=5,
        new_capacity=4,
    )
    assert [row.name for row in collapsed.discarded] == ["support"]
    print("5 -> 4 four-core board:", collapsed)


if __name__ == "__main__":
    main()
