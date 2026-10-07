"""Reproduce retrieval-choice separation from strategic demand projection."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from typed_search_retrieval import (
    enumerate_typed_retrieval_actions,
    project_retrieval_to_demands,
)
from typed_search_target_allocator import (
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
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
    guzma_hala = representative(profiles, "Guzma & Hala")
    outputs = guzma_hala.base_outputs + guzma_hala.conditional_outputs

    targets = (
        TargetGroup("Stadium target", 1, frozenset({STADIUM})),
        TargetGroup("Tool target", 1, frozenset({POKEMON_TOOL})),
        TargetGroup("DCE target", 1, frozenset({SPECIAL_ENERGY})),
    )
    immediate_demands = (
        make_demand("need Special Energy", "Special Energy card"),
    )

    retrievals = enumerate_typed_retrieval_actions(outputs, targets)
    assert len(retrievals) == 8

    dce_only = next(
        action
        for action in retrievals
        if action.target_cost == (0, 0, 1)
    )
    full_payload = next(
        action
        for action in retrievals
        if action.target_cost == (1, 1, 1)
    )

    dce_projection = project_retrieval_to_demands(
        dce_only,
        targets,
        immediate_demands,
    )
    full_projection = project_retrieval_to_demands(
        full_payload,
        targets,
        immediate_demands,
    )
    assert dce_projection.full_demand_feasible
    assert full_projection.full_demand_feasible
    assert dce_projection.minimum_unmet_units == 0
    assert full_projection.minimum_unmet_units == 0

    demand_first = enumerate_typed_target_profiles(
        outputs,
        targets,
        immediate_demands,
    )
    satisfying = tuple(
        action
        for action in demand_first.actions
        if action.output == (1,)
    )
    assert {action.target_cost for action in satisfying} == {(0, 0, 1)}
    assert full_payload.target_cost not in {
        action.target_cost
        for action in satisfying
    }

    print(
        json.dumps(
            {
                "raw_retrieval_actions": len(retrievals),
                "immediate_demand_units": 1,
                "dce_only_retrieval": list(dce_only.target_cost),
                "full_side_payload_retrieval": list(full_payload.target_cost),
                "both_satisfy_same_immediate_demand": True,
                "demand_first_full_payload_preserved": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
