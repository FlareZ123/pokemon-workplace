"""Reproduce the exact K0 discard/reacquisition information-gap result."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from k0_discard_reacquisition_bias import (
    DiscardReacquisitionChoice,
    exhaustive_small_model,
)


def check_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-15):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    flagship = DiscardReacquisitionChoice(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=2,
        forced_critical_discards=1,
    )
    check_close(flagship.blind_k0_success, 0.8846153846153846)
    check_close(flagship.informed_k1_success, 0.9886877828054299)
    check_close(flagship.information_gap, 0.10407239819004532)

    forced_both = DiscardReacquisitionChoice(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=2,
        forced_critical_discards=2,
    )
    check_close(forced_both.blind_k0_success, 0.7805429864253394)
    check_close(forced_both.informed_k1_success, forced_both.blind_k0_success)
    check_close(forced_both.information_gap, 0.0)

    three_choose_two = DiscardReacquisitionChoice(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=3,
        forced_critical_discards=2,
    )
    check_close(three_choose_two.blind_k0_success, 0.7805429864253394)
    check_close(three_choose_two.informed_k1_success, 0.9678733031674208)
    check_close(three_choose_two.information_gap, 0.18733031674208145)

    for params in ((7, 2, 3, 1), (7, 2, 3, 2)):
        model = DiscardReacquisitionChoice(
            unknown_pool=params[0],
            prize_count=params[1],
            candidate_classes=params[2],
            forced_critical_discards=params[3],
        )
        exhaustive_blind, exhaustive_informed = exhaustive_small_model(*params)
        check_close(exhaustive_blind, model.blind_k0_success)
        check_close(exhaustive_informed, model.informed_k1_success)

    print(
        "flagship blind K0 success="
        f"{flagship.blind_k0_success:.9%}"
    )
    print(
        "flagship informed K1/oracle success="
        f"{flagship.informed_k1_success:.9%}"
    )
    print(
        "flagship hidden-information gap="
        f"{flagship.information_gap * 100:.9f} percentage points"
    )
    print(
        "three-candidate/two-discard gap="
        f"{three_choose_two.information_gap * 100:.9f} percentage points"
    )
    print("All K0 discard-reacquisition checks passed.")


if __name__ == "__main__":
    main()
