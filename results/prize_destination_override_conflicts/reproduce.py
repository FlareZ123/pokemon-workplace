"""Reproduce ordered destination overrides for taken Prize cards."""

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


def make_pending_state(prize_count: int = 1):
    prize_rows = tuple(
        CardInstance(
            f"prize-{index}",
            f"P{index}",
            f"Prize {index}",
            "prize",
        )
        for index in range(prize_count)
    )
    ledger = IdentityLedger(
        ZoneCountState(),
        prize_rows + (CardInstance("top", "TOP", "Top", "deck_top"),),
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top",
        tuple(row.instance_id for row in prize_rows),
        tuple(False for _ in prize_rows),
    )
    return physical, stage_prize_takes(
        physical,
        positions=tuple(range(prize_count)),
    )


def main() -> None:
    physical, pending = make_pending_state()
    assert pending.physical.ledger.instance("prize-0").zone == "prize_pending"

    ordinary = resolve_pending_prize_with_overrides(pending, ())
    assert ordinary.resolved
    assert ordinary.decision.destination_zone == "hand"
    assert ordinary.resolution is not None
    assert ordinary.resolution.after.physical.ledger.instance("prize-0").zone == "hand"
    assert_conserved(physical.ledger, ordinary.resolution.after.physical.ledger)

    lost_block = PrizeDestinationOverride("Lost Block", "lost_zone")
    smoke = PrizeDestinationOverride("Billowing Smoke", "discard")

    lost = resolve_pending_prize_with_overrides(pending, (lost_block,))
    assert lost.resolved
    assert lost.resolution is not None
    assert lost.resolution.after.physical.ledger.instance("prize-0").zone == "lost_zone"

    discarded = resolve_pending_prize_with_overrides(pending, (smoke,))
    assert discarded.resolved
    assert discarded.resolution is not None
    assert discarded.resolution.after.physical.ledger.instance("prize-0").zone == "discard"

    same_destination = decide_prize_destination(
        (
            PrizeDestinationOverride("Lost Block A", "lost_zone"),
            PrizeDestinationOverride("Lost Block B", "lost_zone"),
        )
    )
    assert same_destination.resolved
    assert same_destination.destination_zone == "lost_zone"

    unresolved = resolve_pending_prize_with_overrides(
        pending,
        (lost_block, smoke),
    )
    assert not unresolved.resolved
    assert unresolved.decision.requires_choice
    assert unresolved.decision.candidate_zones == ("discard", "lost_zone")
    assert pending.physical.ledger.instance("prize-0").zone == "prize_pending"

    choose_lost = resolve_pending_prize_with_overrides(
        pending,
        (lost_block, smoke),
        chosen_effect_id="Lost Block",
    )
    assert choose_lost.resolved
    assert choose_lost.resolution is not None
    assert (
        choose_lost.resolution.after.physical.ledger.instance("prize-0").zone
        == "lost_zone"
    )

    choose_smoke = resolve_pending_prize_with_overrides(
        pending,
        (lost_block, smoke),
        chosen_effect_id="Billowing Smoke",
    )
    assert choose_smoke.resolved
    assert choose_smoke.resolution is not None
    assert (
        choose_smoke.resolution.after.physical.ledger.instance("prize-0").zone
        == "discard"
    )

    physical_two, pending_two = make_pending_state(2)
    first = resolve_pending_prize_with_overrides(
        pending_two,
        (lost_block, smoke),
        chosen_effect_id="Billowing Smoke",
    )
    assert first.resolution is not None
    assert (
        first.resolution.after.physical.ledger.instance("prize-0").zone
        == "discard"
    )
    assert tuple(
        row.instance_id for row in first.resolution.after.pending
    ) == ("prize-1",)

    second = resolve_pending_prize_with_overrides(
        first.resolution.after,
        (lost_block, smoke),
        chosen_effect_id="Lost Block",
    )
    assert second.resolution is not None
    final = second.resolution.after
    assert final.pending == ()
    assert final.physical.ledger.instance("prize-0").zone == "discard"
    assert final.physical.ledger.instance("prize-1").zone == "lost_zone"
    assert_conserved(physical_two.ledger, final.physical.ledger)

    print("Prize destination override ordering regressions passed")


if __name__ == "__main__":
    main()
