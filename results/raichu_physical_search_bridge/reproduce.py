"""Validate Harto search-to-Crobat witnesses through canonical Trainer transactions."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from single_output_search_profile_compiler import (
    compile_single_output_revealed_search_profiles,
)
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_search_transaction,
)
from typed_search_target_allocator import (
    BASIC_POKEMON,
    STAGE_1_POKEMON,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


def representative(profiles, name: str):
    return next(profile for profile in profiles if profile.name == name)


def hand_size(zones: ZoneCountState) -> int:
    return sum(
        count
        for _card_class, zone, count in zones.counts
        if zone == "hand"
    )


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    profiles = compile_single_output_revealed_search_profiles(ROOT / "resources")
    quick_ball = representative(profiles, "Quick Ball")
    ultra_ball = representative(profiles, "Ultra Ball")

    targets = (
        SearchZoneTarget(
            "crobat_v",
            TargetGroup("Crobat V", 1, frozenset({BASIC_POKEMON})),
        ),
        SearchZoneTarget(
            "alolan_raichu",
            TargetGroup("Alolan Raichu", 1, frozenset({STAGE_1_POKEMON})),
        ),
    )
    pokemon_demand = (make_demand("pokemon", "Pokémon"),)

    quick_allocation = enumerate_typed_target_profiles(
        quick_ball.base_outputs,
        tuple(target.group for target in targets),
        pokemon_demand,
    )
    quick_crobat = next(
        action
        for action in quick_allocation.actions
        if action.target_cost == (1, 0)
    )
    assert all(
        action.target_cost != (0, 1)
        for action in quick_allocation.actions
    )

    quick_state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("quick_ball", "hand"): 1,
                ("quick_fodder", "hand"): 1,
                ("forest_seal", "hand"): 1,
                ("quick_other", "hand"): 4,
                ("crobat_v", "deck"): 1,
                ("alolan_raichu", "deck"): 1,
            }
        )
    )
    quick_candidates = (DiscardCandidate("quick_fodder"),)
    quick_selection = enumerate_discard_selections(
        quick_state.zones,
        quick_candidates,
        1,
    )[0]
    quick_tx = execute_trainer_search_transaction(
        quick_state,
        profile=quick_ball,
        action_card_class="quick_ball",
        demands=pokemon_demand,
        targets=targets,
        search_action=quick_crobat,
        discard_candidates=quick_candidates,
        discard_selection=quick_selection,
        play_condition_met=True,
    )
    assert quick_tx.discard_cost == 1
    assert quick_tx.after.zones.count("quick_ball", "discard") == 1
    assert quick_tx.after.zones.count("quick_fodder", "discard") == 1
    assert quick_tx.after.zones.count("crobat_v", "hand") == 1
    assert quick_tx.after.zones.count("alolan_raichu", "deck") == 1
    assert hand_size(quick_tx.after.zones) == 6

    quick_after_bench = quick_tx.after.zones.move(
        "crobat_v",
        "hand",
        "bench",
    )
    assert hand_size(quick_after_bench) == 5
    quick_dark_asset_draws = 6 - hand_size(quick_after_bench)
    assert quick_dark_asset_draws == 1

    ultra_allocation = enumerate_typed_target_profiles(
        ultra_ball.base_outputs,
        tuple(target.group for target in targets),
        pokemon_demand,
    )
    ultra_crobat = next(
        action
        for action in ultra_allocation.actions
        if action.target_cost == (1, 0)
    )
    ultra_raichu = next(
        action
        for action in ultra_allocation.actions
        if action.target_cost == (0, 1)
    )

    ultra_state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("ultra_ball", "hand"): 1,
                ("ultra_fodder_a", "hand"): 1,
                ("ultra_fodder_b", "hand"): 1,
                ("forest_seal", "hand"): 1,
                ("ultra_other", "hand"): 3,
                ("crobat_v", "deck"): 1,
                ("alolan_raichu", "prize"): 1,
                ("gladion", "deck"): 1,
            }
        )
    )
    ultra_candidates = (
        DiscardCandidate("ultra_fodder_a"),
        DiscardCandidate("ultra_fodder_b"),
    )
    ultra_selection = enumerate_discard_selections(
        ultra_state.zones,
        ultra_candidates,
        2,
    )[0]

    direct_prized_target_rejected = expect_value_error(
        lambda: execute_trainer_search_transaction(
            ultra_state,
            profile=ultra_ball,
            action_card_class="ultra_ball",
            demands=pokemon_demand,
            targets=targets,
            search_action=ultra_raichu,
            discard_candidates=ultra_candidates,
            discard_selection=ultra_selection,
            play_condition_met=True,
        )
    )
    assert direct_prized_target_rejected

    ultra_tx = execute_trainer_search_transaction(
        ultra_state,
        profile=ultra_ball,
        action_card_class="ultra_ball",
        demands=pokemon_demand,
        targets=targets,
        search_action=ultra_crobat,
        discard_candidates=ultra_candidates,
        discard_selection=ultra_selection,
        play_condition_met=True,
    )
    assert ultra_tx.discard_cost == 2
    assert ultra_tx.after.zones.count("ultra_ball", "discard") == 1
    assert ultra_tx.after.zones.count("ultra_fodder_a", "discard") == 1
    assert ultra_tx.after.zones.count("ultra_fodder_b", "discard") == 1
    assert ultra_tx.after.zones.count("crobat_v", "hand") == 1
    assert ultra_tx.after.zones.count("alolan_raichu", "prize") == 1
    assert ultra_tx.after.zones.count("forest_seal", "hand") == 1
    assert hand_size(ultra_tx.after.zones) == 5

    ultra_after_bench = ultra_tx.after.zones.move(
        "crobat_v",
        "hand",
        "bench",
    )
    assert hand_size(ultra_after_bench) == 4
    ultra_dark_asset_draws = 6 - hand_size(ultra_after_bench)
    assert ultra_dark_asset_draws == 2

    for state, after in (
        (quick_state.zones, quick_after_bench),
        (ultra_state.zones, ultra_after_bench),
    ):
        classes = {
            card_class
            for card_class, _zone, _count in state.counts
        } | {
            card_class
            for card_class, _zone, _count in after.counts
        }
        for card_class in classes:
            assert state.total(card_class) == after.total(card_class)

    print("Harto physical search-to-Crobat bridge: PASS")
    print("Quick Ball cannot search Stage 1 Alolan Raichu: PASS")
    print("Quick Ball exact discard cost:", quick_tx.discard_cost)
    print("Quick Ball post-Bench hand size:", hand_size(quick_after_bench))
    print("Quick Ball Dark Asset draw count:", quick_dark_asset_draws)
    print("Ultra Ball direct Prized-target move rejected:", direct_prized_target_rejected)
    print("Ultra Ball Crobat pivot exact discard cost:", ultra_tx.discard_cost)
    print("Ultra Ball post-Bench hand size:", hand_size(ultra_after_bench))
    print("Ultra Ball Dark Asset draw count:", ultra_dark_asset_draws)
    print("Per-card-class totals conserved: PASS")


if __name__ == "__main__":
    main()
