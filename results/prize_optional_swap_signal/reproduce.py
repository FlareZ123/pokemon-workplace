"""Reproduce optional Arc Phone-style action signaling."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_optional_swap_signal import condition_on_optional_swap_decision
from prize_top_swap_belief import (
    TopPrizeJointBelief,
    swap_joint_top_with_face_down_prize,
)


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def prior() -> TopPrizeJointBelief:
    return TopPrizeJointBelief(
        ("A", "B"),
        (False,),
        (
            (("A", ("B",)), 1.0 / 2.0),
            (("B", ("A",)), 1.0 / 2.0),
        ),
    )


def main() -> None:
    belief = prior()

    # Deterministic policy: swap exactly when the privately viewed top card is A.
    signal = condition_on_optional_swap_decision(
        belief,
        swap_probability_by_top={"A": 1.0, "B": 0.0},
        observed_swap=True,
    )
    assert_close(signal.top_probability("A"), 1.0)
    assert_close(signal.prize_probability_at(0, "B"), 1.0)

    after_swap = swap_joint_top_with_face_down_prize(
        signal,
        position=0,
    )
    assert_close(after_swap.top_probability("B"), 1.0)
    assert_close(after_swap.prize_probability_at(0, "A"), 1.0)

    decline = condition_on_optional_swap_decision(
        belief,
        swap_probability_by_top={"A": 1.0, "B": 0.0},
        observed_swap=False,
    )
    assert_close(decline.top_probability("B"), 1.0)
    assert_close(decline.prize_probability_at(0, "A"), 1.0)

    # A non-deterministic policy creates graded information.
    partial = condition_on_optional_swap_decision(
        belief,
        swap_probability_by_top={"A": 1.0, "B": 0.5},
        observed_swap=True,
    )
    assert_close(partial.top_probability("A"), 2.0 / 3.0)
    assert_close(partial.top_probability("B"), 1.0 / 3.0)

    partial_after_swap = swap_joint_top_with_face_down_prize(
        partial,
        position=0,
    )
    assert_close(partial_after_swap.top_probability("B"), 2.0 / 3.0)
    assert_close(
        partial_after_swap.prize_probability_at(0, "A"),
        2.0 / 3.0,
    )

    # If the policy always swaps, observing the action carries no information.
    no_signal = condition_on_optional_swap_decision(
        belief,
        swap_probability_by_top={"A": 1.0, "B": 1.0},
        observed_swap=True,
    )
    assert no_signal == belief

    try:
        condition_on_optional_swap_decision(
            belief,
            swap_probability_by_top={"A": 0.0, "B": 0.0},
            observed_swap=True,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("accepted an impossible observed swap")

    print("optional Prize swap signaling regressions passed")


if __name__ == "__main__":
    main()
