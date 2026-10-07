"""Reproduce competing destination overrides for taken Prize cards."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from prize_destination_overrides import (
    PrizeDestinationOverride,
    decide_prize_destination,
    resolve_pending_prize_with_overrides,
)
from prize_pending_take import stage_prize_takes
from top_prize_physical_bridge import TopPrizePhysicalState


def make_pending_state():
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("prize-a", "A", "Prize A", "prize"),
            CardInstance("top", "TOP", "Top", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top",
        ("prize-a",),
        (False,),
    )
    return physical, stage_prize_takes(physical, positions=(0,))


def main() -> None:
    physical, pending = make_pending_state()
    assert pending.physical.ledger.instance("prize-a").zone == "prize_pending"

    ordinary = resolve_pending_prize_with_overrides(pending, ())
    assert ordinary.resolved
    assert ordinary.decision.destination_zone == "hand"
    assert ordinary.resolution is not None
    assert ordinary.resolution.after.physical.ledger.instance("prize-a").zone == "hand"
    assert_conserved(physical.ledger, ordinary.resolution.after.physical.ledger)

    lost_block = PrizeDestinationOverride("Lost Block", "lost_zone")
    lost = resolve_pending_prize_with_overrides(pending, (lost_block,))
    assert lost.resolved
    assert lost.decision.destination_zone == "lost_zone"
    assert lost.resolution is not None
    assert lost.resolution.after.physical.ledger.instance("prize-a").zone == "lost_zone"
    assert_conserved(physical.ledger, lost.resolution.after.physical.ledger)

    smoke = PrizeDestinationOverride("Billowing Smoke", "discard")
    discarded = resolve_pending_prize_with_overrides(pending, (smoke,))
    assert discarded.resolved
    assert discarded.decision.destination_zone == "discard"
    assert discarded.resolution is not None
    assert discarded.resolution.after.physical.ledger.instance("prize-a").zone == "discard"
    assert_conserved(physical.ledger, discarded.resolution.after.physical.ledger)

    same_destination = decide_prize_destination(
        (
            PrizeDestinationOverride("Lost Block A", "lost_zone"),
            PrizeDestinationOverride("Lost Block B", "lost_zone"),
        )
    )
    assert same_destination.resolved
    assert same_destination.destination_zone == "lost_zone"
    assert same_destination.conflicting_zones == ()

    conflict = resolve_pending_prize_with_overrides(
        pending,
        (lost_block, smoke),
    )
    assert not conflict.resolved
    assert conflict.decision.destination_zone is None
    assert conflict.decision.conflicting_zones == ("discard", "lost_zone")

    assert pending.physical.ledger.instance("prize-a").zone == "prize_pending"
    assert pending.pending[0].instance_id == "prize-a"
    assert_conserved(physical.ledger, pending.physical.ledger)

    print("Prize destination override conflict regressions passed")


if __name__ == "__main__":
    main()
