"""Reproduce observer-aware nested Prize barriers inside a sibling batch."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_pending_batch_observer import (
    prepend_additional_prize_with_latent_observers,
    resolve_batch_instance_destination,
    resolve_nested_queue_head_destination,
    stage_prize_batch_with_latent_observers,
)
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState


GROUPS = {
    "A-class": "A",
    "B-class": "B",
    "C-class": "C",
    "X-class": "X",
}


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def make_beliefs() -> ObserverTopPrizeBeliefs:
    belief = TopPrizeJointBelief(
        ("A", "B", "C", "X"),
        (False, False, False),
        (
            (("A", ("X", "B", "C")), 0.5),
            (("C", ("X", "A", "B")), 0.5),
        ),
    )
    return ObserverTopPrizeBeliefs(
        (("actor", belief), ("opponent", belief))
    )


def make_physical():
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("prize-b", "B-class", "B", "prize"),
            CardInstance("prize-c", "C-class", "C", "prize"),
            CardInstance("prize-x", "X-class", "X", "prize"),
            CardInstance("top-a", "A-class", "A", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top-a",
        ("prize-x", "prize-b", "prize-c"),
        (False, False, False),
    )
    return ledger, physical


def raises_value_error(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    initial, physical = make_physical()
    staged = stage_prize_batch_with_latent_observers(
        physical,
        make_beliefs(),
        actor_id="actor",
        positions=(0, 1),
        group_by_card_class=GROUPS,
    )
    state = staged.after
    assert state.order.unresolved_batch_ids == ("prize-x", "prize-b")
    assert state.beliefs.pending_instance_ids == ("prize-x", "prize-b")
    assert_close(
        state.beliefs.belief_for("opponent").top_probability("A"),
        0.5,
    )

    nested = prepend_additional_prize_with_latent_observers(
        state,
        position=0,
    )
    assert tuple(
        row.instance_id for row in nested.order.state.pending
    ) == ("prize-c", "prize-x", "prize-b")
    assert nested.beliefs.pending_instance_ids == (
        "prize-c",
        "prize-x",
        "prize-b",
    )
    assert nested.order.unresolved_batch_ids == ("prize-x", "prize-b")
    assert_close(
        nested.beliefs.belief_for("actor").pending_probability(0, "C"),
        1.0,
    )
    assert_close(
        nested.beliefs.belief_for("opponent").pending_probability(0, "C"),
        0.5,
    )

    assert raises_value_error(
        lambda: nested.order.choose_next("prize-b")
    )

    after_nested = resolve_nested_queue_head_destination(
        nested,
        destination_zone="lost_zone",
    )
    assert after_nested.beliefs.pending_instance_ids == (
        "prize-x",
        "prize-b",
    )
    assert tuple(
        row.instance_id for row in after_nested.order.state.pending
    ) == ("prize-x", "prize-b")
    assert (
        after_nested.order.state.physical.ledger
        .instance("prize-c").zone
        == "lost_zone"
    )
    assert_close(
        after_nested.beliefs.belief_for("opponent").top_probability("A"),
        1.0,
    )

    sibling = resolve_batch_instance_destination(
        after_nested,
        instance_id="prize-b",
        destination_zone="hand",
    )
    assert sibling.after_batch is not None
    assert sibling.after_batch.beliefs.pending_instance_ids == ("prize-x",)
    final = resolve_batch_instance_destination(
        sibling.after_batch,
        instance_id="prize-x",
        destination_zone="hand",
    )
    assert final.after_batch is None
    assert final.physical_resolution.after.pending == ()
    assert_conserved(initial, final.physical_resolution.after.physical.ledger)

    print("Nested Prize observer barrier regressions passed")


if __name__ == "__main__":
    main()
