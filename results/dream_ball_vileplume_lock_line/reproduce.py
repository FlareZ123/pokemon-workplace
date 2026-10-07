"""Reproduce Dream Ball -> Vileplume Item-lock source-scope line."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_profiles import build_before_hand_prize_profiles
from board_position_state import BoardPokemon, PokemonCard
from dream_ball_typed_bench_execution import (
    dream_ball_target_from_metadata,
    execute_dream_ball_item_transaction,
)
from identity_materialization import (
    CardInstance,
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from item_play_source_scope import (
    build_item_play_restrictions,
    restriction_blocks_source,
)
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from prize_pending_take import PendingPrize, PrizePendingTakeState
from promotion_pending_conservation import PromotionPendingState
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import (
    enumerate_typed_target_profiles,
    make_demand,
)


def make_state():
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("active-class", "hand"): 1,
                ("xy7-3", "deck"): 1,
                ("sv3-164", "deck"): 1,
            }
        ),
        (
            CardInstance("dream-a", "swsh7-146", "Dream Ball", "prize_pending"),
            CardInstance("dream-b", "swsh7-146", "Dream Ball", "prize_pending"),
            CardInstance("top", "top-class", "Top Card", "deck_top"),
        ),
    )
    ledger = materialize(
        initial,
        card_class="active-class",
        card_name="Active Pokemon",
        source_zone="hand",
        instance_id="active-card",
    )
    ledger = put_in_play_instance(ledger, "active-card", "active")

    board = PromotionPendingState(
        ledger,
        (
            BoardPokemon(
                "active",
                (PokemonCard("active-card", "Active Pokemon"),),
                retreat_cost=1,
            ),
        ),
        active_id="active",
    )
    prizes = PrizePendingTakeState(
        TopPrizePhysicalState(ledger, "top", (), ()),
        (
            PendingPrize("dream-a", True),
            PendingPrize("dream-b", True),
        ),
    )
    return initial, prizes, board


def main() -> None:
    profile_by_id = {
        row.card_id: row
        for row in build_before_hand_prize_profiles(ROOT / "resources")
    }
    dream_ball = profile_by_id["swsh7-146"]

    metadata = pokemon_board_metadata_by_id(ROOT / "resources")
    vileplume_target = dream_ball_target_from_metadata(
        metadata["xy7-3"],
        copies=1,
    )
    pidgeot_target = dream_ball_target_from_metadata(
        metadata["sv3-164"],
        copies=1,
    )
    targets = (vileplume_target, pidgeot_target)

    allocation = enumerate_typed_target_profiles(
        (SearchOutput("Pokemon"),),
        tuple(row.search_target.group for row in targets),
        (make_demand("pokemon", "Pokemon"),),
    )
    vileplume_action = next(
        action
        for action in allocation.actions
        if action.target_cost == (1, 0)
    )
    pidgeot_action = next(
        action
        for action in allocation.actions
        if action.target_cost == (0, 1)
    )

    restrictions = build_item_play_restrictions(ROOT / "resources")
    vileplume_locks = tuple(
        row
        for row in restrictions
        if row.card_id == "xy7-3" and "Irritating Pollen" in row.source
    )
    assert len(vileplume_locks) == 1
    vileplume_lock = vileplume_locks[0]
    assert restriction_blocks_source(vileplume_lock, "hand")
    assert not restriction_blocks_source(vileplume_lock, "prize_pending")

    initial, prizes, board = make_state()

    first = execute_dream_ball_item_transaction(
        prizes,
        board,
        profile=dream_ball,
        during_own_turn=True,
        targets=targets,
        search_action=vileplume_action,
        pokemon_id="vileplume-object",
        instance_id="vileplume-card",
    )
    assert first.after_board.ledger.instance("vileplume-card").zone == "in_play"
    assert first.after_board.ledger.instance("dream-a").zone == "discard"
    assert first.after_board.ledger.instance("dream-b").zone == "prize_pending"
    assert tuple(row.instance_id for row in first.after_prizes.pending) == ("dream-b",)

    # Irritating Pollen is now active, but it prohibits Item play from hand.
    # The second Dream Ball is still in the E-31 Prize source, so it can begin.
    second = execute_dream_ball_item_transaction(
        first.after_prizes,
        first.after_board,
        profile=dream_ball,
        during_own_turn=True,
        targets=targets,
        search_action=pidgeot_action,
        pokemon_id="pidgeot-object",
        instance_id="pidgeot-card",
        active_item_restrictions=(vileplume_lock,),
    )

    assert second.after_prizes.pending == ()
    assert second.after_board.ledger.instance("dream-b").zone == "discard"
    assert second.after_board.ledger.instance("pidgeot-card").zone == "in_play"
    assert second.after_board.ledger.exchangeable.count("xy7-3", "deck") == 0
    assert second.after_board.ledger.exchangeable.count("sv3-164", "deck") == 0
    assert second.after_board.ledger.exchangeable.count("xy7-3", "hand") == 0
    assert second.after_board.ledger.exchangeable.count("sv3-164", "hand") == 0
    assert_conserved(initial, second.after_board.ledger)

    names = {row.name for row in second.after_board.pokemon}
    assert "Vileplume" in names
    assert "Pidgeot ex" in names

    print(
        json.dumps(
            {
                "first_dream_ball_target": "Vileplume xy7-3",
                "second_dream_ball_target": "Pidgeot ex sv3-164",
                "vileplume_blocks_hand_items": True,
                "vileplume_blocks_prize_pending_items": False,
                "second_dream_ball_resolved_under_vileplume": True,
                "both_targets_skipped_hand": True,
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
