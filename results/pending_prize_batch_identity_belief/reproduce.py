"""Reproduce observer beliefs for a multi-card pending Prize batch."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    independent_top_prize_belief,
    resolve_optional_top_prize_swap,
)
from pending_prize_batch_identity_belief import (
    project_completed_batch,
    resolve_pending_instance_visibility,
    stage_pending_prize_batch_for_observers,
)
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


def public(group):
    return {"actor": group, "opponent": group}


def private_to_actor(group):
    return {"actor": group}


def main() -> None:
    staged = stage_pending_prize_batch_for_observers(
        make_post_swap_beliefs(),
        positions=(0, 1),
        pending_instance_ids=("x-card", "b-card"),
        visible_groups={"actor": ("X", "B")},
    )

    actor = staged.belief_for("actor")
    opponent = staged.belief_for("opponent")
    assert_close(actor.top_probability("A"), 1.0)
    assert_close(opponent.top_probability("A"), 0.5)
    assert_close(opponent.pending_probability(0, "X"), 0.8)
    assert_close(opponent.pending_probability(1, "B"), 0.5)

    b_public_first = resolve_pending_instance_visibility(
        staged,
        instance_id="b-card",
        visible_groups=public("B"),
    )
    assert b_public_first.pending_instance_ids == ("x-card",)
    assert_close(
        b_public_first.belief_for("opponent").top_probability("A"),
        1.0,
    )
    assert_close(
        b_public_first.belief_for("opponent").pending_probability(0, "X"),
        0.8,
    )

    both_public = resolve_pending_instance_visibility(
        b_public_first,
        instance_id="x-card",
        visible_groups=public("X"),
    )
    final_public = project_completed_batch(both_public)
    assert_close(final_public.belief_for("opponent").top_probability("A"), 1.0)

    x_public_first = resolve_pending_instance_visibility(
        staged,
        instance_id="x-card",
        visible_groups=public("X"),
    )
    assert_close(
        x_public_first.belief_for("opponent").top_probability("A"),
        0.5,
    )
    assert_close(
        x_public_first.belief_for("opponent").pending_probability(0, "B"),
        0.5,
    )

    b_public_second = resolve_pending_instance_visibility(
        x_public_first,
        instance_id="b-card",
        visible_groups=public("B"),
    )
    final_reverse = project_completed_batch(b_public_second)
    assert_close(final_reverse.belief_for("opponent").top_probability("A"), 1.0)

    b_hidden = resolve_pending_instance_visibility(
        staged,
        instance_id="b-card",
        visible_groups=private_to_actor("B"),
    )
    x_public_after_hidden = resolve_pending_instance_visibility(
        b_hidden,
        instance_id="x-card",
        visible_groups=public("X"),
    )
    final_mixed = project_completed_batch(x_public_after_hidden)
    assert_close(final_mixed.belief_for("actor").top_probability("A"), 1.0)
    assert_close(final_mixed.belief_for("opponent").top_probability("A"), 0.5)

    print("Pending Prize batch identity-belief regressions passed")


if __name__ == "__main__":
    main()
