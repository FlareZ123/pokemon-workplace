"""Reproduce coupled physical/observer resolution for a Prize batch."""

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
from prize_pending_batch_observer import (
    resolve_batch_instance_destination,
    stage_prize_batch_with_latent_observers,
)
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import TopPrizePhysicalState


GROUPS = {
    "A-class": "A",
    "B-class": "B",
    "X-class": "X",
    "Y-class": "Y",
}


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def make_beliefs() -> ObserverTopPrizeBeliefs:
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


def make_physical():
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("top-a", "A-class", "A", "deck_top"),
            CardInstance("prize-x", "X-class", "X", "prize"),
            CardInstance("prize-b", "B-class", "B", "prize"),
        ),
    )
    return ledger, TopPrizePhysicalState(
        ledger,
        "top-a",
        ("prize-x", "prize-b"),
        (False, False),
    )


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

    smoke_first = resolve_batch_instance_destination(
        state,
        instance_id="prize-b",
        destination_zone="discard",
    )
    assert smoke_first.after_batch is not None
    assert (
        smoke_first.physical_resolution.after.physical.ledger
        .instance("prize-b").zone
        == "discard"
    )
    assert_close(
        smoke_first.after_batch.beliefs
        .belief_for("opponent").top_probability("A"),
        1.0,
    )

    lost_second = resolve_batch_instance_destination(
        smoke_first.after_batch,
        instance_id="prize-x",
        destination_zone="lost_zone",
    )
    assert lost_second.after_batch is None
    final_physical = lost_second.physical_resolution.after.physical
    assert final_physical.ledger.instance("prize-b").zone == "discard"
    assert final_physical.ledger.instance("prize-x").zone == "lost_zone"
    assert final_physical.prize_instance_ids == ()
    assert_close(
        lost_second.after_beliefs.belief_for("opponent").top_probability("A"),
        1.0,
    )
    assert_conserved(initial, final_physical.ledger)

    initial_hidden, physical_hidden = make_physical()
    staged_hidden = stage_prize_batch_with_latent_observers(
        physical_hidden,
        make_beliefs(),
        actor_id="actor",
        positions=(0, 1),
        group_by_card_class=GROUPS,
    )
    b_hidden = resolve_batch_instance_destination(
        staged_hidden.after,
        instance_id="prize-b",
        destination_zone="hand",
    )
    assert b_hidden.after_batch is not None
    x_public = resolve_batch_instance_destination(
        b_hidden.after_batch,
        instance_id="prize-x",
        destination_zone="lost_zone",
    )
    assert x_public.after_batch is None
    assert_close(
        x_public.after_beliefs.belief_for("opponent").top_probability("A"),
        0.5,
    )
    assert_conserved(initial_hidden, x_public.physical_resolution.after.physical.ledger)

    print("Physical pending Prize batch observer regressions passed")


if __name__ == "__main__":
    main()
