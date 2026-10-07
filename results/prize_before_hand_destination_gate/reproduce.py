"""Reproduce destination-gated Prize-origin before-hand effects."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_executor import (
    begin_before_hand_item_play,
    resolve_direct_before_hand_trigger,
)
from before_hand_prize_profiles import build_before_hand_prize_profiles
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from prize_destination_overrides import (
    PrizeDestinationOverride,
    decide_prize_destination,
)
from prize_pending_take import PendingPrize, PrizePendingTakeState
from top_prize_physical_bridge import TopPrizePhysicalState


def make_pending(card_id: str, card_name: str):
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("pending", card_id, card_name, "prize_pending"),
            CardInstance("top", "top-class", "Top Card", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(ledger, "top", (), ())
    return ledger, PrizePendingTakeState(
        physical,
        (PendingPrize("pending", True),),
    )


def raises_value_error(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    profiles = {
        row.card_id: row
        for row in build_before_hand_prize_profiles(ROOT / "resources")
    }

    chansey = profiles["sv3pt5-113"]
    treasure = profiles["swsh7-165"]
    dream_ball = profiles["swsh7-146"]

    smoke = PrizeDestinationOverride("Billowing Smoke", "discard")
    lost_block = PrizeDestinationOverride("Lost Block", "lost_zone")
    smoke_destination = decide_prize_destination((smoke,)).destination_zone
    lost_destination = decide_prize_destination((lost_block,)).destination_zone
    assert smoke_destination == "discard"
    assert lost_destination == "lost_zone"

    initial, pending = make_pending("sv3pt5-113", "Chansey")
    assert raises_value_error(
        lambda: resolve_direct_before_hand_trigger(
            pending,
            chansey,
            use_trigger=True,
            during_own_turn=True,
            bench_open=True,
            board_object_id="chansey-object",
            coin_heads=False,
            pre_hand_destination=smoke_destination,
        )
    )
    declined = resolve_direct_before_hand_trigger(
        pending,
        chansey,
        use_trigger=False,
        during_own_turn=True,
        pre_hand_destination=smoke_destination,
    )
    assert declined.after.physical.ledger.instance("pending").zone == "discard"
    assert_conserved(initial, declined.after.physical.ledger)

    initial, pending = make_pending("swsh7-165", "Treasure Energy")
    assert raises_value_error(
        lambda: resolve_direct_before_hand_trigger(
            pending,
            treasure,
            use_trigger=True,
            during_own_turn=True,
            attached_to="holder",
            pre_hand_destination=lost_destination,
        )
    )
    redirected = resolve_direct_before_hand_trigger(
        pending,
        treasure,
        use_trigger=False,
        during_own_turn=True,
        pre_hand_destination=lost_destination,
    )
    assert redirected.after.physical.ledger.instance("pending").zone == "lost_zone"
    assert_conserved(initial, redirected.after.physical.ledger)

    initial, pending = make_pending("swsh7-146", "Dream Ball")
    assert raises_value_error(
        lambda: begin_before_hand_item_play(
            pending,
            dream_ball,
            during_own_turn=True,
            pre_hand_destination=smoke_destination,
        )
    )
    assert pending.physical.ledger.instance("pending").zone == "prize_pending"
    assert_conserved(initial, pending.physical.ledger)

    initial, pending = make_pending("swsh7-165", "Treasure Energy")
    attached = resolve_direct_before_hand_trigger(
        pending,
        treasure,
        use_trigger=True,
        during_own_turn=True,
        attached_to="holder",
    )
    card = attached.after.physical.ledger.instance("pending")
    assert card.zone == "attached"
    assert card.attached_to == "holder"
    assert_conserved(initial, attached.after.physical.ledger)

    print("Before-hand Prize destination gate regressions passed")


if __name__ == "__main__":
    main()
