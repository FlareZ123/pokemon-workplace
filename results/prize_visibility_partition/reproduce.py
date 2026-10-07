"""Reproduce the face-up / face-down Prize visibility partition."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_belief_kernel import PrizeBelief
from prize_visibility_partition import (
    PrizeVisibilityBelief,
    reveal_all_face_down_prizes,
    reveal_random_face_down_prize,
)


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def main() -> None:
    # Same exact total composition: A + one filler.
    total = PrizeBelief.from_exact({"A": 1}, prize_count=2)

    # State 1: A is the face-up card, so A is ineligible for face-down-only effects.
    a_face_up = reveal_random_face_down_prize(
        PrizeVisibilityBelief.all_face_down(total),
        "A",
    )
    assert a_face_up.face_up_group_count("A") == 1
    assert a_face_up.face_up_filler == 0
    assert a_face_up.face_down.prize_count == 1
    assert_close(a_face_up.probability_group_in_face_down("A"), 0.0)

    # State 2: filler is face up, so A is certainly in the one face-down position.
    filler_face_up = reveal_random_face_down_prize(
        PrizeVisibilityBelief.all_face_down(total),
        None,
    )
    assert filler_face_up.face_up_group_count("A") == 0
    assert filler_face_up.face_up_filler == 1
    assert filler_face_up.face_down.prize_count == 1
    assert_close(filler_face_up.probability_group_in_face_down("A"), 1.0)

    # Forgetting visibility collapses both states to the identical total composition.
    assert a_face_up.collapse_total_composition() == total
    assert filler_face_up.collapse_total_composition() == total

    # Therefore total composition alone cannot answer face-down target eligibility.
    assert (
        a_face_up.probability_group_in_face_down("A")
        != filler_face_up.probability_group_in_face_down("A")
    )

    # Partial reveal from an uncertain prior conditions the hidden remainder.
    uncertain = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1},
        pool_size=5,
        prize_count=2,
    )
    after_a = reveal_random_face_down_prize(
        PrizeVisibilityBelief.all_face_down(uncertain),
        "A",
    )
    assert after_a.total_prize_count == 2
    assert after_a.face_up_count == 1
    assert after_a.face_down.prize_count == 1
    assert_close(after_a.probability_group_in_face_down("A"), 0.0)
    assert_close(after_a.probability_group_in_face_down("B"), 1.0 / 4.0)

    all_revealed = reveal_all_face_down_prizes(
        after_a,
        (None,),
    )
    assert all_revealed.total_prize_count == 2
    assert all_revealed.face_up_count == 2
    assert all_revealed.face_down.prize_count == 0
    assert all_revealed.face_down.is_exact()

    try:
        reveal_all_face_down_prizes(after_a, ())
    except ValueError:
        pass
    else:
        raise AssertionError("accepted incomplete full-reveal observation list")

    print("Prize visibility partition regressions passed")


if __name__ == "__main__":
    main()
