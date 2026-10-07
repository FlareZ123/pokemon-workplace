"""Reproduce synchronized physical Trainer search and card-arrival provenance."""

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
from trainer_transaction_provenance import (
    SynchronizedTrainerState,
    advance_synchronized_state,
    mirror_trainer_search_transaction,
    provenance_from_zones,
    project_zones,
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
    SearchZoneTarget("tm_evolution", TargetGroup("TM Evolution", 1, frozenset({POKEMON_TOOL}))),
    SearchZoneTarget("guzma_hala", TargetGroup("Guzma & Hala", 1, frozenset({SUPPORTER}))),
    SearchZoneTarget("artazon", TargetGroup("Artazon", 1, frozenset({STADIUM}))),
)
BOX_RETRIEVAL = TypedRetrievalAction((1, 1, 1, 1), (1, 1, 1, 1))
GH_TARGETS = (
    SearchZoneTarget("artazon", TargetGroup("Artazon", 1, frozenset({STADIUM}))),
    SearchZoneTarget("tm_evolution", TargetGroup("TM Evolution", 1, frozenset({POKEMON_TOOL}))),
    SearchZoneTarget("jet_energy", TargetGroup("Jet Energy", 1, frozenset({SPECIAL_ENERGY}))),
)
GH_RETRIEVAL = TypedRetrievalAction((0, 1, 1), (0, 1, 1))


def start_zones(*, extra_tm_in_hand: int = 0) -> ZoneCountState:
    return ZoneCountState.from_mapping(
        {
            ("secret_box", "hand"): 1,
            ("filler", "hand"): 3,
            ("tm_evolution", "hand"): extra_tm_in_hand,
            ("tag_call", "deck"): 1,
            ("guzma_hala", "deck"): 1,
            ("tm_evolution", "deck"): 2,
            ("artazon", "deck"): 2,
            ("jet_energy", "deck"): 1,
        }
    )


def execute_box(state: TrainerSearchExecutionState):
    candidates = (DiscardCandidate("filler"),)
    selection = enumerate_discard_selections(state.zones, candidates, 3)[0]
    transaction = execute_trainer_retrieval_transaction(
        state,
        profile=SECRET_BOX,
        action_card_class="secret_box",
        targets=BOX_TARGETS,
        retrieval_action=BOX_RETRIEVAL,
        discard_candidates=candidates,
        discard_selection=selection,
    )
    return transaction, candidates, selection


def execute_gh(state: TrainerSearchExecutionState):
    candidates = (
        DiscardCandidate("tag_call"),
        DiscardCandidate("tm_evolution", max_copies=1),
    )
    selection = next(
        selection
        for selection in enumerate_discard_selections(state.zones, candidates, 2)
        if selection.counts == (1, 1)
    )
    transaction = execute_trainer_retrieval_transaction(
        state,
        profile=GUZMA_HALA,
        action_card_class="guzma_hala",
        targets=GH_TARGETS,
        retrieval_action=GH_RETRIEVAL,
        discard_candidates=candidates,
        discard_selection=selection,
        pay_optional_discard=True,
    )
    return transaction, candidates, selection


def unique_line() -> SynchronizedTrainerState:
    physical = TrainerSearchExecutionState(zones=start_zones())
    synchronized = SynchronizedTrainerState(
        physical=physical,
        provenance=provenance_from_zones(physical.zones),
    )

    box, box_candidates, box_selection = execute_box(physical)
    box_witnesses = mirror_trainer_search_transaction(
        synchronized,
        box,
        action_card_class="secret_box",
        action_name="Secret Box",
        step_index=0,
        discard_candidates=box_candidates,
        discard_selection=box_selection,
        targets=BOX_TARGETS,
        target_cost=BOX_RETRIEVAL.target_cost,
    )
    assert len(box_witnesses) == 1
    synchronized = advance_synchronized_state(box_witnesses[0])

    assert synchronized.provenance.count(
        "tm_evolution", "hand", origin="0:Secret Box"
    ) == 1
    assert synchronized.provenance.count(
        "guzma_hala", "hand", origin="0:Secret Box"
    ) == 1

    gh, gh_candidates, gh_selection = execute_gh(synchronized.physical)
    gh_witnesses = mirror_trainer_search_transaction(
        synchronized,
        gh,
        action_card_class="guzma_hala",
        action_name="Guzma & Hala",
        step_index=1,
        discard_candidates=gh_candidates,
        discard_selection=gh_selection,
        targets=GH_TARGETS,
        target_cost=GH_RETRIEVAL.target_cost,
    )
    assert len(gh_witnesses) == 1
    synchronized = advance_synchronized_state(gh_witnesses[0])

    assert synchronized.provenance.count(
        "tm_evolution", "discard", origin="0:Secret Box"
    ) == 1
    assert synchronized.provenance.count(
        "tm_evolution", "hand", origin="1:Guzma & Hala"
    ) == 1
    assert synchronized.provenance.count(
        "tag_call", "discard", origin="0:Secret Box"
    ) == 1
    assert synchronized.provenance.count(
        "guzma_hala", "discard", origin="0:Secret Box"
    ) == 1
    assert project_zones(synchronized.provenance) == synchronized.physical.zones
    return synchronized


def ambiguous_same_class_line() -> int:
    physical = TrainerSearchExecutionState(zones=start_zones(extra_tm_in_hand=1))
    synchronized = SynchronizedTrainerState(
        physical=physical,
        provenance=provenance_from_zones(physical.zones),
    )

    box, box_candidates, box_selection = execute_box(physical)
    box_witness = mirror_trainer_search_transaction(
        synchronized,
        box,
        action_card_class="secret_box",
        action_name="Secret Box",
        step_index=0,
        discard_candidates=box_candidates,
        discard_selection=box_selection,
        targets=BOX_TARGETS,
        target_cost=BOX_RETRIEVAL.target_cost,
    )[0]
    synchronized = advance_synchronized_state(box_witness)

    assert synchronized.provenance.count(
        "tm_evolution", "hand", origin="initial"
    ) == 1
    assert synchronized.provenance.count(
        "tm_evolution", "hand", origin="0:Secret Box"
    ) == 1

    gh, gh_candidates, gh_selection = execute_gh(synchronized.physical)
    witnesses = mirror_trainer_search_transaction(
        synchronized,
        gh,
        action_card_class="guzma_hala",
        action_name="Guzma & Hala",
        step_index=1,
        discard_candidates=gh_candidates,
        discard_selection=gh_selection,
        targets=GH_TARGETS,
        target_cost=GH_RETRIEVAL.target_cost,
    )
    assert len(witnesses) == 2
    discarded_origins = {
        origin
        for witness in witnesses
        for card_class, origin, zone, count in witness.after.counts
        if card_class == "tm_evolution" and zone == "discard" and count == 1
    }
    assert discarded_origins == {"initial", "0:Secret Box"}
    assert all(project_zones(witness.after) == gh.after.zones for witness in witnesses)
    return len(witnesses)


def main() -> None:
    final = unique_line()
    ambiguous_count = ambiguous_same_class_line()

    print(
        json.dumps(
            {
                "synchronized_projection_matches_physical": True,
                "box_tm_origin": "0:Secret Box",
                "discarded_tm_origin": "0:Secret Box",
                "replacement_tm_origin": "1:Guzma & Hala",
                "final_tm_in_hand": final.physical.zones.count("tm_evolution", "hand"),
                "same_class_physical_alias_provenance_witnesses": ambiguous_count,
                "ambiguous_discard_origins": ["0:Secret Box", "initial"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
