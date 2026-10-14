"""Regression for correlated multi-Prize visibility and conserved physical queue."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_batch_belief import (
    finish_pending_prize_batch,
    resolve_next_pending_batch_visibility,
    stage_pending_prize_batch,
)
from physical_pending_prize_batch_bridge import (
    resolve_physical_next_pending_batch,
    stage_physical_additional_pending_front,
    stage_physical_pending_batch,
)
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState


def close(actual: float, expected: float) -> None:
    assert abs(actual - expected) < 1e-12, (actual, expected)


def raises(exception: type[Exception], call) -> None:
    try:
        call()
    except exception:
        return
    raise AssertionError(f"expected {exception.__name__}")


def example() -> tuple[TopPrizePhysicalState, ObserverTopPrizeBeliefs]:
    # Two equally possible grouped assignments, correlated with the top card.
    # Physical truth is the first branch. An actor can inspect staged Prizes.
    prior = TopPrizeJointBelief(
        ("A", "B", "X", "C"),
        (False, False, False),
        (
            (("A", ("B", "X", "C")), 0.5),
            (("B", ("X", "A", "C")), 0.5),
        ),
    )
    observers = ObserverTopPrizeBeliefs(
        (("actor", prior), ("opponent", prior)),
    )
    rows = (
        CardInstance("top", "A", "Top A", "deck_top"),
        CardInstance("p0", "B", "Prize B", "prize"),
        CardInstance("p1", "X", "Prize X", "prize"),
        CardInstance("p2", "C", "Prize C", "prize"),
    )
    physical = TopPrizePhysicalState(
        IdentityLedger(ZoneCountState(), rows),
        "top",
        ("p0", "p1", "p2"),
        (False, False, False),
    )
    return physical, observers


def main() -> None:
    physical, observers = example()
    by_class = {group: group for group in ("A", "B", "X", "C")}

    staged = stage_physical_pending_batch(
        physical, observers,
        actor_id="actor",
        positions=(0, 1),
        group_by_card_class=by_class,
    )
    assert tuple(row.instance_id for row in staged.pending.pending) == ("p0", "p1")
    assert staged.pending.physical.prize_instance_ids == ("p2",)
    close(staged.observers.belief_for("actor").top_probability("A"), 1.0)
    close(staged.observers.belief_for("opponent").top_probability("A"), 0.5)
    close(staged.observers.belief_for("opponent").pending_probability("p1", "X"), 0.5)

    # First Prize is hidden in hand. The second becomes public, revealing the
    # correlation with the deck top even though the first identity was removed.
    private_first = resolve_physical_next_pending_batch(
        staged, actor_id="actor",
        destination_zone="hand", group_by_card_class=by_class,
    )
    close(private_first.observers.belief_for("opponent").top_probability("A"), 0.5)
    assert private_first.observers.belief_for("opponent").pending_ids == ("p1",)
    lost_second = resolve_physical_next_pending_batch(
        private_first, actor_id="actor",
        destination_zone="lost_zone", group_by_card_class=by_class,
    )
    close(lost_second.observers.belief_for("opponent").top_probability("A"), 1.0)
    assert lost_second.pending.pending == ()
    final = finish_pending_prize_batch(lost_second.observers)
    close(final.belief_for("opponent").top_probability("A"), 1.0)
    assert lost_second.pending.physical.ledger.instance("p0").zone == "hand"
    assert lost_second.pending.physical.ledger.instance("p1").zone == "lost_zone"
    assert_conserved(physical.ledger, lost_second.pending.physical.ledger)

    # A public first destination reveals early, even while the next card
    # remains physically pending.
    revealed_first = resolve_physical_next_pending_batch(
        staged, actor_id="actor",
        destination_zone="discard", group_by_card_class=by_class,
    )
    close(revealed_first.observers.belief_for("opponent").top_probability("A"), 1.0)
    raises(ValueError, lambda: finish_pending_prize_batch(revealed_first.observers))

    # Additional prizes can be inserted at the front without losing earlier
    # unresolved identities. Original selected slots are deliberately reversed.
    initial = stage_physical_pending_batch(
        physical, observers,
        actor_id="actor",
        positions=(2, 1),
        group_by_card_class=by_class,
    )
    extra = stage_physical_additional_pending_front(
        initial, actor_id="actor", position=0, group_by_card_class=by_class,
    )
    assert tuple(row.instance_id for row in extra.pending.pending) == (
        "p0", "p2", "p1",
    )
    assert extra.observers.belief_for("actor").pending_ids == ("p0", "p2", "p1")
    close(extra.observers.belief_for("opponent").top_probability("A"), 0.5)
    second = resolve_physical_next_pending_batch(
        extra, actor_id="actor", destination_zone="hand",
        group_by_card_class=by_class,
    )
    third = resolve_physical_next_pending_batch(
        second, actor_id="actor", destination_zone="hand",
        group_by_card_class=by_class,
    )
    fourth = resolve_physical_next_pending_batch(
        third, actor_id="actor", destination_zone="discard",
        group_by_card_class=by_class,
    )
    assert fourth.pending.pending == ()
    close(fourth.observers.belief_for("opponent").top_probability("A"), 1.0)
    assert_conserved(physical.ledger, fourth.pending.physical.ledger)

    # Reject missing, duplicated, out-of-order and impossible observations.
    raises(ValueError, lambda: stage_pending_prize_batch(
        observers, positions=(0, 0), pending_ids=("p0", "p1"),
        visible_groups={},
    ))
    raises(ValueError, lambda: stage_pending_prize_batch(
        observers, positions=(0, 1), pending_ids=("p0",),
        visible_groups={},
    ))
    raises(IndexError, lambda: stage_pending_prize_batch(
        observers, positions=(3,), pending_ids=("p3",),
        visible_groups={},
    ))
    raises(ValueError, lambda: stage_pending_prize_batch(
        observers, positions=(0,), pending_ids=("p0",),
        visible_groups={"actor": {"unknown-id": "A"}},
    ))
    raises(ValueError, lambda: stage_pending_prize_batch(
        observers, positions=(0,), pending_ids=("p0",),
        visible_groups={"actor": {"p0": "C"}},
    ))
    raises(ValueError, lambda: resolve_next_pending_batch_visibility(
        staged.observers, instance_id="p1", visible_groups={},
    ))
    raises(ValueError, lambda: resolve_next_pending_batch_visibility(
        staged.observers, instance_id="p0",
        visible_groups={"opponent": "C"},
    ))
    raises(ValueError, lambda: stage_physical_additional_pending_front(
        staged, actor_id="actor", position=4, group_by_card_class=by_class,
    ))

    print("Correlated pending Prize batch regressions passed")


if __name__ == "__main__":
    main()
