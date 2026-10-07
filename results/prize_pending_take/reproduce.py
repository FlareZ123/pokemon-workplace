"""Reproduce the E-31 Prize pending queue and observer update."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    independent_top_prize_belief,
    resolve_optional_top_prize_swap,
)
from prize_pending_take import (
    resolve_next_pending_prize,
    stage_additional_prize_front,
    stage_prize_takes,
    stage_prize_takes_with_observers,
)
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import TopPrizePhysicalState


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def make_swapped_state():
    groups = {"A": "A", "B": "B", "X": "X", "Y": "Y"}

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
    observers = resolve_optional_top_prize_swap(
        observers,
        actor_id="actor",
        actor_observed_top="X",
        swap_probability_by_top={"X": 1.0, "Y": 1.0 / 4.0},
        observed_swap=True,
        position=0,
    )

    ledger = IdentityLedger(
        ZoneCountState.from_mapping({("Y", "deck"): 1}),
        (
            CardInstance("a", "A", "A", "deck_top"),
            CardInstance("b", "B", "B", "prize"),
            CardInstance("x", "X", "X", "prize"),
        ),
    )
    physical = TopPrizePhysicalState(
        ledger,
        "a",
        ("x", "b"),
        (False, False),
    )
    return physical, observers, groups


def main() -> None:
    physical, observers, groups = make_swapped_state()

    staged = stage_prize_takes_with_observers(
        physical,
        observers,
        actor_id="actor",
        positions=(1,),
        group_by_card_class=groups,
    )

    pending = staged.after_pending
    assert pending.physical.prize_instance_ids == ("x",)
    assert len(pending.pending) == 1
    assert pending.pending[0].instance_id == "b"
    assert pending.pending[0].was_face_down
    assert pending.physical.ledger.instance("b").zone == "prize_pending"
    assert_conserved(physical.ledger, pending.physical.ledger)

    actor = staged.beliefs_after.belief_for("actor")
    opponent = staged.beliefs_after.belief_for("opponent")

    # Seeing B before hand entry reveals the anti-correlated top A to the actor.
    assert_close(actor.top_probability("A"), 1.0)
    assert_close(opponent.top_probability("A"), 1.0 / 2.0)

    resolved = resolve_next_pending_prize(pending)
    assert resolved.resolved.instance_id == "b"
    assert resolved.resolved.was_face_down
    assert resolved.after.pending == ()
    assert resolved.after.physical.ledger.instance("b").zone == "hand"
    assert_conserved(physical.ledger, resolved.after.physical.ledger)

    # Multiple Prize cards are staged in caller-supplied order and resolved
    # strictly one at a time. A before-hand effect can route a card directly
    # into play without first entering hand.
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("a", "A", "A", "prize"),
            CardInstance("b", "B", "B", "prize"),
            CardInstance("x", "X", "X", "deck_top"),
        ),
    )
    multi_physical = TopPrizePhysicalState(
        ledger,
        "x",
        ("a", "b"),
        (False, False),
    )
    multi = stage_prize_takes(
        multi_physical,
        positions=(1, 0),
    )
    assert tuple(row.instance_id for row in multi.pending) == ("b", "a")
    assert multi.physical.prize_instance_ids == ()

    first = resolve_next_pending_prize(multi)
    assert first.resolved.instance_id == "b"
    assert first.after.physical.ledger.instance("b").zone == "hand"
    assert tuple(row.instance_id for row in first.after.pending) == ("a",)

    second = resolve_next_pending_prize(
        first.after,
        destination_zone="in_play",
        board_object_id="bench-a",
    )
    assert second.resolved.instance_id == "a"
    assert second.resolved.was_face_down
    assert second.after.pending == ()
    assert second.after.physical.ledger.instance("a").zone == "in_play"
    assert (
        second.after.physical.ledger.instance("a").board_object_id
        == "bench-a"
    )
    assert_conserved(multi_physical.ledger, second.after.physical.ledger)

    # An extra Prize taken while another before-hand card is waiting must
    # become the next pending card, ahead of the older sibling queue.
    nested_ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("extra", "EXTRA", "Extra", "prize"),
            CardInstance("old", "OLD", "Old", "prize_pending"),
            CardInstance("top", "TOP", "Top", "deck_top"),
        ),
    )
    nested_physical = TopPrizePhysicalState(
        nested_ledger,
        "top",
        ("extra",),
        (False,),
    )
    nested_state = PrizePendingTakeState(
        nested_physical,
        (PendingPrize("old", True),),
    )
    nested = stage_additional_prize_front(
        nested_state,
        position=0,
    )
    assert tuple(row.instance_id for row in nested.pending) == (
        "extra",
        "old",
    )
    assert nested.physical.prize_instance_ids == ()

    print("Prize pending-take regressions passed")


if __name__ == "__main__":
    main()
