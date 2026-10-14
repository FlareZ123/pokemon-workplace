"""Reproduce E-31 public/private observer updates across pending Prize batches."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_profiles import build_before_hand_prize_profiles
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_batch_belief import finish_pending_prize_batch
from physical_before_hand_batch_bridge import (
    resolve_direct_before_hand_with_batch_beliefs,
)
from physical_pending_prize_batch_bridge import stage_physical_pending_batch
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState


def close(actual: float, expected: float) -> None:
    assert abs(actual - expected) < 1e-12, (actual, expected)


def raises_value_error(fn) -> None:
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def make_example():
    prior = TopPrizeJointBelief(
        ("A", "C", "T"),
        (False, False),
        (
            (("A", ("C", "T")), 0.5),
            (("T", ("A", "C")), 0.5),
        ),
    )
    beliefs = ObserverTopPrizeBeliefs(
        (("actor", prior), ("opponent", prior)),
    )
    rows = (
        CardInstance("top", "A", "Top Card", "deck_top"),
        CardInstance("chansey", "sv3pt5-113", "Chansey", "prize"),
        CardInstance("treasure", "swsh7-165", "Treasure Energy", "prize"),
    )
    physical = TopPrizePhysicalState(
        IdentityLedger(
            ZoneCountState(),
            tuple(sorted(rows, key=lambda instance: instance.instance_id)),
        ),
        "top",
        ("chansey", "treasure"),
        (False, False),
    )
    group_by_class = {
        "A": "A",
        "sv3pt5-113": "C",
        "swsh7-165": "T",
    }
    return physical, beliefs, group_by_class


def main() -> None:
    profiles = {
        profile.card_id: profile
        for profile in build_before_hand_prize_profiles(ROOT / "resources")
    }
    chansey = profiles["sv3pt5-113"]
    treasure = profiles["swsh7-165"]
    physical, beliefs, group_by_class = make_example()
    batch = stage_physical_pending_batch(
        physical, beliefs, actor_id="actor", positions=(0, 1),
        group_by_card_class=group_by_class,
    )
    close(batch.observers.belief_for("opponent").top_probability("A"), 0.5)

    # Lucky Bonus sends Chansey into public play. The opponent now knows
    # which original Prize position held Chansey, narrowing the deck top.
    bench, trigger = resolve_direct_before_hand_with_batch_beliefs(
        batch, chansey, actor_id="actor", group_by_card_class=group_by_class,
        use_trigger=True, during_own_turn=True, bench_open=True,
        board_object_id="chansey-bench", coin_heads=False,
    )
    assert trigger.used_trigger
    assert trigger.additional_prize_awards == 0
    assert bench.pending.physical.ledger.instance("chansey").zone == "in_play"
    close(bench.observers.belief_for("opponent").top_probability("A"), 1.0)

    attached, effect = resolve_direct_before_hand_with_batch_beliefs(
        bench, treasure, actor_id="actor", group_by_card_class=group_by_class,
        use_trigger=True, during_own_turn=True, attached_to="holder",
    )
    assert effect.used_trigger
    assert attached.pending.physical.ledger.instance("treasure").zone == "attached"
    assert attached.pending.pending == ()
    close(finish_pending_prize_batch(attached.observers).belief_for("opponent").top_probability("A"), 1.0)
    assert_conserved(physical.ledger, attached.pending.physical.ledger)

    # Declining Chansey keeps it private. Only the later attached public
    # Treasure Energy reveals the remaining correlation.
    private, declined = resolve_direct_before_hand_with_batch_beliefs(
        batch, chansey, actor_id="actor", group_by_card_class=group_by_class,
        use_trigger=False, during_own_turn=True,
    )
    assert not declined.used_trigger
    close(private.observers.belief_for("opponent").top_probability("A"), 0.5)
    public, _ = resolve_direct_before_hand_with_batch_beliefs(
        private, treasure, actor_id="actor", group_by_card_class=group_by_class,
        use_trigger=True, during_own_turn=True, attached_to="holder",
    )
    close(public.observers.belief_for("opponent").top_probability("A"), 1.0)
    assert_conserved(physical.ledger, public.pending.physical.ledger)

    # Billowing Smoke replaces hand destination with public discard.
    # The pre-hand trigger must be unavailable in that branch.
    raises_value_error(lambda: resolve_direct_before_hand_with_batch_beliefs(
        batch, chansey, actor_id="actor", group_by_card_class=group_by_class,
        use_trigger=True, during_own_turn=True, bench_open=True,
        board_object_id="chansey-bench", coin_heads=False,
        pre_hand_destination="discard",
    ))
    discarded, _ = resolve_direct_before_hand_with_batch_beliefs(
        batch, chansey, actor_id="actor", group_by_card_class=group_by_class,
        use_trigger=False, during_own_turn=True,
        pre_hand_destination="discard",
    )
    assert discarded.pending.physical.ledger.instance("chansey").zone == "discard"
    close(discarded.observers.belief_for("opponent").top_probability("A"), 1.0)
    assert_conserved(physical.ledger, discarded.pending.physical.ledger)

    print("E-31 pending Prize observer visibility regressions passed")


if __name__ == "__main__":
    main()
