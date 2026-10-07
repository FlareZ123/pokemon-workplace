"""Reproduce the Arc Phone-style cross-zone correlation result."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from prize_top_swap_belief import swap_known_top_with_face_down_prize


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def main() -> None:
    prior_positions = PrizePositionBelief.from_exact_composition(
        {"A": 1, "B": 1, "X": 0},
        prize_count=2,
    )
    prizes = PrizeSlotVisibilityBelief.all_face_down(prior_positions)

    result = swap_known_top_with_face_down_prize(
        prizes,
        position=0,
        incoming_group="X",
    )

    # The unknown outgoing Prize is now the unknown top-deck card.
    assert_close(result.top_probability("A"), 1.0 / 2.0)
    assert_close(result.top_probability("B"), 1.0 / 2.0)

    # The untouched Prize slot is also marginally A/B with equal probability.
    assert_close(result.prize_probability_at(1, "A"), 1.0 / 2.0)
    assert_close(result.prize_probability_at(1, "B"), 1.0 / 2.0)

    # The two marginals are perfectly anti-correlated.
    assert_close(
        result.joint_probability(
            top_group="A",
            prize_position=1,
            prize_group="A",
        ),
        0.0,
    )
    assert_close(
        result.joint_probability(
            top_group="A",
            prize_position=1,
            prize_group="B",
        ),
        1.0 / 2.0,
    )
    assert_close(
        result.joint_probability(
            top_group="B",
            prize_position=1,
            prize_group="A",
        ),
        1.0 / 2.0,
    )
    assert_close(
        result.joint_probability(
            top_group="B",
            prize_position=1,
            prize_group="B",
        ),
        0.0,
    )

    # Multiplying independent marginals would invent impossible states.
    independent_false_mass = (
        result.top_probability("A")
        * result.prize_probability_at(1, "A")
    )
    assert_close(independent_false_mass, 1.0 / 4.0)

    # A later observation of the top card collapses the correlated Prize slot.
    top_a = result.condition_top("A")
    assert_close(top_a.prize_probability_at(1, "B"), 1.0)
    assert_close(top_a.prize_probability_at(1, "A"), 0.0)

    top_b = result.condition_top("B")
    assert_close(top_b.prize_probability_at(1, "A"), 1.0)
    assert_close(top_b.prize_probability_at(1, "B"), 0.0)

    projected = result.project_prizes()
    assert projected.face_up_positions() == ()
    assert_close(projected.positions.group_probability_at(0, "X"), 1.0)
    assert_close(projected.best_face_down_probability("X"), 1.0)

    # Face-up Prize positions are not legal Arc Phone-style targets.
    visible = PrizeSlotVisibilityBelief(
        PrizePositionBelief.from_known_positions(
            ("A", "B"),
            groups=("A", "B", "X"),
        ),
        (True, False),
    )
    try:
        swap_known_top_with_face_down_prize(
            visible,
            position=0,
            incoming_group="X",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("allowed a face-up Prize as swap target")

    print("Prize/topdeck joint-belief regressions passed")


if __name__ == "__main__":
    main()
