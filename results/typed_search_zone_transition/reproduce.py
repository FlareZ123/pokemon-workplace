"""Reproduce exact typed-search action materialization into zone state."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget, apply_typed_search_action
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import (
    BASIC_ENERGY,
    SPECIAL_ENERGY,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


def main() -> None:
    targets = (
        TargetGroup(
            "Basic Fire Energy",
            1,
            frozenset({BASIC_ENERGY, "type:fire"}),
        ),
        TargetGroup(
            "Double Colorless Energy",
            1,
            frozenset({SPECIAL_ENERGY}),
        ),
    )
    allocation = enumerate_typed_target_profiles(
        (SearchOutput("Energy card", 1),),
        targets,
        (make_demand("generic energy", "Energy card"),),
    )

    assert allocation.profiles == ((1,),)

    aliased_actions = tuple(
        action
        for action in allocation.actions
        if action.output == (1,)
    )
    assert {action.target_cost for action in aliased_actions} == {
        (1, 0),
        (0, 1),
    }

    state = ZoneCountState.from_mapping(
        {
            ("basic_fire", "deck"): 1,
            ("dce", "deck"): 1,
        }
    )
    bound_targets = (
        SearchZoneTarget("basic_fire", targets[0]),
        SearchZoneTarget("dce", targets[1]),
    )

    outcomes = {}
    for action in aliased_actions:
        transition = apply_typed_search_action(
            state,
            bound_targets,
            action,
        )
        signature = (
            transition.after.count("basic_fire", "hand"),
            transition.after.count("dce", "hand"),
        )
        outcomes[action.target_cost] = signature

        assert transition.after.total("basic_fire") == 1
        assert transition.after.total("dce") == 1
        assert sum(move.amount for move in transition.moves) == 1

    assert set(outcomes.values()) == {(1, 0), (0, 1)}

    stale_state = ZoneCountState.from_mapping(
        {
            ("basic_fire", "deck"): 1,
            ("dce", "hand"): 1,
        }
    )
    dce_action = next(
        action
        for action in aliased_actions
        if action.target_cost == (0, 1)
    )
    stale_rejected = False
    try:
        apply_typed_search_action(
            stale_state,
            bound_targets,
            dce_action,
        )
    except ValueError:
        stale_rejected = True
    assert stale_rejected

    print(
        json.dumps(
            {
                "collapsed_demand_profiles": len(allocation.profiles),
                "distinct_exact_actions_for_profile": len(aliased_actions),
                "exact_target_costs": sorted(
                    [list(action.target_cost) for action in aliased_actions]
                ),
                "distinct_hand_outcomes": len(set(outcomes.values())),
                "stale_action_rejected": stale_rejected,
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
