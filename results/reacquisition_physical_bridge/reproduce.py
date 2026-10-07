"""Reproduce physical copy depletion in a Secret Box -> Guzma & Hala reacquisition line."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import CompiledTrainerSearchProfile, SearchOutput
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
)
from typed_search_retrieval import TypedRetrievalAction
from typed_search_target_allocator import (
    ITEM,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
    SUPPORTER,
    TargetGroup,
)


SECRET_BOX = CompiledTrainerSearchProfile(
    card_id="sv6-163",
    name="Secret Box",
    action_class="Item",
    base_outputs=(
        SearchOutput("Item card"),
        SearchOutput("Pokémon Tool card"),
        SearchOutput("Supporter card"),
        SearchOutput("Stadium card"),
    ),
    required_discard_other_cards=3,
)

GUZMA_HALA = CompiledTrainerSearchProfile(
    card_id="sm12-193",
    name="Guzma & Hala",
    action_class="Supporter",
    base_outputs=(SearchOutput("Stadium card"),),
    conditional_outputs=(
        SearchOutput("Pokémon Tool card"),
        SearchOutput("Special Energy card"),
    ),
    optional_discard_other_cards=2,
)


BOX_TARGETS = (
    SearchZoneTarget("tag_call", TargetGroup("Tag Call", 1, frozenset({ITEM}))),
    SearchZoneTarget(
        "tm_evolution",
        TargetGroup("Technical Machine: Evolution", 1, frozenset({POKEMON_TOOL})),
    ),
    SearchZoneTarget(
        "guzma_hala",
        TargetGroup("Guzma & Hala", 1, frozenset({SUPPORTER})),
    ),
    SearchZoneTarget("artazon", TargetGroup("Artazon", 1, frozenset({STADIUM}))),
)
BOX_RETRIEVAL = TypedRetrievalAction(
    target_cost=(1, 1, 1, 1),
    axis_usage=(1, 1, 1, 1),
)

GH_TARGETS = (
    SearchZoneTarget("artazon", TargetGroup("Artazon", 1, frozenset({STADIUM}))),
    SearchZoneTarget(
        "tm_evolution",
        TargetGroup("Technical Machine: Evolution", 1, frozenset({POKEMON_TOOL})),
    ),
    SearchZoneTarget(
        "jet_energy",
        TargetGroup("Jet Energy", 1, frozenset({SPECIAL_ENERGY})),
    ),
)
GH_RETRIEVAL = TypedRetrievalAction(
    target_cost=(0, 1, 1),
    axis_usage=(0, 1, 1),
)


def initial_state(tm_copies: int) -> TrainerSearchExecutionState:
    return TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("secret_box", "hand"): 1,
                ("filler", "hand"): 3,
                ("tag_call", "deck"): 1,
                ("guzma_hala", "deck"): 1,
                ("tm_evolution", "deck"): tm_copies,
                ("artazon", "deck"): 2,
                ("jet_energy", "deck"): 1,
            }
        )
    )


def execute_box(state: TrainerSearchExecutionState):
    candidates = (DiscardCandidate("filler"),)
    selection = enumerate_discard_selections(state.zones, candidates, 3)[0]
    return execute_trainer_retrieval_transaction(
        state,
        profile=SECRET_BOX,
        action_card_class="secret_box",
        targets=BOX_TARGETS,
        retrieval_action=BOX_RETRIEVAL,
        discard_candidates=candidates,
        discard_selection=selection,
    )


def execute_gh_after_box(state: TrainerSearchExecutionState):
    candidates = (
        DiscardCandidate("tag_call"),
        DiscardCandidate("tm_evolution", max_copies=1),
    )
    selection = enumerate_discard_selections(state.zones, candidates, 2)[0]
    return execute_trainer_retrieval_transaction(
        state,
        profile=GUZMA_HALA,
        action_card_class="guzma_hala",
        targets=GH_TARGETS,
        retrieval_action=GH_RETRIEVAL,
        discard_candidates=candidates,
        discard_selection=selection,
        pay_optional_discard=True,
    )


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def assert_totals_equal(before: ZoneCountState, after: ZoneCountState) -> None:
    classes = {
        card_class for card_class, _zone, _count in before.counts
    } | {
        card_class for card_class, _zone, _count in after.counts
    }
    for card_class in classes:
        assert before.total(card_class) == after.total(card_class)


def main() -> None:
    start = initial_state(tm_copies=2)
    box = execute_box(start)

    assert box.after.zones.count("secret_box", "discard") == 1
    assert box.after.zones.count("filler", "discard") == 3
    assert box.after.zones.count("tm_evolution", "hand") == 1
    assert box.after.zones.count("tm_evolution", "deck") == 1
    assert box.after.zones.count("artazon", "hand") == 1
    assert box.after.zones.count("artazon", "deck") == 1
    assert box.after.zones.count("guzma_hala", "hand") == 1
    assert box.after.zones.count("tag_call", "hand") == 1

    gh = execute_gh_after_box(box.after)
    assert gh.optional_discard_paid
    assert gh.used_conditional_outputs
    assert gh.after.budget.supporter_used

    assert gh.after.zones.count("tag_call", "discard") == 1
    assert gh.after.zones.count("tm_evolution", "discard") == 1
    assert gh.after.zones.count("tm_evolution", "deck") == 0
    assert gh.after.zones.count("tm_evolution", "hand") == 1
    assert gh.after.zones.count("artazon", "hand") == 1
    assert gh.after.zones.count("jet_energy", "hand") == 1
    assert gh.after.zones.count("guzma_hala", "discard") == 1

    assert_totals_equal(start.zones, gh.after.zones)

    depleted_start = initial_state(tm_copies=1)
    depleted_box = execute_box(depleted_start)
    assert depleted_box.after.zones.count("tm_evolution", "deck") == 0
    abstract_gh_action_still_describes_one_tool = GH_RETRIEVAL.target_cost[1] == 1
    assert abstract_gh_action_still_describes_one_tool

    replacement_rejected = expect_value_error(
        lambda: execute_gh_after_box(depleted_box.after)
    )
    assert replacement_rejected

    no_side_payload_start = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("guzma_hala", "hand"): 1,
                ("tm_evolution", "hand"): 1,
                ("tm_evolution", "deck"): 1,
                ("artazon", "hand"): 1,
                ("jet_energy", "deck"): 1,
            }
        )
    )
    no_side_candidates = (DiscardCandidate("tm_evolution"),)
    no_side_selections = enumerate_discard_selections(
        no_side_payload_start.zones,
        no_side_candidates,
        2,
    )
    assert no_side_selections == ()

    print(
        json.dumps(
            {
                "physical_reacquisition_succeeded": True,
                "box_first_tm_moved_deck_to_hand": True,
                "gh_discarded_first_tm_copy": True,
                "gh_retrieved_second_tm_copy": True,
                "final_required_payload": {
                    "tm_evolution_hand": gh.after.zones.count("tm_evolution", "hand"),
                    "artazon_hand": gh.after.zones.count("artazon", "hand"),
                    "jet_energy_hand": gh.after.zones.count("jet_energy", "hand"),
                },
                "supporter_budget_consumed": gh.after.budget.supporter_used,
                "card_totals_conserved": True,
                "depleted_second_copy_rejected_at_execution": replacement_rejected,
                "second_discard_still_needs_two_physical_cards": no_side_selections == (),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
