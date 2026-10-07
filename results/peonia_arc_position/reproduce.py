"""Reproduce the Peonia -> Arc Phone positional policy calculation."""

from __future__ import annotations

from fractions import Fraction
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from peonia_arc_position import analyze_peonia_arc_position  # noqa: E402


def _assert_close(actual: float, expected: Fraction) -> None:
    if not isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _labeled_preserved_success(
    prize_count: int,
    peonia_count: int,
) -> Fraction:
    """Independent exhaustive target-position check.

    The target starts uniformly at one labeled Prize position. Peonia chooses
    positions 0..peonia_count-1. After a miss, every untouched position is
    equiprobable, so a fixed best Arc Phone policy may choose the first untouched
    slot without loss of generality.
    """

    selected = set(range(peonia_count))
    arc_position = peonia_count
    successes = 0

    for target_position in range(prize_count):
        if target_position in selected or target_position == arc_position:
            successes += 1

    return Fraction(successes, prize_count)


def _labeled_shuffled_success(
    prize_count: int,
    peonia_count: int,
) -> Fraction:
    """Independent exhaustive check if a Prize shuffle follows a Peonia miss."""

    selected = set(range(peonia_count))
    success = Fraction(0, 1)

    for target_position in range(prize_count):
        initial_mass = Fraction(1, prize_count)
        if target_position in selected:
            success += initial_mass
            continue

        for post_shuffle_position in range(prize_count):
            if post_shuffle_position == 0:
                success += initial_mass * Fraction(1, prize_count)

    return success


def main() -> None:
    prize_count = 6

    print("Peonia -> Arc Phone singleton target")
    print(
        "Peonia count | preserved | shuffled counterfactual | positional gain"
    )

    for peonia_count in (1, 2, 3):
        result = analyze_peonia_arc_position(
            prize_count=prize_count,
            peonia_count=peonia_count,
        )

        preserved_closed_form = Fraction(peonia_count + 1, prize_count)
        shuffled_closed_form = (
            Fraction(peonia_count, prize_count)
            + Fraction(prize_count - peonia_count, prize_count)
            * Fraction(1, prize_count)
        )

        _assert_close(
            result.peonia_target_probability,
            Fraction(peonia_count, prize_count),
        )
        _assert_close(
            result.arc_target_given_peonia_miss,
            Fraction(1, prize_count - peonia_count),
        )
        _assert_close(
            result.combined_target_probability,
            preserved_closed_form,
        )
        _assert_close(
            result.shuffled_arc_target_given_miss,
            Fraction(1, prize_count),
        )
        _assert_close(
            result.shuffled_combined_target_probability,
            shuffled_closed_form,
        )
        _assert_close(
            result.position_information_gain,
            preserved_closed_form - shuffled_closed_form,
        )

        assert (
            _labeled_preserved_success(prize_count, peonia_count)
            == preserved_closed_form
        )
        assert (
            _labeled_shuffled_success(prize_count, peonia_count)
            == shuffled_closed_form
        )

        print(
            f"{peonia_count:12d} | "
            f"{100 * result.combined_target_probability:8.6f}% | "
            f"{100 * result.shuffled_combined_target_probability:8.6f}% | "
            f"{100 * result.position_information_gain:8.6f} pp"
        )

    three = analyze_peonia_arc_position(
        prize_count=6,
        peonia_count=3,
    )
    _assert_close(three.combined_target_probability, Fraction(2, 3))
    _assert_close(
        three.shuffled_combined_target_probability,
        Fraction(7, 12),
    )
    _assert_close(three.position_information_gain, Fraction(1, 12))

    print()
    print("All Peonia -> Arc Phone positional checks passed.")


if __name__ == "__main__":
    main()
