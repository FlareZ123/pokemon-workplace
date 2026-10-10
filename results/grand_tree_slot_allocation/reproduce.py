"""Verify exact balanced allocation theorem for joint evolution access."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.grand_tree_slot_allocation import (
    allocation_frontier,
    missing_probability,
    optimal_splits,
    verify_diminishing_rescue,
)


def main() -> None:
    assert verify_diminishing_rescue()

    four = allocation_frontier(4)
    assert [(row.stage1, row.stage2) for row in four] == [
        (2, 2), (1, 3), (3, 1)
    ]
    assert four[0].both_deck > four[1].both_deck
    assert four[1].both_deck == four[2].both_deck

    # Balance is the unique optimum up to swapping stages, for every
    # physically allowed 2-8 slot total with <=4 copies per named stage.
    for total in range(2, 9):
        winners = optimal_splits(total)
        assert winners
        assert {
            (row.stage1, row.stage2) for row in winners
        } == {
            (a, total - a)
            for a in range(1, total)
            if abs(a - (total - a)) <= 1
            and a <= 4
            and total - a <= 4
        }

    # The argument is finite-population rather than specific to 59/12.
    # Check exact discrete convexity across small legal n/u values, then
    # independently brute-enumerate all split choices for total<=8.
    for n in range(10, 19):
        for inaccessible in range(n):
            assert verify_diminishing_rescue(
                n=n, inaccessible=inaccessible
            )
            for total in range(2, min(8, n) + 1):
                rows = allocation_frontier(
                    total,
                    max_copies_per_stage=4,
                    n=n,
                    hand=inaccessible,
                    prizes=0,
                )
                if not rows:
                    continue
                best = max(row.both_deck for row in rows)
                balanced = tuple(
                    row for row in rows
                    if abs(row.stage1 - row.stage2) <= 1
                )
                assert balanced
                assert all(row.both_deck == best for row in balanced)

    assert missing_probability(0) == 1
    assert missing_probability(13) == 0
    assert Fraction(0) <= four[0].both_deck <= Fraction(1)

    print("fixed total | best split | both stages searchable")
    for total in range(2, 9):
        best = optimal_splits(total)
        label = ", ".join(f"{row.stage1}/{row.stage2}" for row in best)
        print(f"{total:>11} | {label:<12} | {float(best[0].both_deck):.6%}")

    print("Grand Tree balanced-slot theorem regressions passed")


if __name__ == "__main__":
    main()
