"""Reproduce observer-relative Prize-position removal."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    independent_top_prize_belief,
    resolve_optional_top_prize_swap,
)
from prize_joint_position_removal import remove_prize_position_for_observers
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def main() -> None:
    positions = PrizePositionBelief.from_exact_composition(
        {"A": 1, "B": 1, "X": 0, "Y": 0},
        prize_count=2,
    )
    prizes = PrizeSlotVisibilityBelief.all_face_down(positions)
    prior = independent_top_prize_belief(
        prizes,
        {"X": 1.0 / 2.0, "Y": 1.0 / 2.0},
    )
    observers = ObserverTopPrizeBeliefs(
        (("actor", prior), ("opponent", prior))
    )

    swapped = resolve_optional_top_prize_swap(
        observers,
        actor_id="actor",
        actor_observed_top="X",
        swap_probability_by_top={"X": 1.0, "Y": 1.0 / 4.0},
        observed_swap=True,
        position=0,
    )

    # Physical truth for this branch is top=A, slots=(X, B). The actor takes
    # slot 1 and privately sees B. The opponent sees only that slot leave.
    after_take = remove_prize_position_for_observers(
        swapped,
        position=1,
        visible_groups={"actor": "B"},
    )
    actor = after_take.belief_for("actor")
    opponent = after_take.belief_for("opponent")

    assert actor.prize_count == 1
    assert opponent.prize_count == 1

    # The actor learns the correlated top card without looking at the top.
    assert_close(actor.top_probability("A"), 1.0)
    assert_close(actor.top_probability("B"), 0.0)

    # The opponent did not see the removed identity, so top uncertainty remains.
    assert_close(opponent.top_probability("A"), 1.0 / 2.0)
    assert_close(opponent.top_probability("B"), 1.0 / 2.0)

    # The untouched inserted Prize keeps the observers' earlier disagreement.
    assert_close(actor.prize_probability_at(0, "X"), 1.0)
    assert_close(opponent.prize_probability_at(0, "X"), 4.0 / 5.0)
    assert_close(opponent.prize_probability_at(0, "Y"), 1.0 / 5.0)

    try:
        remove_prize_position_for_observers(
            swapped,
            position=1,
            visible_groups={"actor": "X"},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("accepted an impossible observed Prize identity")

    print("Joint Prize-position removal regressions passed")


if __name__ == "__main__":
    main()
