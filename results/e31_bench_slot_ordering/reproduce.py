"""Reproduce owner-selected E-31 Bench-slot contention between Chansey and Dream Ball."""

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
    execute_dream_ball_item_no_target_transaction,
    execute_dream_ball_item_transaction,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from prize_before_hand_bench_entry import use_lucky_bonus
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import resolve_next_pending_prize, stage_prize_takes
from promotion_pending_conservation import PromotionPendingState
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import (
    enumerate_typed_target_profiles,
    make_demand,
)


def make_state():
    counts = {
        ("active-class", "hand"): 1,
        ("bench-0-class", "hand"): 1,
        ("bench-1-class", "hand"): 1,
        ("bench-2-class", "hand"): 1,
        ("bench-3-class", "hand"): 1,
        ("xy7-3", "deck"): 1,
        ("top-class", "deck_top"): 1,
        ("sv3pt5-113", "prize"): 1,
        ("swsh7-146", "prize"): 1,
    }
    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = initial

    ledger = materialize(
        ledger,
        card_class="active-class",
        card_name="Active Pokemon",
        source_zone="hand",
        instance_id="active-card",
    )
    ledger = put_in_play_instance(ledger, "active-card", "active")

    pokemon = [
        BoardPokemon(
            "active",
            (PokemonCard("active-card", "Active Pokemon"),),
            retreat_cost=1,
        )
    ]
    for index in range(4):
        card_id = f"bench-{index}-card"
        pokemon_id = f"bench-{index}"
        ledger = materialize(
            ledger,
            card_class=f"bench-{index}-class",
            card_name=f"Bench {index}",
            source_zone="hand",
            instance_id=card_id,
        )
        ledger = put_in_play_instance(ledger, card_id, pokemon_id)
        pokemon.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(card_id, f"Bench {index}"),),
                retreat_cost=1,
            )
        )

    ledger = materialize(
        ledger,
        card_class="top-class",
        card_name="Top Card",
        source_zone="deck_top",
        instance_id="top-card",
    )
    ledger = materialize(
        ledger,
        card_class="sv3pt5-113",
        card_name="Chansey",
        source_zone="prize",
        instance_id="chansey",
    )
    ledger = materialize(
        ledger,
        card_class="swsh7-146",
        card_name="Dream Ball",
        source_zone="prize",
        instance_id="dream",
    )

    board = PromotionPendingState(
        ledger,
        tuple(pokemon),
        active_id="active",
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top-card",
        ("chansey", "dream"),
        (False, False),
    )
    staged = stage_prize_takes(physical, positions=(0, 1))
    board = board.with_ledger(staged.physical.ledger)
    assert board.open_bench_slots == 1
    return initial, staged, board


def make_dream_action():
    metadata = pokemon_board_metadata_by_id(ROOT / "resources")
    target = dream_ball_target_from_metadata(
        metadata["xy7-3"],
        copies=1,
    )
    allocation = enumerate_typed_target_profiles(
        (SearchOutput("Pokemon"),),
        (target.search_target.group,),
        (make_demand("pokemon", "Pokemon"),),
    )
    action = next(
        row
        for row in allocation.actions
        if row.target_cost == (1,)
    )
    return target, action


def main() -> None:
    profiles = {
        row.card_id: row
        for row in build_before_hand_prize_profiles(ROOT / "resources")
    }
    dream_profile = profiles["swsh7-146"]
    dream_target, dream_action = make_dream_action()

    # Branch A: Chansey gets the one open Bench slot.
    initial_a, staged_a, board_a = make_state()
    order_a = PendingPrizeBatchOrder.from_staged(staged_a)
    chansey_first = order_a.choose_next("chansey")
    lucky = use_lucky_bonus(
        chansey_first,
        board_a,
        pokemon_id="chansey-object",
        coin_heads=False,
        during_your_turn=True,
    )
    assert lucky is not None
    assert lucky.after_board.open_bench_slots == 0

    order_a = order_a.advance_after_resolution(
        lucky.after_prizes,
        resolved_instance_id="chansey",
    )
    assert order_a is not None
    dream_next = order_a.choose_next("dream")

    dream_blocked_by_full_bench = False
    try:
        execute_dream_ball_item_transaction(
            dream_next,
            lucky.after_board,
            profile=dream_profile,
            during_own_turn=True,
            targets=(dream_target,),
            search_action=dream_action,
            pokemon_id="vileplume-object",
            instance_id="vileplume-card",
        )
    except ValueError:
        dream_blocked_by_full_bench = True
    assert dream_blocked_by_full_bench

    dream_declined = resolve_next_pending_prize(dream_next).after
    final_board_a = lucky.after_board.with_ledger(
        dream_declined.physical.ledger
    )
    assert final_board_a.ledger.instance("chansey").zone == "in_play"
    assert final_board_a.ledger.instance("dream").zone == "hand"
    assert final_board_a.ledger.exchangeable.count("xy7-3", "deck") == 1
    assert_conserved(initial_a, final_board_a.ledger)

    # Branch B: Dream Ball gets the one open Bench slot.
    initial_b, staged_b, board_b = make_state()
    order_b = PendingPrizeBatchOrder.from_staged(staged_b)
    dream_first = order_b.choose_next("dream")
    dream_used = execute_dream_ball_item_transaction(
        dream_first,
        board_b,
        profile=dream_profile,
        during_own_turn=True,
        targets=(dream_target,),
        search_action=dream_action,
        pokemon_id="vileplume-object",
        instance_id="vileplume-card",
    )
    assert dream_used.after_board.open_bench_slots == 0

    order_b = order_b.advance_after_resolution(
        dream_used.after_prizes,
        resolved_instance_id="dream",
    )
    assert order_b is not None
    chansey_next = order_b.choose_next("chansey")
    lucky_blocked = use_lucky_bonus(
        chansey_next,
        dream_used.after_board,
        pokemon_id="chansey-object",
        coin_heads=False,
        during_your_turn=True,
    )
    assert lucky_blocked is None

    chansey_declined = resolve_next_pending_prize(chansey_next).after
    final_board_b = dream_used.after_board.with_ledger(
        chansey_declined.physical.ledger
    )
    assert final_board_b.ledger.instance("dream").zone == "discard"
    assert final_board_b.ledger.instance("vileplume-card").zone == "in_play"
    assert final_board_b.ledger.instance("chansey").zone == "hand"
    assert final_board_b.ledger.exchangeable.count("xy7-3", "deck") == 0
    assert_conserved(initial_b, final_board_b.ledger)

    # Branch C: Dream Ball is processed first, but its typed deck search
    # deliberately selects no Pokemon. The Item resolves and discards without
    # consuming the open slot, so Chansey can still use Lucky Bonus afterward.
    initial_c, staged_c, board_c = make_state()
    order_c = PendingPrizeBatchOrder.from_staged(staged_c)
    dream_first_none = order_c.choose_next("dream")
    dream_no_target = execute_dream_ball_item_no_target_transaction(
        dream_first_none,
        board_c,
        profile=dream_profile,
        during_own_turn=True,
    )
    assert dream_no_target.after_board.open_bench_slots == 1
    assert dream_no_target.after_board.ledger.instance("dream").zone == "discard"
    assert dream_no_target.after_board.ledger.exchangeable.count("xy7-3", "deck") == 1

    order_c = order_c.advance_after_resolution(
        dream_no_target.after_prizes,
        resolved_instance_id="dream",
    )
    assert order_c is not None
    chansey_after_none = order_c.choose_next("chansey")
    lucky_after_none = use_lucky_bonus(
        chansey_after_none,
        dream_no_target.after_board,
        pokemon_id="chansey-object",
        coin_heads=False,
        during_your_turn=True,
    )
    assert lucky_after_none is not None
    final_board_c = lucky_after_none.after_board
    assert final_board_c.open_bench_slots == 0
    assert final_board_c.ledger.instance("chansey").zone == "in_play"
    assert final_board_c.ledger.instance("dream").zone == "discard"
    assert final_board_c.ledger.exchangeable.count("xy7-3", "deck") == 1
    assert_conserved(initial_c, final_board_c.ledger)

    names_a = {row.name for row in final_board_a.pokemon}
    names_b = {row.name for row in final_board_b.pokemon}
    names_c = {row.name for row in final_board_c.pokemon}
    assert "Chansey" in names_a and "Vileplume" not in names_a
    assert "Vileplume" in names_b and "Chansey" not in names_b
    assert "Chansey" in names_c and "Vileplume" not in names_c

    print(
        json.dumps(
            {
                "starting_open_bench_slots": 1,
                "owner_can_choose_same_award_order_after_reveal": True,
                "chansey_first": {
                    "chansey_enters_play": True,
                    "dream_ball_effect_usable": False,
                    "dream_ball_destination": "hand",
                    "vileplume_remains_in_deck": True,
                },
                "dream_ball_first_take_target": {
                    "vileplume_enters_play": True,
                    "chansey_lucky_bonus_usable": False,
                    "chansey_destination": "hand",
                },
                "dream_ball_first_select_none": {
                    "dream_ball_destination": "discard",
                    "vileplume_remains_in_deck": True,
                    "chansey_lucky_bonus_usable": True,
                    "chansey_enters_play": True,
                },
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
