"""Reproduce observer-aware additional Prize staging."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import IdentityLedger, assert_conserved, materialize
from multicopy_zone_state import ZoneCountState
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_pending_observer_extra import stage_additional_prize_front_with_observers
from prize_pending_take import stage_prize_takes_with_observers
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState


def main() -> None:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("other-class", "deck_top"): 1,
                ("trigger-class", "prize"): 1,
                ("switch-class", "prize"): 1,
            }
        )
    )
    ledger = materialize(
        initial,
        card_class="other-class",
        card_name="Other",
        source_zone="deck_top",
        instance_id="top-other",
    )
    ledger = materialize(
        ledger,
        card_class="trigger-class",
        card_name="Jirachi ◇",
        source_zone="prize",
        instance_id="prize-trigger",
    )
    ledger = materialize(
        ledger,
        card_class="switch-class",
        card_name="Switch",
        source_zone="prize",
        instance_id="prize-switch",
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top-other",
        ("prize-trigger", "prize-switch"),
        (False, False),
    )

    prior = TopPrizeJointBelief(
        ("Trigger", "Switch", "Other"),
        (False, False),
        (
            (("Other", ("Trigger", "Switch")), 0.5),
            (("Switch", ("Trigger", "Other")), 0.5),
        ),
    )
    beliefs = ObserverTopPrizeBeliefs(
        (("B", prior), ("A", prior))
    )
    groups = {
        "trigger-class": "Trigger",
        "switch-class": "Switch",
        "other-class": "Other",
    }

    initial_take = stage_prize_takes_with_observers(
        physical,
        beliefs,
        actor_id="B",
        positions=(0,),
        group_by_card_class=groups,
    )
    pending = initial_take.after_pending
    beliefs = initial_take.beliefs_after

    assert pending.pending[0].instance_id == "prize-trigger"
    assert beliefs.belief_for("B").top_probability("Other") == 0.5
    assert beliefs.belief_for("A").top_probability("Other") == 0.5

    extra = stage_additional_prize_front_with_observers(
        pending,
        beliefs,
        actor_id="B",
        position=0,
        group_by_card_class=groups,
    )

    assert tuple(row.instance_id for row in extra.after.pending) == (
        "prize-switch",
        "prize-trigger",
    )
    assert extra.after.physical.prize_instance_ids == ()
    assert extra.after.physical.ledger.instance("prize-switch").zone == "prize_pending"

    assert extra.beliefs_after.belief_for("B").top_probability("Other") == 1.0
    assert extra.beliefs_after.belief_for("A").top_probability("Other") == 0.5

    assert_conserved(initial, extra.after.physical.ledger)
    print("observer-aware additional Prize regression passed")


if __name__ == "__main__":
    main()
