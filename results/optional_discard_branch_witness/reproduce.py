"""Reproduce optional-discard branch choice independently of search output use."""

from __future__ import annotations

import json
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
    execute_trainer_retrieval_transaction,
)
from typed_search_retrieval import enumerate_typed_retrieval_actions
from typed_search_target_allocator import POKEMON_TOOL, SPECIAL_ENERGY, STADIUM, TargetGroup


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    profile = next(row for row in profiles if row.name == "Guzma & Hala")

    targets = (
        SearchZoneTarget("stadium", TargetGroup("Stadium", 1, frozenset({STADIUM}))),
        SearchZoneTarget("tool", TargetGroup("Tool", 1, frozenset({POKEMON_TOOL}))),
        SearchZoneTarget("special", TargetGroup("Special Energy", 1, frozenset({SPECIAL_ENERGY}))),
    )
    retrievals = enumerate_typed_retrieval_actions(
        profile.base_outputs + profile.conditional_outputs,
        tuple(target.group for target in targets),
    )
    stadium_only = next(action for action in retrievals if action.target_cost == (1, 0, 0))
    retrieve_none = next(action for action in retrievals if action.target_cost == (0, 0, 0))

    state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("guzma_hala", "hand"): 1,
                ("payload_a", "hand"): 1,
                ("payload_b", "hand"): 1,
                ("stadium", "deck"): 1,
                ("tool", "deck"): 1,
                ("special", "deck"): 1,
            }
        )
    )
    candidates = (
        DiscardCandidate("payload_a"),
        DiscardCandidate("payload_b"),
    )
    selection = enumerate_discard_selections(state.zones, candidates, 2)[0]

    free = execute_trainer_retrieval_transaction(
        state,
        profile=profile,
        action_card_class="guzma_hala",
        targets=targets,
        retrieval_action=stadium_only,
    )
    paid_same_retrieval = execute_trainer_retrieval_transaction(
        state,
        profile=profile,
        action_card_class="guzma_hala",
        targets=targets,
        retrieval_action=stadium_only,
        discard_candidates=candidates,
        discard_selection=selection,
        pay_optional_discard=True,
    )
    discard_only = execute_trainer_retrieval_transaction(
        state,
        profile=profile,
        action_card_class="guzma_hala",
        targets=targets,
        retrieval_action=retrieve_none,
        discard_candidates=candidates,
        discard_selection=selection,
        pay_optional_discard=True,
    )

    assert free.discard_cost == 0
    assert not free.optional_discard_paid
    assert paid_same_retrieval.discard_cost == 2
    assert paid_same_retrieval.optional_discard_paid
    assert not paid_same_retrieval.used_conditional_outputs
    assert discard_only.discard_cost == 2
    assert discard_only.optional_discard_paid
    assert not discard_only.used_conditional_outputs

    assert free.after.zones.count("payload_a", "hand") == 1
    assert paid_same_retrieval.after.zones.count("payload_a", "discard") == 1
    assert discard_only.after.zones.count("stadium", "deck") == 1

    free_zero_rejected = False
    try:
        execute_trainer_retrieval_transaction(
            state,
            profile=profile,
            action_card_class="guzma_hala",
            targets=targets,
            retrieval_action=retrieve_none,
        )
    except ValueError:
        free_zero_rejected = True
    assert free_zero_rejected

    print(
        json.dumps(
            {
                "same_stadium_retrieval_free_discard_cost": free.discard_cost,
                "same_stadium_retrieval_paid_discard_cost": paid_same_retrieval.discard_cost,
                "paid_without_conditional_search": True,
                "paid_with_zero_retrieval": True,
                "free_zero_retrieval_rejected": free_zero_rejected,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
