"""Reproduce state-dependent finite-horizon Prize-position policy results."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief  # noqa: E402
from prize_position_policy import (  # noqa: E402
    optimal_prize_probe_policy,
    optimal_prize_terminal_policy,
)


SUPPORT = (
    ("C", "A", "B", None),
    (None, "A", "C", "B"),
    ("C", None, "B", "A"),
)


def _terminal_utility(acquired: frozenset[str]) -> float:
    value = 0.0
    if {"A", "B"} <= acquired:
        value += 10.0
    if "C" in acquired:
        value += 6.0
    return value


def _exact_terminal_utility(acquired: frozenset[str]) -> Fraction:
    value = Fraction(0, 1)
    if {"A", "B"} <= acquired:
        value += Fraction(10, 1)
    if "C" in acquired:
        value += Fraction(6, 1)
    return value


def _assert_close(actual: float, expected: Fraction) -> None:
    if not isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _exact_two_step_terminal_values() -> tuple[Fraction, ...]:
    """Enumerate every observation-contingent second-position policy exactly."""

    groups = ("A", "B", "C", None)
    per_first: list[Fraction] = []

    for first_position in range(4):
        best = Fraction(-1, 1)

        for continuation in product(range(4), repeat=len(groups)):
            next_position = dict(zip(groups, continuation))
            expected = Fraction(0, 1)

            for row in SUPPORT:
                first_group = row[first_position]
                next_row = list(row)
                next_row[first_position] = None

                acquired = set()
                if first_group is not None:
                    acquired.add(first_group)

                second_position = next_position[first_group]
                second_group = next_row[second_position]
                if second_group is not None:
                    acquired.add(second_group)

                expected += (
                    Fraction(1, len(SUPPORT))
                    * _exact_terminal_utility(frozenset(acquired))
                )

            best = max(best, expected)

        per_first.append(best)

    return tuple(per_first)


def main() -> None:
    state = PrizePositionBelief(
        groups=("A", "B", "C"),
        prize_count=4,
        masses=tuple((row, 1 / 3) for row in SUPPORT),
    )

    distribution = state.composition_distribution()
    assert len(distribution) == 1
    only_composition, mass = next(iter(distribution.items()))
    assert only_composition == (1, 1, 1)
    _assert_close(mass, Fraction(1, 1))
    assert state.composition_entropy_bits() <= 1e-12

    additive_proxy = optimal_prize_probe_policy(
        state,
        {"A": 5.0, "B": 5.0, "C": 6.0},
        probes=2,
    )
    assert additive_proxy.best_position == 2
    expected_additive = (
        Fraction(28, 3),
        Fraction(9, 1),
        Fraction(11, 1),
        Fraction(28, 3),
    )
    for actual, expected in zip(
        additive_proxy.action_values,
        expected_additive,
    ):
        _assert_close(actual, expected)

    terminal = optimal_prize_terminal_policy(
        state,
        _terminal_utility,
        probes=2,
    )
    assert terminal.best_position == 3
    expected_terminal = (
        Fraction(6, 1),
        Fraction(22, 3),
        Fraction(6, 1),
        Fraction(26, 3),
    )
    for actual, expected in zip(terminal.action_values, expected_terminal):
        _assert_close(actual, expected)
    _assert_close(terminal.value, Fraction(26, 3))
    _assert_close(terminal.stop_value, Fraction(0, 1))

    assert _exact_two_step_terminal_values() == expected_terminal

    already_has_a = optimal_prize_terminal_policy(
        state,
        _terminal_utility,
        probes=1,
        initial_acquired=("A",),
    )
    assert already_has_a.best_position == 2
    _assert_close(already_has_a.value, Fraction(26, 3))

    saturated = optimal_prize_terminal_policy(
        state,
        _terminal_utility,
        probes=2,
        initial_acquired=("A", "B", "C"),
    )
    assert saturated.best_position is None
    _assert_close(saturated.value, Fraction(16, 1))
    _assert_close(saturated.stop_value, Fraction(16, 1))

    print("Posterior support:")
    for row in SUPPORT:
        print(f"  p=1/3: {row}")

    print()
    print("Two-probe additive proxy values:")
    for position, value in enumerate(additive_proxy.action_values):
        print(f"  slot {position}: {value:.9f}")
    print(f"  additive first slot: {additive_proxy.best_position}")

    print()
    print("Two-probe terminal-utility values:")
    for position, value in enumerate(terminal.action_values):
        print(f"  slot {position}: {value:.9f}")
    print(f"  terminal-optimal first slot: {terminal.best_position}")

    print()
    print("The fixed additive proxy selects the wrong first physical position.")
    print("All state-dependent Prize-position policy checks passed.")


if __name__ == "__main__":
    main()
