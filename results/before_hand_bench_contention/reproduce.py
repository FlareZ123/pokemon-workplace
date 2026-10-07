"""Reproduce one-open-Bench contention between Chansey and Dream Ball."""

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
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from prize_before_hand_bench_entry import use_lucky_bonus
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import resolve_next_pending_prize, stage_prize_takes
from promotion_pending_conservation import PromotionPendingState
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import enumerate_typed_target_profiles, make_demand


def build_state():
    instances = [
        CardInstance("top", "TOP", "Top", "deck_top"),
        CardInstance("chansey", "sv3pt5-113", "Chansey", "prize"),
        CardInstance("dream", "swsh7-146", "Dream Ball", "prize"),
        CardInstance("extra", "EXTRA", "Extra Prize", "prize"),
    ]
    pokemon = []
    for index in range(5):
        instance_id = f"board-card-{index}"
        pokemon_id = "active" if index == 0 else f"bench-{index}"
        instances.append(
            CardInstance(
                instance_id,
                f"BOARD-{index}",
                f"Board Pokemon {index}",
                "in_play",
                board_object_id=pokemon_id,
            )
        )
        pokemon.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(instance_id, f"Board Pokemon {index}"),),
                retreat_cost=1,
            )
        )

    ledger = IdentityLedger(
        ZoneCountState.from_mapping({("sm2-60", "deck"): 1}),
        tuple(sorted(instances, key=lambda row: row.instance_id)),
    )
    board = PromotionPendingState(
        ledger,
        tuple(pokemon),
        active_id="active",
    )
    physical = TopPrizePhysicalState(
        ledger,
        "top",
        ("chansey", "dream", "extra"),
        (False, False, False),
    )
    prizes = stage_prize_takes(physical, positions=(0, 1))
    assert board.open_bench_slots == 1
    assert tuple(row.instance_id for row in prizes.pending) == (
        "chansey",
        "dream",
    )
    return ledger, prizes, board


def dream_ball_action():
    profiles = {
        row.card_id: row
        for row in build_before_hand_prize_profiles(ROOT / "resources")
    }
    metadata = pokemon_board_metadata_by_id(ROOT / "resources")
    target = dream_ball_target_from_metadata(metadata["sm2-60"], copies=1)
    allocation = enumerate_typed_target_profiles(
        (SearchOutput("Pokemon"),),
        (target.search_target.group,),
        (make_demand("pokemon", "Pokemon"),),
    )
    action = next(
        row
        for row in allocation.actions
        if row.output == (1,) and row.target_cost == (1,)
    )
    return profiles["swsh7-146"], (target,), action


def dream_ball_first(profile, targets, action):
    initial, prizes, board = build_state()
    order = PendingPrizeBatchOrder.from_staged(prizes)
    prizes = order.choose_next("dream")

    dream = execute_dream_ball_item_transaction(
        prizes,
        board,
        profile=profile,
        during_own_turn=True,
        targets=targets,
        search_action=action,
        pokemon_id="dream-target",
        instance_id="dream-target-card",
    )
    assert dream.after_board.open_bench_slots == 0

    order = order.advance_after_resolution(
        dream.after_prizes,
        resolved_instance_id="dream",
    )
    assert order is not None
    prizes = order.choose_next("chansey")

    blocked = use_lucky_bonus(
        prizes,
        dream.after_board,
        pokemon_id="chansey-object",
        coin_heads=True,
        during_your_turn=True,
        extra_prize_position=0,
    )
    assert blocked is None

    chansey_to_hand = resolve_next_pending_prize(prizes)
    final_board = dream.after_board.with_ledger(
        chansey_to_hand.after.physical.ledger
    )
    assert final_board.ledger.instance("chansey").zone == "hand"
    assert final_board.ledger.instance("dream-target-card").zone == "in_play"
    assert final_board.ledger.instance("extra").zone == "prize"
    assert final_board.ledger.exchangeable.count("sm2-60", "deck") == 0
    assert_conserved(initial, final_board.ledger)
    return final_board


def chansey_first(profile, targets, action):
    initial, prizes, board = build_state()
    order = PendingPrizeBatchOrder.from_staged(prizes)
    prizes = order.choose_next("chansey")

    chansey = use_lucky_bonus(
        prizes,
        board,
        pokemon_id="chansey-object",
        coin_heads=True,
        during_your_turn=True,
        extra_prize_position=0,
    )
    assert chansey is not None
    assert chansey.extra_prize_staged
    assert chansey.after_board.open_bench_slots == 0
    assert tuple(row.instance_id for row in chansey.after_prizes.pending) == (
        "extra",
        "dream",
    )

    order = order.advance_after_resolution(
        chansey.after_prizes,
        resolved_instance_id="chansey",
    )
    assert order is not None

    try:
        order.choose_next("dream")
    except ValueError:
        pass
    else:
        raise AssertionError("Dream Ball skipped the nested Lucky Bonus Prize")

    extra_to_hand = resolve_next_pending_prize(order.state)
    board = chansey.after_board.with_ledger(
        extra_to_hand.after.physical.ledger
    )
    order = order.rebind(extra_to_hand.after)
    prizes = order.choose_next("dream")

    try:
        execute_dream_ball_item_transaction(
            prizes,
            board,
            profile=profile,
            during_own_turn=True,
            targets=targets,
            search_action=action,
            pokemon_id="dream-target",
            instance_id="dream-target-card",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Dream Ball ignored the full Bench")

    dream_to_hand = resolve_next_pending_prize(prizes)
    final_board = board.with_ledger(dream_to_hand.after.physical.ledger)
    assert final_board.ledger.instance("chansey").zone == "in_play"
    assert final_board.ledger.instance("extra").zone == "hand"
    assert final_board.ledger.instance("dream").zone == "hand"
    assert final_board.ledger.exchangeable.count("sm2-60", "deck") == 1
    assert_conserved(initial, final_board.ledger)
    return final_board


def main() -> None:
    profile, targets, action = dream_ball_action()
    dream_board = dream_ball_first(profile, targets, action)
    chansey_board = chansey_first(profile, targets, action)

    assert {
        row.name for row in dream_board.pokemon
    } - {
        row.name for row in chansey_board.pokemon
    } == {"Tapu Lele-GX"}
    assert {
        row.name for row in chansey_board.pokemon
    } - {
        row.name for row in dream_board.pokemon
    } == {"Chansey"}

    print("one-open-Bench E-31 ordering contention regression passed")
    print("Dream Ball first: Tapu Lele-GX enters play; Chansey goes to hand")
    print("Chansey first on heads: Chansey enters play; extra Prize enters hand; Dream Ball goes to hand")


if __name__ == "__main__":
    main()
