"""Reproduce observer-relative Arc Phone-style swap beliefs."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    condition_top_observations,
    independent_top_prize_belief,
    resolve_optional_top_prize_swap,
)
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

    post = resolve_optional_top_prize_swap(
        observers,
        actor_id="actor",
        actor_observed_top="X",
        swap_probability_by_top={"X": 1.0, "Y": 1.0 / 4.0},
        observed_swap=True,
        position=0,
    )

    actor = post.belief_for("actor")
    opponent = post.belief_for("opponent")

    assert_close(actor.prize_probability_at(0, "X"), 1.0)
    assert_close(opponent.prize_probability_at(0, "X"), 4.0 / 5.0)
    assert_close(opponent.prize_probability_at(0, "Y"), 1.0 / 5.0)

    assert_close(actor.top_probability("A"), 1.0 / 2.0)
    assert_close(actor.top_probability("B"), 1.0 / 2.0)
    assert_close(opponent.top_probability("A"), 1.0 / 2.0)
    assert_close(opponent.top_probability("B"), 1.0 / 2.0)

    for belief in (actor, opponent):
        assert_close(
            belief.joint_probability(
                top_group="A",
                prize_position=1,
                prize_group="A",
            ),
            0.0,
        )
        assert_close(
            belief.joint_probability(
                top_group="A",
                prize_position=1,
                prize_group="B",
            ),
            1.0 / 2.0,
        )

    later = condition_top_observations(
        post,
        visible_groups={"actor": "A"},
    )
    actor_later = later.belief_for("actor")
    opponent_later = later.belief_for("opponent")

    assert_close(actor_later.prize_probability_at(1, "B"), 1.0)
    assert_close(actor_later.prize_probability_at(1, "A"), 0.0)
    assert_close(opponent_later.prize_probability_at(1, "B"), 1.0 / 2.0)
    assert_close(opponent_later.prize_probability_at(1, "A"), 1.0 / 2.0)

    declined = resolve_optional_top_prize_swap(
        observers,
        actor_id="actor",
        actor_observed_top="Y",
        swap_probability_by_top={"X": 1.0, "Y": 1.0 / 4.0},
        observed_swap=False,
        position=None,
    )
    assert_close(declined.belief_for("actor").top_probability("Y"), 1.0)
    assert_close(declined.belief_for("opponent").top_probability("Y"), 1.0)

    try:
        resolve_optional_top_prize_swap(
            observers,
            actor_id="actor",
            actor_observed_top="X",
            swap_probability_by_top={"X": 1.0, "Y": 1.0 / 4.0},
            observed_swap=False,
            position=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("declined swap accepted a Prize position")

    try:
        resolve_optional_top_prize_swap(
            observers,
            actor_id="actor",
            actor_observed_top="X",
            swap_probability_by_top={"X": 0.0, "Y": 1.0},
            observed_swap=True,
            position=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("accepted an actor decision with zero policy probability")

    print("Observer-indexed top/Prize swap regressions passed")


if __name__ == "__main__":
    main()
