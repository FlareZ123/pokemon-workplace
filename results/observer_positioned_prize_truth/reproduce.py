"""Reproduce physically consistent observer-indexed Prize and top transitions."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_positioned_prize_truth import PhysicalPrizeTop, ObserverPositionedPrizes
from prize_position_top_swap import PrizePositionTopBelief


def close(actual, expected):
    assert abs(actual - expected) < 1e-12, (actual, expected)


def main():
    prior = PrizePositionTopBelief.from_pool(
        {"A": 1, "B": 1}, pool_size=5, prize_count=2
    )
    physical = PhysicalPrizeTop(
        ("F1", "B"), "A", (False, False),
        (("A", "A"), ("B", "B"), ("F1", None), ("F2", None), ("F3", None)),
    )
    state = ObserverPositionedPrizes(
        physical, (("actor", prior), ("opponent", prior))
    )

    state = state.peek_top("actor")
    close(state.belief_for("actor").probability_top("A"), 1)
    close(state.belief_for("opponent").probability_top("A"), 1 / 5)

    state = state.swap(0)
    assert state.truth.prizes == ("A", "B")
    assert state.truth.deck_top == "F1"
    close(state.belief_for("actor").probability_at(0, "A"), 1)
    close(state.belief_for("opponent").probability_at(0, "A"), 1 / 5)

    state = state.shuffle((1, 0))
    assert state.truth.prizes == ("B", "A")
    assert state.truth.deck_top == "F1"
    close(state.belief_for("actor").probability_at(1, "A"), 1 / 2)
    close(state.belief_for("opponent").probability_at(1, "A"), 1 / 5)

    state = state.reveal(1)
    close(state.belief_for("actor").probability_at(1, "A"), 1)
    close(state.belief_for("opponent").probability_at(1, "A"), 1)
    assert state.truth.face_up == (False, True)

    try:
        state.swap(1)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted swapping a face-up Prize")

    try:
        state.shuffle((0, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("accepted an invalid physical shuffle")

    incompatible = prior.observe_top("B")
    try:
        ObserverPositionedPrizes(physical, (("bad", incompatible),))
    except ValueError:
        pass
    else:
        raise AssertionError("accepted posterior excluding material truth")

    policy_state = ObserverPositionedPrizes(
        physical, (("actor", prior), ("opponent", prior))
    )
    policy_state = policy_state.peek_top("actor").swap(
        0,
        observed_choice_likelihoods={
            "opponent": {"A": 4 / 5, "B": 1 / 5, None: 1 / 5}
        },
    )
    close(policy_state.belief_for("opponent").probability_at(0, "A"), 1 / 2)
    assert policy_state.truth.prizes == ("A", "B")

    print("Physical Prize/top truth and private observer posterior regressions passed")


if __name__ == "__main__":
    main()
