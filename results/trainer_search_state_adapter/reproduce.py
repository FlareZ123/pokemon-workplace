"""Reproduce state adaptation of compiled Trainer search profiles."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from lock_state_kernel import PlayerChannels, apply_play_lock
from resource_constrained_connectors import evaluate_resource_constrained_connectors
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_state_adapter import TrainerSearchState, adapt_compiled_search_profile


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def targets(*labels: str, count: int = 1):
    return tuple((label, count) for label in labels)


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")

    secret_box = representative(profiles, "Secret Box")
    secret_channels = ("Item card", "Pokémon Tool card", "Supporter card", "Stadium card")
    secret_state = TrainerSearchState(
        target_counts=targets(*secret_channels),
        discardable_cards=3,
    )
    secret = adapt_compiled_search_profile(secret_box, secret_channels, secret_state)
    assert secret is not None
    assert len(secret.profiles) == 15
    assert any(
        action.output == (1, 1, 1, 1) and action.cost == (3, 0, 0)
        for action in secret.profiles
    )
    secret_result = evaluate_resource_constrained_connectors(
        (1, 1, 1, 1),
        secret_state.resource_capacities,
        (secret,),
    )
    assert secret_result.exact_joint_feasible

    assert adapt_compiled_search_profile(
        secret_box,
        secret_channels,
        TrainerSearchState(
            target_counts=targets(*secret_channels),
            discardable_cards=2,
        ),
    ) is None

    assert adapt_compiled_search_profile(
        secret_box,
        secret_channels,
        TrainerSearchState(
            target_counts=targets(*secret_channels),
            discardable_cards=3,
            channels=apply_play_lock(PlayerChannels(), "item"),
        ),
    ) is None

    arven = representative(profiles, "Arven")
    arven_channels = ("Item card", "Pokémon Tool card")
    one_supporter = TrainerSearchState(
        target_counts=targets(*arven_channels, count=2),
        supporter_plays_remaining=1,
    )
    two_arven = adapt_compiled_search_profile(
        arven,
        arven_channels,
        one_supporter,
        copies=2,
    )
    assert two_arven is not None
    one_supporter_result = evaluate_resource_constrained_connectors(
        (2, 2),
        one_supporter.resource_capacities,
        (two_arven,),
    )
    assert one_supporter_result.raw_naive_joint_reachable
    assert not one_supporter_result.exact_joint_feasible

    two_supporters = TrainerSearchState(
        target_counts=targets(*arven_channels, count=2),
        supporter_plays_remaining=2,
    )
    two_arven_with_capacity = adapt_compiled_search_profile(
        arven,
        arven_channels,
        two_supporters,
        copies=2,
    )
    assert two_arven_with_capacity is not None
    assert evaluate_resource_constrained_connectors(
        (2, 2),
        two_supporters.resource_capacities,
        (two_arven_with_capacity,),
    ).exact_joint_feasible

    item_only_state = TrainerSearchState(
        target_counts=(("Item card", 1), ("Pokémon Tool card", 0)),
    )
    item_only_arven = adapt_compiled_search_profile(
        arven,
        arven_channels,
        item_only_state,
    )
    assert item_only_arven is not None
    assert {action.output for action in item_only_arven.profiles} == {(1, 0)}

    guzma_hala = representative(profiles, "Guzma & Hala")
    guzma_channels = ("Stadium card", "Pokémon Tool card", "Special Energy card")
    full_guzma_state = TrainerSearchState(
        target_counts=targets(*guzma_channels),
        discardable_cards=2,
        supporter_plays_remaining=1,
    )
    full_guzma = adapt_compiled_search_profile(
        guzma_hala,
        guzma_channels,
        full_guzma_state,
    )
    assert full_guzma is not None
    assert len(full_guzma.profiles) == 7
    assert any(
        action.output == (1, 1, 1) and action.cost == (2, 1, 0)
        for action in full_guzma.profiles
    )
    assert evaluate_resource_constrained_connectors(
        (1, 1, 1),
        full_guzma_state.resource_capacities,
        (full_guzma,),
    ).exact_joint_feasible

    base_only_state = TrainerSearchState(
        target_counts=targets(*guzma_channels),
        discardable_cards=0,
        supporter_plays_remaining=1,
    )
    base_only_guzma = adapt_compiled_search_profile(
        guzma_hala,
        guzma_channels,
        base_only_state,
    )
    assert base_only_guzma is not None
    assert len(base_only_guzma.profiles) == 1
    assert base_only_guzma.profiles[0].output == (1, 0, 0)
    assert not evaluate_resource_constrained_connectors(
        (1, 1, 1),
        base_only_state.resource_capacities,
        (base_only_guzma,),
    ).exact_joint_feasible

    assert adapt_compiled_search_profile(
        guzma_hala,
        guzma_channels,
        TrainerSearchState(
            target_counts=targets(*guzma_channels),
            discardable_cards=2,
            channels=apply_play_lock(PlayerChannels(), "supporter"),
        ),
    ) is None

    rosa = representative(profiles, "Rosa")
    rosa_channels = tuple(output.label for output in rosa.base_outputs)
    rosa_state = TrainerSearchState(target_counts=targets(*rosa_channels))
    assert adapt_compiled_search_profile(rosa, rosa_channels, rosa_state) is None
    assert adapt_compiled_search_profile(
        rosa,
        rosa_channels,
        rosa_state,
        play_condition_met=True,
    ) is not None

    larry = representative(profiles, "Larry's Skill")
    larry_channels = tuple(output.label for output in larry.base_outputs)
    assert adapt_compiled_search_profile(
        larry,
        larry_channels,
        TrainerSearchState(
            target_counts=targets(*larry_channels),
            discardable_cards=3,
            whole_hand_discard_count=4,
        ),
    ) is None

    larry_connector = adapt_compiled_search_profile(
        larry,
        larry_channels,
        TrainerSearchState(
            target_counts=targets(*larry_channels),
            discardable_cards=4,
            whole_hand_discard_count=4,
        ),
    )
    assert larry_connector is not None
    assert all(action.cost[0] == 4 for action in larry_connector.profiles)

    print(
        json.dumps(
            {
                "secret_box_state_valid_profiles": len(secret.profiles),
                "secret_box_joint_feasible": secret_result.exact_joint_feasible,
                "two_arven_one_supporter_joint_feasible": one_supporter_result.exact_joint_feasible,
                "two_arven_two_supporters_joint_feasible": True,
                "guzma_hala_full_profiles": len(full_guzma.profiles),
                "guzma_hala_no_discard_profiles": len(base_only_guzma.profiles),
                "rosa_requires_explicit_condition": True,
                "larry_whole_hand_gate": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
