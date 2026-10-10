"""Reproduce the 500,000-opening Aichi Secret Box coalition audit."""

from fractions import Fraction
from math import prod
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from secret_box_coalition_synergy import (
    expected_successes,
    singleton_or_counts,
    synergy_counts,
    uniform_availability_coefficients,
)
from subset_shapley import shapley_values


# Pinned from results/aichi_secret_box_output_dependencies/reproduce_full.py.
MASK_SUCCESS_COUNTS = (
    0, 20_783, 2_313, 20_783,
    20_703, 20_785, 20_785, 20_785,
    623, 20_783, 4_849, 20_783,
    20_745, 20_785, 20_785, 20_785,
)
SINGLETON_SIGNATURE_COUNTS = (
    0, 42, 0, 40,
    2, 17_809, 0, 2_269,
    0, 0, 0, 0,
    0, 619, 0, 4,
)
EXPECTED_SYNERGY = (
    0, 0, 0, 0,
    0, 0, 42, 0,
    0, 0, 1_917, 0,
    42, 0, 42, 0,
)


def test_small_independent_oracle() -> None:
    """Enumerate four Boolean states and all 16 availability masks."""
    routes = (
        (0b0001,),
        (0b0010, 0b1000),
        (0b1010,),
        (0b0001, 0b1010),
    )
    actual = tuple(
        sum(
            any(mask & needed == needed for needed in options)
            for options in routes
        )
        for mask in range(16)
    )
    signatures = tuple(
        sum(
            sum(
                1 << bit
                for bit in range(4)
                if any((1 << bit) & needed == needed for needed in options)
            ) == signature
            for options in routes
        )
        for signature in range(16)
    )
    surplus = synergy_counts(actual, signatures)
    assert surplus[0b1010] == 2
    assert surplus[0b1111] == 1  # One state has no singleton witness.
    assert expected_successes(
        actual, (Fraction(1, 2),) * 4
    ) == Fraction(sum(actual), 16)


def main() -> None:
    test_small_independent_oracle()
    original = MASK_SUCCESS_COUNTS
    singletons = singleton_or_counts(SINGLETON_SIGNATURE_COUNTS)
    synergy = synergy_counts(original, SINGLETON_SIGNATURE_COUNTS)
    assert synergy == EXPECTED_SYNERGY
    assert singletons[15] == original[15] == 20_785
    assert singletons[10] == 2_932
    assert original[10] == 4_849
    assert uniform_availability_coefficients(original) == (
        0, 44_422, -24_536, -1_056, 1_955
    )
    assert uniform_availability_coefficients(singletons) == (
        0, 44_422, -26_537, 2_904, -4
    )
    assert uniform_availability_coefficients(synergy) == (
        0, 0, 2_001, -3_960, 1_959
    )

    half = (Fraction(1, 2),) * 4
    full_expectation = expected_successes(original, half)
    or_expectation = expected_successes(singletons, half)
    assert full_expectation == Fraction(257_075, 16)
    assert or_expectation == Fraction(31_879, 2)
    assert full_expectation - or_expectation == Fraction(2_043, 16)
    assert expected_successes(original, (Fraction(1),) * 4) == 20_785
    assert expected_successes(original, (Fraction(0),) * 4) == 0

    correction = shapley_values(synergy)
    assert correction == (
        Fraction(-709, 4), Fraction(653, 4),
        Fraction(-597, 4), Fraction(653, 4),
    )
    assert sum(correction) == 0

    ps = (Fraction(1, 3), Fraction(3, 4),
          Fraction(2, 5), Fraction(5, 6))
    explicit = sum(
        Fraction(original[m]) * prod(
            ps[i] if m & (1 << i) else 1 - ps[i]
            for i in range(4)
        )
        for m in range(16)
    )
    assert expected_successes(original, ps) == explicit

    print("Accepted openings: 500000; incremental successes: 20785")
    print("Tool+Stadium successes:", original[10])
    print("Tool+Stadium singleton union:", singletons[10])
    print("Tool+Stadium extra routes:", synergy[10])
    print("All mask synergies:", synergy)
    print("Uniform success polynomial:", uniform_availability_coefficients(original))
    print("Singleton-only polynomial:", uniform_availability_coefficients(singletons))
    print("At q=1/2 actual:", full_expectation,
          "singleton-only:", or_expectation)
    print("Expected undercount:", full_expectation - or_expectation,
          "states; conditional percentage points:",
          float((full_expectation - or_expectation) * 100 / 20_785))
    print("Shapley corrections:", correction)
    print("All coalition-synergy checks passed.")


if __name__ == "__main__":
    main()
