"""Reproduce a non-greedy finite-horizon Prize-position policy."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief  # noqa: E402
from prize_position_policy import optimal_prize_probe_policy  # noqa: E402


SUPPORT = (
    ("A", "B", None),
    ("A", None, "B"),
    (None, "A", "B"),
)
REWARD = {
    "A": Fraction(2, 1),
    "B": Fraction(1, 1),
}


def _assert_close(actual: float, expected: Fraction) -> None:
    if not isclose(actual, float(expected), rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _reward(group: str | None) -> Fraction:
    if group is None:
        return Fraction(0, 1)
    return REWARD[group]


def _exact_two_step_values() -> tuple[Fraction, ...]:
    """Enumerate every observation-contingent second-probe policy exactly."""

    groups = ("A", "B", None)
    per_first: list[Fraction] = []

    for first_position in range(3):
        best = Fraction(-1, 1)

        for continuation in product(range(3), repeat=len(groups)):
            next_position = dict(zip(groups, continuation))
            value = Fraction(0, 1)

            for row in SUPPORT:
                first_group = row[first_position]
                next_row = list(row)
                next_row[first_position] = None
                second_position = next_position[first_group]

                outcome_reward = (
                    _reward(first_group)
                    + _reward(next_row[second_position])
                )
                value += Fraction(1, len(SUPPORT)) * outcome_reward

            best = max(best, value)

        per_first.append(best)

    return tuple(per_first)


def main() -> None:
    state = PrizePositionBelief(
        groups=("A", "B"),
        prize_count=3,
        masses=tuple((row, 1 / 3) for row in SUPPORT),
    )

    distribution = state.composition_distribution()
    assert len(distribution) == 1
    only_composition, mass = next(iter(distribution.items()))
    assert only_composition == (1, 1)
    _assert_close(mass, Fraction(1, 1))
    assert state.composition_entropy_bits() <= 1e-12

    one_step = optimal_prize_probe_policy(
        state,
        {"A": 2.0, "B": 1.0},
        probes=1,
    )
    assert one_step.best_position == 0
    for actual, expected in zip(
        one_step.action_values,
        (Fraction(4, 3), Fraction(1, 1), Fraction(2, 3)),
    ):
        _assert_close(actual, expected)

    two_step = optimal_prize_probe_policy(
        state,
        {"A": 2.0, "B": 1.0},
        probes=2,
    )
    assert two_step.best_position == 1
    expected_two_step = (
        Fraction(7, 3),
        Fraction(8, 3),
        Fraction(2, 1),
    )
    for actual, expected in zip(two_step.action_values, expected_two_step):
        _assert_close(actual, expected)
    _assert_close(two_step.value, Fraction(8, 3))

    assert _exact_two_step_values() == expected_two_step

    print("Posterior support:")
    for row in SUPPORT:
        print(f"  p=1/3: {row}")

    print()
    print("Immediate one-probe values:")
    for position, value in enumerate(one_step.action_values):
        print(f"  slot {position}: {value:.9f}")
    print(f"  greedy slot: {one_step.best_position}")

    print()
    print("Optimal two-probe values by first slot:")
    for position, value in enumerate(two_step.action_values):
        print(f"  slot {position}: {value:.9f}")
    print(f"  optimal first slot: {two_step.best_position}")

    print()
    print("The two-step optimum deliberately gives up immediate expected reward.")
    print("All finite-horizon Prize-position policy checks passed.")


if __name__ == "__main__":
    main()
