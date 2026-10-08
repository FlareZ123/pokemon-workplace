"""Endogenous Active-position lock changes during Prime -> Guzma.

Run: python -m results.paired_gust_live_lock_execution.reproduce
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from tools.ability_lock_causal_state import initialize_snapshot_lock_state
from tools.board_object_kernel import make_board, make_pokemon
from tools.card_action_metadata import card_action_metadata_by_id
from tools.identity_materialization import CardInstance, IdentityLedger
from tools.multicopy_zone_state import ZoneCountState
from tools.paired_gust_live_lock_execution import execute_live_paired_switch
from tools.paired_switch_order_catalog import PROGRAMS
from tools.source_scoped_restriction_activation import (
    build_restriction_activation_profiles,
)
from tools.turn_action_budget import TurnActionBudget


def boards(extra_vileplume=False, opponent_bench=True):
    actor = make_board(
        make_pokemon("a", "Friendly Active", tags=("team_rocket",)),
        (make_pokemon("b", "Friendly Bench", tags=("team_rocket",)),),
    )
    st = make_pokemon(
        "st", "Stoutland", print_id="bw7-122"
    )
    bench = [
        make_pokemon("ob", "Opponent Bench")
    ] if opponent_bench else []
    if extra_vileplume:
        bench.append(make_pokemon(
            "vi", "Vileplume", print_id="xy7-3"
        ))
    foe = make_board(st, bench)
    return actor, foe


def ledger():
    return IdentityLedger(ZoneCountState(), (
        CardInstance("guzma", "Guzma", "Guzma", "hand"),
        CardInstance("prime", "Prime Catcher", "Prime Catcher", "hand"),
    ))


def main():
    profiles = build_restriction_activation_profiles(ROOT / "resources")
    metadata = card_action_metadata_by_id(ROOT / "resources")
    action_cards = {
        "Prime Catcher": metadata["sv5-157"],
        "Guzma": metadata["sm3-115"],
    }
    own, foe = boards()
    lock = initialize_snapshot_lock_state(own, foe)
    assert lock.resolved

    # Active Stoutland locks Supporters while permitting the first Item gust.
    gu = PROGRAMS["Guzma"]
    denied = execute_live_paired_switch(
        ledger(), own, foe, TurnActionBudget(), lock, gu,
        action_cards["Guzma"],
        profiles=profiles, source_instance_ids=("guzma",),
        own_promote_id="b", opponent_promote_id="ob"
    )
    assert denied is None

    prime = PROGRAMS["Prime Catcher"]
    first = execute_live_paired_switch(
        ledger(), own, foe, TurnActionBudget(), lock, prime,
        action_cards["Prime Catcher"], profiles=profiles,
        source_instance_ids=("prime",),
        own_promote_id="b", opponent_promote_id="ob"
    )
    assert first is not None
    assert any(
        row.card_id == "bw7-122" for row in first.restrictions_before
    )
    assert all(
        row.card_id != "bw7-122" for row in first.restrictions_after
    )
    assert first.transaction.board_resolution.opponent_board.active_id == "ob"
    assert first.transaction.board_resolution.opponent_board.get("st").object_id == "st"
    assert first.transaction.board_resolution.player_board.active_id == "b"
    assert first.transaction.ledger.instance("prime").zone == "discard"
    assert first.transaction.ledger.instance("guzma").zone == "hand"
    assert first.transaction.board_resolution.turn_budget.supporter_plays_used == 0

    # With Sentinel now inactive, a later Supporter from the same hand is
    # playable. Gust Stoutland back Active and use the own self-switch.
    intermediate = first.transaction.board_resolution
    second = execute_live_paired_switch(
        first.transaction.ledger,
        intermediate.player_board,
        intermediate.opponent_board,
        intermediate.turn_budget,
        first.lock_state,
        gu,
        action_cards["Guzma"],
        profiles=profiles, source_instance_ids=("guzma",),
        own_promote_id="a", opponent_promote_id="st"
    )
    assert second is not None
    assert second.transaction.board_resolution.opponent_board.active_id == "st"
    assert second.transaction.board_resolution.player_board.active_id == "a"
    assert second.transaction.board_resolution.turn_budget.supporter_plays_used == 1
    assert second.transaction.ledger.instance("guzma").zone == "discard"
    assert second.transaction.ledger.totals() == ledger().totals()
    assert all(row.card_id != "bw7-122" for row in second.restrictions_before)
    assert any(row.card_id == "bw7-122" for row in second.restrictions_after)

    # The reactivated Sentinel lock denies another Supporter, even if the
    # artificial turn budget were raised to two available Supporters.
    third = execute_live_paired_switch(
        second.transaction.ledger,
        second.transaction.board_resolution.player_board,
        second.transaction.board_resolution.opponent_board,
        TurnActionBudget(supporter_play_limit=2, supporter_plays_used=1),
        second.lock_state,
        gu,
        action_cards["Guzma"],
        profiles=profiles, source_instance_ids=("guzma",),
        own_promote_id="b", opponent_promote_id="ob"
    )
    assert third is None

    # With passive Vileplume Item lock on the opposing Bench, Stoutland
    # Supporter lock and Vileplume Item lock jointly close this line.
    own2, foe2 = boards(extra_vileplume=True)
    lock2 = initialize_snapshot_lock_state(own2, foe2)
    assert lock2.resolved
    item_denied = execute_live_paired_switch(
        ledger(), own2, foe2, TurnActionBudget(), lock2,
        prime, action_cards["Prime Catcher"],
        profiles=profiles, source_instance_ids=("prime",),
        own_promote_id="b", opponent_promote_id="ob"
    )
    assert item_denied is None
    supporter_denied = execute_live_paired_switch(
        ledger(), own2, foe2, TurnActionBudget(), lock2,
        gu, action_cards["Guzma"], profiles=profiles,
        source_instance_ids=("guzma",),
        own_promote_id="b", opponent_promote_id="ob"
    )
    assert supporter_denied is None

    # With no opposing Bench, neither Prime nor Guzma can gust the Active
    # Stoutland out of position. Source lock remains in effect.
    own3, foe3 = boards(opponent_bench=False)
    lock3 = initialize_snapshot_lock_state(own3, foe3)
    assert execute_live_paired_switch(
        ledger(), own3, foe3, TurnActionBudget(), lock3,
        prime, action_cards["Prime Catcher"],
        profiles=profiles, source_instance_ids=("prime",),
        own_promote_id="b", opponent_promote_id=None
    ) is None

    print("PASS: live Stoutland source Active -> Bench -> Active, "
          "with reversible Supporter permission and physical source conservation")
    print("PASS: Vileplume Bench Item lock jointly closes Prime/Guzma line")
    print("PASS: no opposing Bench makes lock-source gust unavailable")


if __name__ == "__main__":
    main()
