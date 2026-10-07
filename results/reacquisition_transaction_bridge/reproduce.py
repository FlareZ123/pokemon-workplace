"""Validate temporal-ledger reacquisition with conserved Trainer transactions."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from temporal_resource_ledger import TemporalAction, minimum_initial_filler
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
    execute_trainer_search_transaction,
)
from typed_search_retrieval import enumerate_typed_retrieval_actions
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
    ledger_box = TemporalAction(
        "Secret Box",
        consumes=("Secret Box",),
        discard_cost=3,
        generates=(
            "Guzma & Hala",
            "Tag Call",
            "Technical Machine: Evolution",
            "Artazon",
        ),
    )
    ledger_gnh = TemporalAction(
        "Guzma & Hala",
        consumes=("Guzma & Hala",),
        discard_cost=2,
        generates=("Technical Machine: Evolution", "Jet Energy"),
    )
    fillers, ledger_witness = minimum_initial_filler(
        ("Secret Box",),
        (ledger_box, ledger_gnh),
        final_hand_requirements={
            "Technical Machine: Evolution": 1,
            "Artazon": 1,
            "Jet Energy": 1,
        },
        max_fillers=3,
    )
    assert fillers == 3
    assert ledger_witness.initial_discards == 3
    assert ledger_witness.total_discards == 5
    second_discards = {
        card_class
        for card_class, _origin, count in ledger_witness.actions[1].discarded
        for _ in range(count)
    }
    assert second_discards == {"Tag Call", "Technical Machine: Evolution"}

    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    secret_box = representative(profiles, "Secret Box")
    guzma_hala = representative(profiles, "Guzma & Hala")

    secret_targets = (
        SearchZoneTarget(
            "tag_call",
            TargetGroup("Tag Call", 1, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            "tm_evolution",
            TargetGroup("TM Evolution", 2, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            "guzma_hala",
            TargetGroup("Guzma & Hala", 1, frozenset({SUPPORTER})),
        ),
        SearchZoneTarget(
            "artazon",
            TargetGroup("Artazon", 1, frozenset({STADIUM})),
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
                ("filler_a", "hand"): 1,
                ("filler_b", "hand"): 1,
                ("filler_c", "hand"): 1,
                ("tag_call", "deck"): 1,
                ("tm_evolution", "deck"): 2,
                ("guzma_hala", "deck"): 1,
                ("artazon", "deck"): 1,
                ("jet_energy", "deck"): 1,
            }
        )
    )
    box_candidates = (
        DiscardCandidate("filler_a"),
        DiscardCandidate("filler_b"),
        DiscardCandidate("filler_c"),
    )
    box_selections = enumerate_discard_selections(
        initial.zones,
        box_candidates,
        3,
    )
    assert len(box_selections) == 1

    box_tx = execute_trainer_search_transaction(
        initial,
        profile=secret_box,
        action_card_class="secret_box",
        demands=secret_demands,
        targets=secret_targets,
        search_action=secret_action,
        discard_candidates=box_candidates,
        discard_selection=box_selections[0],
    )
    assert box_tx.after.zones.count("tm_evolution", "hand") == 1
    assert box_tx.after.zones.count("tm_evolution", "deck") == 1
    assert box_tx.after.zones.count("tag_call", "hand") == 1
    assert box_tx.after.zones.count("artazon", "hand") == 1
    assert box_tx.after.zones.count("guzma_hala", "hand") == 1

    gh_targets = (
        SearchZoneTarget(
            "unused_stadium",
            TargetGroup("Unused Stadium", 1, frozenset({STADIUM})),
        ),
        SearchZoneTarget(
            "tm_evolution",
            TargetGroup("Replacement TM Evolution", 1, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            "jet_energy",
            TargetGroup("Jet Energy", 1, frozenset({SPECIAL_ENERGY})),
        ),
    )
    gh_retrievals = enumerate_typed_retrieval_actions(
        guzma_hala.base_outputs + guzma_hala.conditional_outputs,
        tuple(target.group for target in gh_targets),
    )
    gh_retrieval = next(
        action
        for action in gh_retrievals
        if action.target_cost == (0, 1, 1)
    )

    gh_candidates = (
        DiscardCandidate("tag_call"),
        DiscardCandidate("tm_evolution", max_copies=1),
    )
    gh_selections = enumerate_discard_selections(
        box_tx.after.zones,
        gh_candidates,
        2,
    )
    assert len(gh_selections) == 1

    gh_tx = execute_trainer_retrieval_transaction(
        box_tx.after,
        profile=guzma_hala,
        action_card_class="guzma_hala",
        targets=gh_targets,
        retrieval_action=gh_retrieval,
        discard_candidates=gh_candidates,
        discard_selection=gh_selections[0],
    )

    assert gh_tx.discard_cost == 2
    assert gh_tx.optional_discard_paid
    assert gh_tx.used_conditional_outputs
    assert gh_tx.after.budget.supporter_used

    assert gh_tx.after.zones.count("tag_call", "discard") == 1
    assert gh_tx.after.zones.count("tm_evolution", "discard") == 1
    assert gh_tx.after.zones.count("tm_evolution", "hand") == 1
    assert gh_tx.after.zones.count("tm_evolution", "deck") == 0
    assert gh_tx.after.zones.count("artazon", "hand") == 1
    assert gh_tx.after.zones.count("jet_energy", "hand") == 1

    for card_class in {
        card_class for card_class, _zone, _count in initial.zones.counts
    } | {
        card_class for card_class, _zone, _count in gh_tx.after.zones.counts
    }:
        assert initial.zones.total(card_class) == gh_tx.after.zones.total(card_class)

    print("ledger_minimum_initial_fillers=3")
    print("ledger_total_discards=5")
    print("exact_initial_fillers=3")
    print("discarded_generated_payload=tm_evolution")
    print("reacquired_payload=tm_evolution")
    print("final_tm=1")
    print("final_artazon=1")
    print("final_jet=1")
    print("card_class_totals_conserved=True")
    print("All reacquisition transaction bridge checks passed.")


if __name__ == "__main__":
    main()
