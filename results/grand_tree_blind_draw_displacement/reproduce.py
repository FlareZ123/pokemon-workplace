"""Prove blind draws remove searchable Grand Tree targets at exact rates."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.grand_tree_blind_draw_displacement import (
    probability_joint_after_draws,
    probability_stage2_given_stage1,
    probability_stage_remaining,
)
from tools.grand_tree_initial_zone_probability import enumerate_zone_outcomes


def main() -> None:
    assert probability_joint_after_draws(1, 1, 0) == Fraction(1081, 1711)
    assert probability_joint_after_draws(1, 1, 1) == Fraction(1035, 1711)

    for d in range(48):
        closed = probability_joint_after_draws(1, 1, d)
        independent = Fraction((47-d) * (46-d), 59 * 58)
        assert closed == independent, d
        assert probability_stage_remaining(1, d) == Fraction(47-d, 59)
        if d < 47:
            assert (
                probability_stage2_given_stage1(1, 1, d)
                == Fraction(46-d, 58)
            )
        if d > 0:
            assert (
                closed <= probability_joint_after_draws(1, 1, d - 1)
            )

    # The general joint formula agrees with an independent full
    # hand/Prize category enumeration after expanding hand by d draws.
    checks = 0
    for a in range(1, 5):
        for b in range(1, 5):
            prior = Fraction(1)
            for d in range(0, 12):
                analytic = probability_joint_after_draws(a, b, d)
                counted = enumerate_zone_outcomes(
                    n=59, hand=6+d, prizes=6,
                    stage1=a, stage2=b,
                )
                assert analytic == counted.full_chain, (a, b, d)
                assert analytic <= prior
                prior = analytic
                checks += 1

    # Draws cannot be requested beyond actual deck exhaustion.
    try:
        probability_joint_after_draws(1, 1, 48)
    except ValueError:
        pass
    else:
        raise AssertionError("impossible 48th draw was accepted")

    assert probability_joint_after_draws(1, 1, 47) == 0

    print("blind draws | singleton pair in deck | 2/2 stages in deck")
    for d in (0, 1, 2, 3, 5, 8, 10):
        p11 = probability_joint_after_draws(1, 1, d)
        p22 = probability_joint_after_draws(2, 2, d)
        print(f"{d:>11} | {float(p11):.6%} | {float(p22):.6%}")
    print(f"Grand Tree blind-draw tests passed: {checks} general cases")


if __name__ == "__main__":
    main()
