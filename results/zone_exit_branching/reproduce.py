"""Reproduce zone-exit target and promotion branching counts."""

from pathlib import Path
import itertools
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from zone_exit_branching import (
    any_number_own_board_continuations,
    ordered_promotion_continuations,
    target_set_upper_bound,
)


FULL_BOARD = {
    "own_board_count": 6,
    "own_bench_count": 5,
    "opponent_board_count": 6,
    "opponent_bench_count": 5,
}


def enumerate_any_number_continuations(bench_count: int) -> int:
    bench = tuple(range(bench_count))
    total = 0

    for active_removed in (False, True):
        for removed_count in range(bench_count + 1):
            for removed in itertools.combinations(bench, removed_count):
                if not active_removed:
                    total += 1
                    continue
                survivors = bench_count - len(removed)
                total += survivors if survivors else 1

    return total


def main() -> None:
    expected_full_board = {
        "self": 1,
        "own_one": 6,
        "own_bench_one": 5,
        "opponent_active": 1,
        "opponent_bench_one": 5,
        "opponent_one": 6,
        "own_any_number": 64,
        "opponent_bench_one_and_self": 5,
        "opponent_bench_all": 1,
        "opponent_bench_all_except_selected_three": 10,
        "both_active": 1,
    }

    actual_full_board = {
        geometry: target_set_upper_bound(
            geometry,
            **FULL_BOARD,
        )
        for geometry in expected_full_board
    }
    assert actual_full_board == expected_full_board

    assert target_set_upper_bound(
        "unqualified_one_to_your_hand",
        **FULL_BOARD,
    ) is None

    expected_any_number = {
        0: 2,
        1: 4,
        2: 9,
        3: 21,
        4: 49,
        5: 113,
    }
    for bench_count, expected in expected_any_number.items():
        calculated = any_number_own_board_continuations(
            bench_count
        )
        enumerated = enumerate_any_number_continuations(
            bench_count
        )
        assert calculated == expected
        assert calculated == enumerated

    assert ordered_promotion_continuations(5, 5) == 25
    assert ordered_promotion_continuations(1, 5) == 5
    assert ordered_promotion_continuations(0, 5) == 0

    print(actual_full_board)
    print(expected_any_number)
    print(
        "full-board ordered two-player promotions:",
        ordered_promotion_continuations(5, 5),
    )


if __name__ == "__main__":
    main()
