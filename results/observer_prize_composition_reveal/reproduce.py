"""Reproduce observer-relative K0->K1 Prize composition."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_prize_composition_reveal import (
    reveal_exact_prize_composition_to_observers,
)
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_top_swap_belief import TopPrizeJointBelief


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def main() -> None:
    # Before the first full deck search, either A or B is the one modeled
    # singleton in two face-down Prize slots. Its physical slot is also unknown.
    masses = (
        (("X", ("A", None)), 1.0 / 4.0),
        (("X", (None, "A")), 1.0 / 4.0),
        (("X", ("B", None)), 1.0 / 4.0),
        (("X", (None, "B")), 1.0 / 4.0),
    )
    prior = TopPrizeJointBelief(
        ("A", "B"),
        (False, False),
        masses,
    )
    observers = ObserverTopPrizeBeliefs(
        (("searcher", prior), ("opponent", prior))
    )

    revealed = reveal_exact_prize_composition_to_observers(
        observers,
        visible_compositions={
            "searcher": {"A": 1, "B": 0},
        },
    )

    searcher = revealed.belief_for("searcher").project_prizes()
    opponent = revealed.belief_for("opponent").project_prizes()

    assert searcher.composition_distribution() == {(1, 0): 1.0}
    assert_close(searcher.group_probability_at(0, "A"), 1.0 / 2.0)
    assert_close(searcher.group_probability_at(1, "A"), 1.0 / 2.0)

    assert opponent.composition_distribution() == {
        (1, 0): 1.0 / 2.0,
        (0, 1): 1.0 / 2.0,
    }
    assert_close(opponent.group_probability_at(0, "A"), 1.0 / 4.0)
    assert_close(opponent.group_probability_at(0, "B"), 1.0 / 4.0)

    try:
        reveal_exact_prize_composition_to_observers(
            observers,
            visible_compositions={
                "searcher": {"A": 1, "B": 1},
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError("accepted impossible exact Prize composition")

    print("Observer K0->K1 Prize composition regressions passed")


if __name__ == "__main__":
    main()
