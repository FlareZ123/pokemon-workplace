"""Execute Secret Box -> Guzma & Hala with exact generated discard fodder."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_search_transaction,
)
from typed_search_target_allocator import (
    ITEM,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
    SUPPORTER,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    secret_box = representative(profiles, "Secret Box")
    guzma_hala = representative(profiles, "Guzma & Hala")

    secret_targets = (
        SearchZoneTarget(
            "sb_item",
            TargetGroup("Secret Box Item", 1, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            "sb_tool",
            TargetGroup("Secret Box Tool", 1, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            "guzma_hala",
            TargetGroup("Secret Box Supporter", 1, frozenset({SUPPORTER})),
        ),
        SearchZoneTarget(
            "sb_stadium",
            TargetGroup("Secret Box Stadium", 1, frozenset({STADIUM})),
        ),
    )
    secret_demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("supporter", "Supporter card"),
        make_demand("stadium", "Stadium card"),
    )
    secret_allocation = enumerate_typed_target_profiles(
        secret_box.base_outputs,
        tuple(target.group for target in secret_targets),
        secret_demands,
    )
    secret_action = next(
        action
        for action in secret_allocation.actions
        if action.output == (1, 1, 1, 1)
    )

    initial = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("secret_box", "hand"): 1,
                ("pre_box_fodder_a", "hand"): 1,
                ("pre_box_fodder_b", "hand"): 1,
                ("pre_box_fodder_c", "hand"): 1,
                ("sb_item", "deck"): 1,
                ("sb_tool", "deck"): 1,
                ("guzma_hala", "deck"): 1,
                ("sb_stadium", "deck"): 1,
                ("gh_stadium", "deck"): 1,
                ("gh_tool", "deck"): 1,
                ("gh_special", "deck"): 1,
            }
        )
    )
    pre_box_candidates = (
        DiscardCandidate("pre_box_fodder_a"),
        DiscardCandidate("pre_box_fodder_b"),
        DiscardCandidate("pre_box_fodder_c"),
    )
    pre_box_selections = enumerate_discard_selections(
        initial.zones,
        pre_box_candidates,
        3,
    )
    assert len(pre_box_selections) == 1

    box_tx = execute_trainer_search_transaction(
        initial,
        profile=secret_box,
        action_card_class="secret_box",
        demands=secret_demands,
        targets=secret_targets,
        search_action=secret_action,
        discard_candidates=pre_box_candidates,
        discard_selection=pre_box_selections[0],
    )
    assert box_tx.discard_cost == 3
    assert not box_tx.after.budget.supporter_used
    for card_class in ("sb_item", "sb_tool", "guzma_hala", "sb_stadium"):
        assert box_tx.after.zones.count(card_class, "hand") == 1
    for card_class in (
        "pre_box_fodder_a",
        "pre_box_fodder_b",
        "pre_box_fodder_c",
    ):
        assert box_tx.after.zones.count(card_class, "discard") == 1
        assert box_tx.after.zones.count(card_class, "hand") == 0

    gh_targets = (
        SearchZoneTarget(
            "gh_stadium",
            TargetGroup("G&H Stadium", 1, frozenset({STADIUM})),
        ),
        SearchZoneTarget(
            "gh_tool",
            TargetGroup("G&H Tool", 1, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            "gh_special",
            TargetGroup("G&H Special Energy", 1, frozenset({SPECIAL_ENERGY})),
        ),
    )
    gh_demands = (
        make_demand("stadium", "Stadium card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("special", "Special Energy card"),
    )
    gh_allocation = enumerate_typed_target_profiles(
        guzma_hala.base_outputs + guzma_hala.conditional_outputs,
        tuple(target.group for target in gh_targets),
        gh_demands,
    )
    gh_action = next(
        action
        for action in gh_allocation.actions
        if action.output == (1, 1, 1)
    )

    # The only G&H payment cards are outputs created by Secret Box.
    # The Tool output is protected as a retained payload.
    generated_candidates = (
        DiscardCandidate("sb_item"),
        DiscardCandidate("sb_tool", max_copies=0),
        DiscardCandidate("sb_stadium"),
    )
    generated_selections = enumerate_discard_selections(
        box_tx.after.zones,
        generated_candidates,
        2,
    )
    assert len(generated_selections) == 1

    gh_tx = execute_trainer_search_transaction(
        box_tx.after,
        profile=guzma_hala,
        action_card_class="guzma_hala",
        demands=gh_demands,
        targets=gh_targets,
        search_action=gh_action,
        discard_candidates=generated_candidates,
        discard_selection=generated_selections[0],
    )

    assert gh_tx.discard_cost == 2
    assert gh_tx.used_conditional_outputs
    assert gh_tx.after.budget.supporter_used
    assert gh_tx.after.zones.count("sb_item", "discard") == 1
    assert gh_tx.after.zones.count("sb_stadium", "discard") == 1
    assert gh_tx.after.zones.count("sb_tool", "hand") == 1
    assert gh_tx.after.zones.count("guzma_hala", "discard") == 1
    for card_class in ("gh_stadium", "gh_tool", "gh_special"):
        assert gh_tx.after.zones.count(card_class, "hand") == 1

    # The sequence consumed exactly three cards that existed as discard fodder
    # before Secret Box. The later cost was paid from generated card classes.
    assert sum(
        initial.zones.count(card_class, "hand")
        for card_class in (
            "pre_box_fodder_a",
            "pre_box_fodder_b",
            "pre_box_fodder_c",
        )
    ) == 3

    classes = {
        card_class
        for card_class, _zone, _count in initial.zones.counts
    } | {
        card_class
        for card_class, _zone, _count in gh_tx.after.zones.counts
    }
    for card_class in classes:
        assert initial.zones.total(card_class) == gh_tx.after.zones.total(card_class)

    print("initial_pre_box_fodder=3")
    print("secret_box_discard=3")
    print("guzma_hala_discard=2")
    print("downstream_payment=sb_item + sb_stadium")
    print("retained_generated_payload=sb_tool")
    print("supporter_budget_consumed_after_box=False")
    print("supporter_budget_consumed_after_guzma_hala=True")
    print("card_class_totals_conserved=True")
    print("All sequential Trainer replenishment checks passed.")


if __name__ == "__main__":
    main()
