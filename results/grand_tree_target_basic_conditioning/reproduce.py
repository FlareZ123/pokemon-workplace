"""Compare exact conditional hypergeom to independent four-group enumeration."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.grand_tree_initial_zone_probability import probability_full
from tools.grand_tree_target_basic_conditioning import (
    conditional_full_chain,
    enumerate_conditional_full_chain,
    probability_no_stage_deck_given_target_basic_hand,
)


def main() -> None:
    # Exactly one Basic copy in the entire deck is equivalent to
    # conditioning on that designated copy already in opening hand.
    for a in range(1, 5):
        for b in range(1, 5):
            expected = probability_full(first=a, second=b)
            actual = conditional_full_chain(
                basics=1, stage1=a, stage2=b
            )
            assert actual == expected, (a, b, expected, actual)

    # With more Basic copies, conditioning on at least one Basic is
    # genuinely different from fixing one specified Basic in the hand.
    r1 = conditional_full_chain(basics=1, stage1=1, stage2=1)
    r4 = conditional_full_chain(basics=4, stage1=1, stage2=1)
    assert r1 == Fraction(1081, 1711)
    assert r4 < r1

    cases = 0
    for basics in range(1, 6):
        for a in range(0, 5):
            for b in range(0, 5):
                closed = conditional_full_chain(
                    basics=basics, stage1=a, stage2=b
                )
                counted = enumerate_conditional_full_chain(
                    basics=basics, stage1=a, stage2=b
                )
                assert closed == counted, (basics, a, b, closed, counted)
                assert 0 <= closed <= 1
                if a == 0 or b == 0:
                    assert closed == 0
                cases += 1

    # The identity also holds for smaller physical setups with different
    # hand and Prize sizes (and at least one Basic in hand).
    for cards, hand, prizes in ((12, 4, 2), (16, 5, 3)):
        for basics in (1, 2, 3):
            for a in (0, 1, 2):
                for b in (0, 1, 2):
                    if basics + a + b > cards:
                        continue
                    closed = conditional_full_chain(
                        basics=basics, stage1=a, stage2=b,
                        cards=cards, hand=hand, prizes=prizes,
                    )
                    counted = enumerate_conditional_full_chain(
                        basics=basics, stage1=a, stage2=b,
                        cards=cards, hand=hand, prizes=prizes,
                    )
                    assert closed == counted, (
                        cards, hand, prizes, basics, a, b,
                    )
                    cases += 1

    print("target Basic copies | P(both singleton stages in deck)")
    for basics in (1, 2, 3, 4, 8):
        probability = conditional_full_chain(
            basics=basics, stage1=1, stage2=1
        )
        print(f"{basics:>19} | {float(probability):.6%}")
    assert (
        probability_no_stage_deck_given_target_basic_hand(
            basics=4, stage_copies=0
        ) == 1
    )
    print(f"Grand Tree conditioned Basic regression cases: {cases} passed")


if __name__ == "__main__":
    main()
