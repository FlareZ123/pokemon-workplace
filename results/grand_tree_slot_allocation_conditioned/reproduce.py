"""Check balance remains optimal after conditioning on target Basic access."""

from __future__ import annotations

from fractions import Fraction
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.grand_tree_slot_allocation import (
    conditional_frontier,
    missing_probability,
)
from tools.grand_tree_target_basic_conditioning import (
    conditional_full_chain,
    probability_no_stage_deck_given_target_basic_hand,
)


def test_mixture_convexity(
    basics: int,
    *,
    cards: int = 60,
    hand: int = 7,
    prizes: int = 6,
) -> None:
    """Verify exact falling-factorial mixture's discrete convexity."""
    nonbasics = cards - basics
    q = [
        probability_no_stage_deck_given_target_basic_hand(
            basics=basics,
            stage_copies=k,
            cards=cards,
            hand=hand,
            prizes=prizes,
        )
        for k in range(nonbasics + 1)
    ]
    drops = [q[k] - q[k+1] for k in range(nonbasics)]
    assert all(drops[k] >= drops[k+1] >= 0 for k in range(len(drops)-1))


def main() -> None:
    cases = 0
    for r in range(1, 13):
        test_mixture_convexity(r)
        for total in range(2, 9):
            rows = conditional_frontier(
                total, target_basics=r
            )
            assert rows
            best = rows[0].both_deck
            balanced = [
                row for row in rows
                if abs(row.stage1 - row.stage2) <= 1
            ]
            assert balanced
            assert all(row.both_deck == best for row in balanced)
            cases += 1

    # The singleton target-Basic case must recover fixed-designated-
    # Basic (N=59, inaccessible=12) results exactly.
    single_r = conditional_frontier(4, target_basics=1)
    assert single_r[0].stage1 == single_r[0].stage2 == 2
    assert single_r[0].both_deck == (
        Fraction(1) - 2 * missing_probability(2)
        + missing_probability(4)
    )

    # More target Basics changes the conditional *value*, but the
    # maximizing 2/2 split survives.
    four_basic = conditional_frontier(4, target_basics=4)
    assert four_basic[0].stage1 == four_basic[0].stage2 == 2
    assert four_basic[0].both_deck != single_r[0].both_deck
    assert (
        conditional_full_chain(basics=4, stage1=1, stage2=3)
        == four_basic[1].both_deck
    )

    # Smaller population examples show the result is structural,
    # including altered hand/Prize sizes.
    for cards, hand, prizes in ((12, 4, 2), (16, 5, 3)):
        for basics in (1, 2, 4):
            test_mixture_convexity(
                basics, cards=cards, hand=hand, prizes=prizes
            )
            for total in range(2, min(8, cards - basics) + 1):
                rows = conditional_frontier(
                    total,
                    target_basics=basics,
                    cards=cards, hand=hand, prizes=prizes,
                )
                if not rows:
                    continue
                maximum = rows[0].both_deck
                for row in rows:
                    if abs(row.stage1 - row.stage2) <= 1:
                        assert row.both_deck == maximum
                cases += 1

    print("target Basics | P(2/2 joint) | P(1/3 joint)")
    for basics in (1, 2, 4, 8):
        opts = conditional_frontier(4, target_basics=basics)
        balanced = next(x for x in opts if (x.stage1, x.stage2) == (2, 2))
        unbalanced = next(x for x in opts if (x.stage1, x.stage2) == (1, 3))
        print(
            f"{basics:>13} | {float(balanced.both_deck):.6%}"
            f" | {float(unbalanced.both_deck):.6%}"
        )
    print(f"conditional balance oracle: {cases} grid cases passed")


if __name__ == "__main__":
    main()
