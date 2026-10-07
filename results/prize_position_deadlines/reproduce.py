"""Reproduce per-target acquisition deadlines for Prize-position probing."""

from __future__ import annotations

from fractions import Fraction
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief  # noqa: E402
from prize_position_policy import (  # noqa: E402
    optimal_prize_acquisition_deadline_policy,
)


SUPPORT = (
    ("A", "C", "B", None),
    ("C", "B", None, "A"),
    ("A", "B", None, "C"),
    (None, "C", "A", "B"),
)
GROUPS = ("A", "B", "C")


def _assert_close(actual: float, expected: Fraction) -> None:
    if not isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _conditioned_rows(
    rows: tuple[tuple[str | None, ...], ...],
    position: int,
    observed: str | None,
) -> tuple[tuple[str | None, ...], ...]:
    return tuple(row for row in rows if row[position] == observed)


def _replace_position(
    rows: tuple[tuple[str | None, ...], ...],
    position: int,
) -> tuple[tuple[str | None, ...], ...]:
    output = []
    for row in rows:
        next_row = list(row)
        next_row[position] = None
        output.append(tuple(next_row))
    return tuple(output)


def _exact_value(
    rows: tuple[tuple[str | None, ...], ...],
    deadlines: tuple[int, ...],
    acquired: frozenset[str],
) -> Fraction:
    if all(group in acquired for group in GROUPS):
        return Fraction(1, 1)

    if any(
        deadline < 0
        for group, deadline in zip(GROUPS, deadlines)
        if group not in acquired
    ):
        return Fraction(0, 1)

    values = tuple(
        _exact_action_value(rows, deadlines, acquired, position)
        for position in range(4)
    )
    return max(values)


def _exact_action_value(
    rows: tuple[tuple[str | None, ...], ...],
    deadlines: tuple[int, ...],
    acquired: frozenset[str],
    position: int,
) -> Fraction:
    total = Fraction(0, 1)

    for observed in (None,) + GROUPS:
        conditioned = _conditioned_rows(rows, position, observed)
        if not conditioned:
            continue

        probability = Fraction(len(conditioned), len(rows))
        next_acquired = acquired
        if observed in GROUPS:
            next_acquired = acquired | {observed}

        next_deadlines = tuple(
            deadline if group in next_acquired else deadline - 1
            for group, deadline in zip(GROUPS, deadlines)
        )
        total += probability * _exact_value(
            _replace_position(conditioned, position),
            next_deadlines,
            frozenset(next_acquired),
        )

    return total


def _exact_first_values(
    deadlines: tuple[int, ...],
) -> tuple[Fraction, ...]:
    return tuple(
        _exact_action_value(
            SUPPORT,
            deadlines,
            frozenset(),
            position,
        )
        for position in range(4)
    )


def main() -> None:
    state = PrizePositionBelief(
        groups=GROUPS,
        prize_count=4,
        masses=tuple((row, 1 / 4) for row in SUPPORT),
    )

    distribution = state.composition_distribution()
    assert len(distribution) == 1
    only_composition, mass = next(iter(distribution.items()))
    assert only_composition == (1, 1, 1)
    _assert_close(mass, Fraction(1, 1))
    assert state.composition_entropy_bits() <= 1e-12

    relaxed = optimal_prize_acquisition_deadline_policy(
        state,
        {"A": 2, "B": 2, "C": 2},
    )
    expected_relaxed = (
        Fraction(3, 4),
        Fraction(1, 1),
        Fraction(1, 2),
        Fraction(3, 4),
    )
    assert relaxed.best_position == 1
    _assert_close(relaxed.success_probability, Fraction(1, 1))
    for actual, expected in zip(relaxed.action_values, expected_relaxed):
        _assert_close(actual, expected)
    assert _exact_first_values((2, 2, 2)) == expected_relaxed

    urgent_a = optimal_prize_acquisition_deadline_policy(
        state,
        {"A": 0, "B": 2, "C": 2},
    )
    expected_urgent = (
        Fraction(1, 2),
        Fraction(0, 1),
        Fraction(1, 4),
        Fraction(1, 4),
    )
    assert urgent_a.best_position == 0
    _assert_close(urgent_a.success_probability, Fraction(1, 2))
    for actual, expected in zip(urgent_a.action_values, expected_urgent):
        _assert_close(actual, expected)
    assert _exact_first_values((0, 2, 2)) == expected_urgent

    already_has_a = optimal_prize_acquisition_deadline_policy(
        state,
        {"A": 0, "B": 1, "C": 1},
        initial_acquired=("A",),
    )
    assert already_has_a.success_probability > 0.0

    print("Posterior support:")
    for row in SUPPORT:
        print(f"  p=1/4: {row}")

    print()
    print("Relaxed deadline values:")
    for position, value in enumerate(relaxed.action_values):
        print(f"  slot {position}: {value:.9f}")
    print(f"  relaxed first slot: {relaxed.best_position}")
    print(f"  relaxed success: {relaxed.success_probability:.9f}")

    print()
    print("A-due-now values:")
    for position, value in enumerate(urgent_a.action_values):
        print(f"  slot {position}: {value:.9f}")
    print(f"  urgent first slot: {urgent_a.best_position}")
    print(f"  urgent success: {urgent_a.success_probability:.9f}")

    print()
    print("The immediate A deadline forces coverage before information gathering.")
    print("All Prize-position deadline checks passed.")


if __name__ == "__main__":
    main()
