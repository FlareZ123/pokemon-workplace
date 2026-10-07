"""Reproduce owner-selected E-31 sibling ordering with nested barriers."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import (
    PrizePendingTakeState,
    resolve_next_pending_prize,
    stage_additional_prize_front,
    stage_prize_takes,
)
from top_prize_physical_bridge import TopPrizePhysicalState


def make_initial_state() -> tuple[TopPrizePhysicalState, IdentityLedger]:
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("chansey", "sv3pt5-113", "Chansey", "prize"),
            CardInstance("dream", "swsh7-146", "Dream Ball", "prize"),
            CardInstance("extra", "EXTRA", "Extra Prize", "prize"),
            CardInstance("top", "TOP", "Top", "deck_top"),
        ),
    )
    return (
        TopPrizePhysicalState(
            ledger,
            "top",
            ("chansey", "dream", "extra"),
            (False, False, False),
        ),
        ledger,
    )


def stage_two() -> tuple[PrizePendingTakeState, IdentityLedger]:
    physical, ledger = make_initial_state()
    return stage_prize_takes(physical, positions=(0, 1)), ledger


def main() -> None:
    staged, initial_ledger = stage_two()
    assert tuple(row.instance_id for row in staged.pending) == (
        "chansey",
        "dream",
    )

    order = PendingPrizeBatchOrder.from_staged(staged)

    dream_first = order.choose_next("dream")
    assert tuple(row.instance_id for row in dream_first.pending) == (
        "dream",
        "chansey",
    )

    chansey_first = order.choose_next("chansey")
    assert tuple(row.instance_id for row in chansey_first.pending) == (
        "chansey",
        "dream",
    )

    chansey_done = resolve_next_pending_prize(
        chansey_first,
        destination_zone="in_play",
        board_object_id="bench-chansey",
    ).after
    nested = stage_additional_prize_front(chansey_done, position=0)
    order = order.advance_after_resolution(
        nested,
        resolved_instance_id="chansey",
    )
    assert order is not None
    assert tuple(row.instance_id for row in order.state.pending) == (
        "extra",
        "dream",
    )

    try:
        order.choose_next("dream")
    except ValueError:
        pass
    else:
        raise AssertionError("same-batch sibling skipped unresolved nested Prize work")

    extra_done = resolve_next_pending_prize(order.state).after
    order = order.rebind(extra_done)
    dream_next = order.choose_next("dream")
    assert tuple(row.instance_id for row in dream_next.pending) == ("dream",)

    dream_done = resolve_next_pending_prize(dream_next).after
    order = order.advance_after_resolution(
        dream_done,
        resolved_instance_id="dream",
    )
    assert order is None
    assert_conserved(initial_ledger, dream_done.physical.ledger)

    print("E-31 sibling ordering and nested barrier regressions passed")


if __name__ == "__main__":
    main()
