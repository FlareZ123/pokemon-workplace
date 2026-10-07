"""Reproduce repeated position-aware Prize probing."""

from __future__ import annotations

from fractions import Fraction
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from repeated_prize_probe import analyze_repeated_prize_probes  # noqa: E402


def _assert_close(actual: float, expected: Fraction) -> None:
    if not isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _labeled_without_replacement(
    prize_count: int,
    prechecked: int,
    probes: int,
) -> Fraction:
    """Independent labeled target-position enumeration."""

    successful_positions = min(
        prize_count,
        prechecked + probes,
    )
    return Fraction(successful_positions, prize_count)


def _composition_forgetting_closed_form(
    prize_count: int,
    prechecked: int,
    probes: int,
) -> Fraction:
    precheck_hit = Fraction(prechecked, prize_count)
    precheck_miss = Fraction(prize_count - prechecked, prize_count)
    per_probe_miss = Fraction(prize_count - 1, prize_count)
    probe_hit = 1 - per_probe_miss ** probes
    return precheck_hit + precheck_miss * probe_hit


def main() -> None:
    prize_count = 6
    prechecked = 3

    print("Peonia precheck + repeated Arc Phone/Trekking Shoes probes")
    print("Probes | position-aware | composition-forgetting | memory gain")

    for probes in range(4):
        result = analyze_repeated_prize_probes(
            prize_count=prize_count,
            prechecked_positions=prechecked,
            probes=probes,
        )

        correct = _labeled_without_replacement(
            prize_count,
            prechecked,
            probes,
        )
        forgetting = _composition_forgetting_closed_form(
            prize_count,
            prechecked,
            probes,
        )

        _assert_close(
            result.precheck_success_probability,
            Fraction(prechecked, prize_count),
        )
        _assert_close(
            result.position_aware_success_probability,
            correct,
        )
        _assert_close(
            result.composition_forgetting_success_probability,
            forgetting,
        )
        _assert_close(
            result.position_memory_gain,
            correct - forgetting,
        )

        print(
            f"{probes:6d} | "
            f"{100 * result.position_aware_success_probability:8.6f}% | "
            f"{100 * result.composition_forgetting_success_probability:8.6f}% | "
            f"{100 * result.position_memory_gain:8.6f} pp"
        )

    three = analyze_repeated_prize_probes(
        prize_count=6,
        prechecked_positions=3,
        probes=3,
    )
    _assert_close(three.position_aware_success_probability, Fraction(1, 1))
    _assert_close(
        three.composition_forgetting_success_probability,
        Fraction(307, 432),
    )
    _assert_close(three.position_memory_gain, Fraction(125, 432))

    print()
    print("Three distinct post-Peonia probes cover all remaining target positions.")
    print("All repeated Prize-probe checks passed.")


if __name__ == "__main__":
    main()
