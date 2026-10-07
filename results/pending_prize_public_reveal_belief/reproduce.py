"""Reproduce latent pending-Prize identity and public destination evidence."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    independent_top_prize_belief,
    resolve_optional_top_prize_swap,
)
from pending_prize_identity_belief import (
    destination_visibility,
    resolve_single_pending_visibility,
    stage_one_pending_prize_for_observers,
)
from prize_joint_position_removal import remove_prize_position_for_observers
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def make_post_swap_beliefs() -> ObserverTopPrizeBeliefs:
    positions = PrizePositionBelief.from_exact_composition(
        {"A": 1, "B": 1, "X": 0, "Y": 0},
        prize_count=2,
    )
    prizes = PrizeSlotVisibilityBelief.all_face_down(positions)
    prior = independent_top_prize_belief(
        prizes,
        {"X": 0.5, "Y": 0.5},
    )
    observers = ObserverTopPrizeBeliefs(
        (("actor", prior), ("opponent", prior))
    )
    return resolve_optional_top_prize_swap(
        observers,
        actor_id="actor",
        actor_observed_top="X",
        swap_probability_by_top={"X": 1.0, "Y": 0.25},
        observed_swap=True,
        position=0,
    )


def main() -> None:
    post_swap = make_post_swap_beliefs()

    latent = stage_one_pending_prize_for_observers(
        post_swap,
        position=1,
        visible_groups={"actor": "B"},
    )
    actor = latent.belief_for("actor")
    opponent = latent.belief_for("opponent")

    assert_close(actor.pending_probability("B"), 1.0)
    assert_close(actor.top_probability("A"), 1.0)
    assert_close(opponent.pending_probability("B"), 0.5)
    assert_close(opponent.top_probability("A"), 0.5)

    observer_ids = ("actor", "opponent")

    public = resolve_single_pending_visibility(
        latent,
        visible_groups=destination_visibility(
            observer_ids,
            actor_id="actor",
            destination_zone="discard",
            observed_group="B",
        ),
    )
    assert_close(public.belief_for("actor").top_probability("A"), 1.0)
    assert_close(public.belief_for("opponent").top_probability("A"), 1.0)

    lost = resolve_single_pending_visibility(
        latent,
        visible_groups=destination_visibility(
            observer_ids,
            actor_id="actor",
            destination_zone="lost_zone",
            observed_group="B",
        ),
    )
    assert_close(lost.belief_for("opponent").top_probability("A"), 1.0)

    hidden_hand = resolve_single_pending_visibility(
        latent,
        visible_groups=destination_visibility(
            observer_ids,
            actor_id="actor",
            destination_zone="hand",
            observed_group="B",
        ),
    )
    assert_close(hidden_hand.belief_for("actor").top_probability("A"), 1.0)
    assert_close(hidden_hand.belief_for("opponent").top_probability("A"), 0.5)

    marginalized = remove_prize_position_for_observers(
        post_swap,
        position=1,
        visible_groups={"actor": "B"},
    )
    assert_close(marginalized.belief_for("opponent").top_probability("A"), 0.5)

    print("Pending Prize public-destination belief regressions passed")


if __name__ == "__main__":
    main()
