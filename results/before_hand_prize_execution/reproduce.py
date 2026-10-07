"""Reproduce direct and Item Prize-origin E-31 execution."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_executor import (
    begin_before_hand_item_play,
    finish_before_hand_item_play,
    resolve_direct_before_hand_trigger,
)
from before_hand_prize_profiles import build_before_hand_prize_profiles
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from item_play_source_scope import build_item_play_restrictions
from multicopy_zone_state import ZoneCountState
from prize_pending_take import PendingPrize, PrizePendingTakeState
from top_prize_physical_bridge import TopPrizePhysicalState

RESOURCES = ROOT / "resources"


def make_state(card_id: str, *, was_face_down: bool = True):
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("pending", card_id, card_id, "prize_pending"),
            CardInstance("top", "TOP", "Top", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top",
        (),
        (),
    )
    return PrizePendingTakeState(
        physical,
        (PendingPrize("pending", was_face_down),),
    )


def main() -> None:
    profiles = {
        row.card_id: row
        for row in build_before_hand_prize_profiles(RESOURCES)
    }

    jirachi_state = make_state("sm7-97")
    jirachi = resolve_direct_before_hand_trigger(
        jirachi_state,
        profiles["sm7-97"],
        use_trigger=True,
        during_own_turn=True,
        bench_open=True,
        board_object_id="bench-jirachi",
    )
    assert jirachi.additional_prize_awards == 1
    assert jirachi.after.pending == ()
    assert (
        jirachi.after.physical.ledger.instance("pending").zone
        == "in_play"
    )
    assert_conserved(
        jirachi_state.physical.ledger,
        jirachi.after.physical.ledger,
    )

    declined = resolve_direct_before_hand_trigger(
        make_state("sm7-97"),
        profiles["sm7-97"],
        use_trigger=False,
        during_own_turn=True,
    )
    assert declined.additional_prize_awards == 0
    assert declined.after.physical.ledger.instance("pending").zone == "hand"

    chansey_heads = resolve_direct_before_hand_trigger(
        make_state("sv3pt5-113"),
        profiles["sv3pt5-113"],
        use_trigger=True,
        during_own_turn=True,
        bench_open=True,
        board_object_id="bench-chansey",
        coin_heads=True,
    )
    assert chansey_heads.additional_prize_awards == 1

    chansey_tails = resolve_direct_before_hand_trigger(
        make_state("sv3pt5-113"),
        profiles["sv3pt5-113"],
        use_trigger=True,
        during_own_turn=True,
        bench_open=True,
        board_object_id="bench-chansey",
        coin_heads=False,
    )
    assert chansey_tails.additional_prize_awards == 0

    treasure_state = make_state("swsh7-165")
    treasure = resolve_direct_before_hand_trigger(
        treasure_state,
        profiles["swsh7-165"],
        use_trigger=True,
        during_own_turn=True,
        attached_to="holder-1",
    )
    energy = treasure.after.physical.ledger.instance("pending")
    assert energy.zone == "attached"
    assert energy.attached_to == "holder-1"
    assert treasure.additional_prize_awards == 0

    try:
        resolve_direct_before_hand_trigger(
            make_state("sm7-97"),
            profiles["sm7-97"],
            use_trigger=True,
            during_own_turn=False,
            bench_open=True,
            board_object_id="bench-jirachi",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("ignored explicit during-your-turn condition")

    try:
        resolve_direct_before_hand_trigger(
            make_state("sm7-97", was_face_down=False),
            profiles["sm7-97"],
            use_trigger=True,
            during_own_turn=True,
            bench_open=True,
            board_object_id="bench-jirachi",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("allowed trigger after a face-up Prize take")

    restrictions = build_item_play_restrictions(RESOURCES)

    dream_state = make_state("swsh7-146")
    dream_resolving = begin_before_hand_item_play(
        dream_state,
        profiles["swsh7-146"],
        during_own_turn=True,
        active_item_restrictions=restrictions,
    )
    assert (
        dream_resolving.physical.ledger.instance("pending").zone
        == "resolving_trainer"
    )
    assert dream_resolving.remaining_pending == ()

    try:
        finish_before_hand_item_play(dream_resolving)
    except ValueError:
        pass
    else:
        raise AssertionError("Dream Ball finished before its search resolved")

    dream_done = finish_before_hand_item_play(
        dream_resolving,
        secondary_effect_resolved=True,
    )
    assert dream_done.additional_prize_awards == 0
    assert dream_done.after.physical.ledger.instance("pending").zone == "discard"
    assert_conserved(
        dream_state.physical.ledger,
        dream_done.after.physical.ledger,
    )

    greedy_state = make_state("xy11-102")
    greedy_resolving = begin_before_hand_item_play(
        greedy_state,
        profiles["xy11-102"],
        during_own_turn=True,
        active_item_restrictions=restrictions,
    )
    greedy_done = finish_before_hand_item_play(
        greedy_resolving,
        coin_heads=True,
    )
    assert greedy_done.additional_prize_awards == 1
    assert greedy_done.after.physical.ledger.instance("pending").zone == "discard"

    print("Prize-origin E-31 execution regressions passed")


if __name__ == "__main__":
    main()
