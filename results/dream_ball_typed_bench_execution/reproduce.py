"""Reproduce exact typed Dream Ball search into conserved Bench topology."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_executor import (
    BeforeHandItemResolutionState,
    begin_before_hand_item_play,
    finish_before_hand_item_play,
    resolve_before_hand_item_effect,
)
from before_hand_prize_profiles import build_before_hand_prize_profiles
from board_position_state import BoardPokemon, PokemonCard
from dream_ball_typed_bench_execution import (
    DreamBallBenchTarget,
    dream_ball_target_from_metadata,
    execute_dream_ball_bench_search,
    execute_dream_ball_item_transaction,
)
from identity_materialization import (
    CardInstance,
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from prize_pending_take import PendingPrize, PrizePendingTakeState
from promotion_pending_conservation import PromotionPendingState
from search_zone_transition import SearchZoneTarget
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import (
    ITEM,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def make_resolving_state(profile):
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("active-class", "hand"): 1,
                ("sm2-60", "deck"): 1,
                ("sv3-164", "deck"): 1,
                ("item-target", "deck"): 1,
            }
        ),
        (
            CardInstance("dream-ball", "swsh7-146", "Dream Ball", "prize_pending"),
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
    ledger = put_in_play_instance(
        ledger,
        "active-card",
        "active",
    )
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
        TopPrizePhysicalState(
            ledger,
            "top",
            (),
            (),
        ),
        (PendingPrize("dream-ball", True),),
    )
    resolving = begin_before_hand_item_play(
        prizes,
        profile,
        during_own_turn=True,
    )
    board = board.with_ledger(resolving.physical.ledger)
    return initial, resolving, board


def make_targets(metadata):
    return (
        dream_ball_target_from_metadata(
            metadata["sm2-60"],
            copies=1,
        ),
        dream_ball_target_from_metadata(
            metadata["sv3-164"],
            copies=1,
        ),
        DreamBallBenchTarget(
            SearchZoneTarget(
                "item-target",
                TargetGroup(
                    "Item decoy",
                    1,
                    frozenset({ITEM}),
                ),
            ),
            "Item decoy",
            0,
        ),
    )

def main() -> None:
    profiles = {
        row.card_id: row
        for row in build_before_hand_prize_profiles(ROOT / "resources")
    }
    dream_ball = profiles["swsh7-146"]

    metadata = pokemon_board_metadata_by_id(ROOT / "resources")
    assert metadata["sm2-60"].name == "Tapu Lele-GX"
    assert metadata["sm2-60"].retreat_cost == 1
    assert metadata["sv3-164"].name == "Pidgeot ex"
    assert metadata["sv3-164"].evolves_from == "Pidgeotto"
    assert metadata["sv3-164"].retreat_cost == 0
    assert "swsh7-83" not in metadata

    targets = make_targets(metadata)
    search_targets = tuple(row.search_target for row in targets)
    allocation = enumerate_typed_target_profiles(
        (SearchOutput("Pokemon"),),
        tuple(row.group for row in search_targets),
        (make_demand("pokemon", "Pokemon"),),
    )
    pokemon_actions = tuple(
        action
        for action in allocation.actions
        if action.output == (1,)
    )
    assert len(pokemon_actions) == 2
    assert {action.target_cost for action in pokemon_actions} == {
        (1, 0, 0),
        (0, 1, 0),
    }

    pidgeot_action = next(
        action
        for action in pokemon_actions
        if action.target_cost == (0, 1, 0)
    )

    initial, resolving, board = make_resolving_state(dream_ball)
    transition = execute_dream_ball_bench_search(
        resolving,
        board,
        targets=targets,
        search_action=pidgeot_action,
        pokemon_id="pidgeot-object",
        instance_id="pidgeot-card",
    )

    assert transition.selected_card_class == "sv3-164"
    assert transition.after_board.open_bench_slots == board.open_bench_slots - 1
    assert transition.after_board.ledger.exchangeable.count("sv3-164", "deck") == 0
    assert transition.after_board.ledger.exchangeable.count("sv3-164", "hand") == 0
    pidgeot_instance = transition.after_board.ledger.instance("pidgeot-card")
    assert pidgeot_instance.zone == "in_play"
    assert pidgeot_instance.board_object_id == "pidgeot-object"
    pidgeot = next(
        row
        for row in transition.after_board.pokemon
        if row.pokemon_id == "pidgeot-object"
    )
    assert pidgeot.name == "Pidgeot ex"
    assert pidgeot.stack[0].evolves_from == "Pidgeotto"
    assert not pidgeot.evolution_eligible
    assert (
        transition.after_resolving.physical.ledger.instance("dream-ball").zone
        == "resolving_trainer"
    )

    effect = resolve_before_hand_item_effect(
        transition.after_resolving,
        secondary_effect_resolved=True,
    )
    done = finish_before_hand_item_play(effect)
    final_board = transition.after_board.with_ledger(done.physical.ledger)
    assert final_board.ledger.instance("dream-ball").zone == "discard"
    assert final_board.ledger.instance("pidgeot-card").zone == "in_play"
    assert_conserved(initial, final_board.ledger)

    # The same demand profile has a second exact Pokemon witness. It produces a
    # different materialized board object rather than aliasing the Pidgeot line.
    basic_action = next(
        action
        for action in pokemon_actions
        if action.target_cost == (1, 0, 0)
    )
    initial_basic, resolving_basic, board_basic = make_resolving_state(dream_ball)
    basic_transition = execute_dream_ball_bench_search(
        resolving_basic,
        board_basic,
        targets=targets,
        search_action=basic_action,
        pokemon_id="basic-object",
        instance_id="basic-card",
    )
    assert basic_transition.selected_card_class == "sm2-60"
    assert basic_transition.after_board.ledger.instance("basic-card").zone == "in_play"
    assert basic_transition.after_board.ledger.exchangeable.count("sv3-164", "deck") == 1
    assert_conserved(initial_basic, basic_transition.after_board.ledger)

    # A full Bench makes the direct-to-Bench effect mechanically unavailable.
    full_board = replace(board, bench_capacity=0)
    full_bench_rejected = expect_value_error(
        lambda: execute_dream_ball_bench_search(
            resolving,
            full_board,
            targets=targets,
            search_action=pidgeot_action,
            pokemon_id="blocked-object",
            instance_id="blocked-card",
        )
    )
    assert full_bench_rejected

    # An exact action becomes stale if its selected target left the deck.
    stale_counts = resolving.physical.ledger.exchangeable.move(
        "sv3-164",
        "deck",
        "hand",
    )
    stale_ledger = IdentityLedger(
        stale_counts,
        resolving.physical.ledger.instances,
    )
    stale_physical = TopPrizePhysicalState(
        stale_ledger,
        resolving.physical.top_instance_id,
        resolving.physical.prize_instance_ids,
        resolving.physical.face_up,
    )
    stale_resolving = BeforeHandItemResolutionState(
        stale_physical,
        resolving.remaining_pending,
        resolving.item_instance_id,
        resolving.profile,
    )
    stale_board = board.with_ledger(stale_ledger)
    stale_rejected = expect_value_error(
        lambda: execute_dream_ball_bench_search(
            stale_resolving,
            stale_board,
            targets=targets,
            search_action=pidgeot_action,
            pokemon_id="stale-object",
            instance_id="stale-card",
        )
    )
    assert stale_rejected

    # A target witness created for a different selector cannot be smuggled into
    # Dream Ball merely because its vector dimensions happen to fit.
    item_allocation = enumerate_typed_target_profiles(
        (SearchOutput("Item card"),),
        tuple(row.group for row in search_targets),
        (make_demand("item", "Item card"),),
    )
    item_action = next(
        action
        for action in item_allocation.actions
        if action.target_cost == (0, 0, 1)
    )
    non_pokemon_rejected = expect_value_error(
        lambda: execute_dream_ball_bench_search(
            resolving,
            board,
            targets=targets,
            search_action=item_action,
            pokemon_id="item-object",
            instance_id="item-card",
        )
    )
    assert non_pokemon_rejected

    print(
        json.dumps(
            {
                "collapsed_pokemon_demand_profiles": len(allocation.profiles),
                "distinct_exact_pokemon_witnesses": len(pokemon_actions),
                "pidgeot_direct_to_bench": True,
                "pidgeot_hand_intermediate": False,
                "stage2_stack_depth": len(pidgeot.stack),
                "full_bench_rejected": full_bench_rejected,
                "stale_witness_rejected": stale_rejected,
                "non_pokemon_witness_rejected": non_pokemon_rejected,
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
