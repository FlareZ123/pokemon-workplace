"""Exact selected-slot signaling under two hidden Prize-position states."""

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief


def close(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main():
    a_first = (("A", "B"), "X")
    b_first = (("B", "A"), "X")
    original = PrizePositionTopBelief(
        ("A", "B", "X"),
        (False, False),
        ((a_first, 0.5), (b_first, 0.5)),
    )

    # A fully revealing actor policy: actor knows the location of A.
    # The opponent sees that the actor chose physical position zero.
    likelihood = {a_first: 4 / 5, b_first: 1 / 5}
    conditioned = original.condition_on_public_world_choice(likelihood)
    close(dict(conditioned.masses)[a_first], Fraction(4, 5))
    close(dict(conditioned.masses)[b_first], Fraction(1, 5))
    physical = conditioned.swap_face_down_with_top(0)
    close(physical.probability_top("A"), Fraction(4, 5))
    close(physical.probability_top("B"), Fraction(1, 5))
    close(original.swap_face_down_with_top(0).probability_top("A"), Fraction(1, 2))
    assert physical.face_up == (False, False)

    # Independent rational oracle calculates a joint probability for observing
    # the selected action in each world, then conditions on the observation.
    joint_weights = {
        a_first: Fraction(1, 2) * Fraction(4, 5),
        b_first: Fraction(1, 2) * Fraction(1, 5),
    }
    probability_of_choice = sum(joint_weights.values())
    assert probability_of_choice == Fraction(1, 2)
    for world, weight in joint_weights.items():
        close(dict(conditioned.masses)[world], weight / probability_of_choice)

    # Choosing a slot using no information gives a neutral likelihood.
    uninformative = original.condition_on_public_world_choice({
        a_first: 1 / 2, b_first: 1 / 2,
    })
    assert dict(uninformative.masses) == dict(original.masses)

    # A deterministic selection strategy fully reveals whether position zero
    # contains A, assuming the player actually knows which position has A.
    deterministic = original.condition_on_public_world_choice({
        a_first: 1, b_first: 0,
    })
    close(deterministic.swap_face_down_with_top(0).probability_top("A"), 1)

    for broken in (
        {a_first: 1},  # missing world
        {a_first: 1, b_first: -0.1},
        {a_first: 1, b_first: 1.1},
        {a_first: 0, b_first: 0},
    ):
        try:
            original.condition_on_public_world_choice(broken)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid policy likelihood {broken}")

    print("Selected Prize-slot signaling passed: exact two-world posterior 4/5")
    print("P(outgoing deck top A)=4/5 with selection-policy inference; baseline=1/2")


if __name__ == "__main__":
    main()
