"""Reproduce the composition / position / visibility separation."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import (
    PrizeSlotVisibilityBelief,
    known_group_at_face_up,
)


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def main() -> None:
    positions = PrizePositionBelief.from_known_positions(
        ("A", None),
        groups=("A",),
    )

    # Same exact composition and same exact physical position mapping.
    # Only face-up status differs.
    a_face_up = PrizeSlotVisibilityBelief(
        positions,
        (True, False),
    )
    filler_face_up = PrizeSlotVisibilityBelief(
        positions,
        (False, True),
    )

    assert a_face_up.positions == filler_face_up.positions
    assert (
        a_face_up.positions.composition_distribution()
        == filler_face_up.positions.composition_distribution()
    )
    assert known_group_at_face_up(a_face_up, 0) == "A"
    assert known_group_at_face_up(filler_face_up, 1) is None

    # A face-down-only action cannot target slot 0 in the first state.
    assert_close(a_face_up.best_face_down_probability("A"), 0.0)
    # The same A at the same known physical slot is eligible in the second.
    assert_close(filler_face_up.best_face_down_probability("A"), 1.0)

    # Partial revelation from unknown position mapping conditions identity.
    unknown = PrizePositionBelief.from_exact_composition(
        {"A": 1},
        prize_count=2,
    )
    all_down = PrizeSlotVisibilityBelief.all_face_down(unknown)

    reveal_a = all_down.reveal_position(0, "A")
    assert reveal_a.face_up_positions() == (0,)
    assert reveal_a.face_down_positions() == (1,)
    assert_close(reveal_a.best_face_down_probability("A"), 0.0)

    reveal_filler = all_down.reveal_position(0, None)
    assert reveal_filler.face_up_positions() == (0,)
    assert reveal_filler.face_down_positions() == (1,)
    assert_close(reveal_filler.best_face_down_probability("A"), 1.0)

    # An E-35-style shuffle erases face-up status and position mapping while
    # preserving exact composition.
    shuffled = a_face_up.turn_all_face_down_and_shuffle()
    assert shuffled.face_up_positions() == ()
    assert shuffled.face_down_positions() == (0, 1)
    assert (
        shuffled.positions.composition_distribution()
        == positions.composition_distribution()
    )
    assert_close(shuffled.best_face_down_probability("A"), 1.0 / 2.0)

    # A publicly face-up slot must have one exact grouped identity.
    try:
        PrizeSlotVisibilityBelief(
            unknown,
            (True, False),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("allowed uncertain identity at face-up position")

    print("Prize slot visibility composition regressions passed")


if __name__ == "__main__":
    main()
