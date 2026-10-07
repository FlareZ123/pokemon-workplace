"""Validate retrieval-first projection against demand-first feasibility."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from typed_search_retrieval import enumerate_typed_retrieval_actions, project_retrieval_to_demands
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


def profile(rows, name):
    return next(row for row in rows if row.name == name)


def compare(name, outputs, targets, demands):
    old = enumerate_typed_target_profiles(outputs, targets, demands)
    raw = enumerate_typed_retrieval_actions(outputs, targets)
    projected = set()
    raw_full = False
    for action in raw:
        result = project_retrieval_to_demands(action, targets, demands)
        projected.update(value for value in result.profiles if any(value))
        raw_full = raw_full or result.full_demand_feasible
    assert projected == set(old.profiles)
    assert raw_full == old.full_demand_feasible
    return {
        "name": name,
        "raw_actions": len(raw),
        "demand_actions": len(old.actions),
        "profiles": len(old.profiles),
    }


def main() -> None:
    rows = compile_multi_output_trainer_profiles(ROOT / "resources")

    gh = profile(rows, "Guzma & Hala")
    gh_row = compare(
        "guzma_hala",
        gh.base_outputs + gh.conditional_outputs,
        (
            TargetGroup("Stadium", 1, frozenset({STADIUM})),
            TargetGroup("Tool", 1, frozenset({POKEMON_TOOL})),
            TargetGroup("DCE", 1, frozenset({SPECIAL_ENERGY})),
        ),
        (make_demand("Special Energy", "Special Energy card"),),
    )

    secret = profile(rows, "Secret Box")
    secret_row = compare(
        "secret_box",
        secret.base_outputs,
        (
            TargetGroup("Item", 1, frozenset({ITEM})),
            TargetGroup("Tool", 1, frozenset({POKEMON_TOOL})),
            TargetGroup("Supporter", 1, frozenset({SUPPORTER})),
            TargetGroup("Stadium", 1, frozenset({STADIUM})),
        ),
        (
            make_demand("Item", "Item card"),
            make_demand("Supporter", "Supporter card"),
        ),
    )

    print(json.dumps([gh_row, secret_row], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
