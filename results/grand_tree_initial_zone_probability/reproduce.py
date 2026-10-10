"""Exact combinatorics for two-stage deck-search availability at setup."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for location in (ROOT, ROOT / "tools"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from tools.grand_tree_initial_zone_probability import (
    enumerate_access,
    probability_full,
)


def main() -> None:
    base = enumerate_access()
    assert base.full_chain == Fraction(1081, 1711)
    assert base.stage1_only == Fraction(282, 1711)
    assert base.no_stage1 == Fraction(12, 59)
    assert base.stage1_with_stage2_all_prized == Fraction(141, 1711)
    assert probability_full() == base.full_chain

    # Independently verify weighted hand -> Prize enumeration against an
    # inclusion-exclusion expression, over 16 natural copy-count pairs.
    for first in range(1, 5):
        for second in range(1, 5):
            enumerated = enumerate_access(first=first, second=second)
            analytical = probability_full(first=first, second=second)
            assert enumerated.full_chain == analytical, (first, second)
            assert (
                enumerated.full_chain
                + enumerated.stage1_only
                + enumerated.no_stage1
                == 1
            )

    assert enumerate_access(first=0).no_stage1 == 1
    assert probability_full(first=0) == 0
    assert probability_full(second=0) == 0

    # With 1 Stage1 and 1 Stage2, initial other-hand displacement and
    # Prize displacement must both be counted (independent conditional
    # probabilities, not independent unconditional events).
    both_outside_other_hand = Fraction(53 * 52, 59 * 58)
    both_avoid_prizes_given_hand = Fraction(47 * 46, 53 * 52)
    assert both_outside_other_hand * both_avoid_prizes_given_hand == base.full_chain

    print("copy counts | full chain | Stage 1 only | no Stage 1")
    for first, second in ((1, 1), (1, 2), (2, 1), (2, 2), (3, 3), (4, 4)):
        row = enumerate_access(first=first, second=second)
        print(
            f"{first}/{second:1d} | "
            f"{float(row.full_chain):.6%} | "
            f"{float(row.stage1_only):.6%} | "
            f"{float(row.no_stage1):.6%}"
        )
    print("Grand Tree exact initial-zone probability regressions passed")


if __name__ == "__main__":
    main()
