"""Reproduce a selected Secret Box -> Guzma & Hala physical search chain."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from acquired_trainer_execution_capacity import TrainerExecutionRequirement
from discard_cost_witness import DiscardCandidate
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from physical_search_sequence_policy import choose_physical_search_sequence
from physical_staged_trainer_policy import PhysicalSearchOption
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import TrainerSearchExecutionState
from turn_action_budget import TurnAction, TurnActionBudget
from typed_search_retrieval import enumerate_typed_retrieval_actions
from typed_search_target_allocator import (
    ITEM,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
    SUPPORTER,
    TargetGroup,
)


def card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def group(card_class: str, tag: str) -> SearchZoneTarget:
    return SearchZoneTarget(
        card_class, TargetGroup(card_class, 1, frozenset({tag}))
    )


def full_action(profile, targets):
    expected = (1,) * len(targets)
    return next(
        action
        for action in enumerate_typed_retrieval_actions(
            profile.base_outputs + profile.conditional_outputs,
            tuple(target.group for target in targets),
        )
        if action.target_cost == expected
    )


def main() -> None:
    secret_print = card("sv6-163")
    gh_print = card("sm12-193")
    assert secret_print["name"] == "Secret Box"
    assert gh_print["name"] == "Guzma & Hala"
    assert "discard 3 other cards" in " ".join(secret_print["rules"])
    assert "discard 2 other cards" in " ".join(gh_print["rules"])

    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    box = next(p for p in profiles if p.name == "Secret Box")
    gh = next(p for p in profiles if p.name == "Guzma & Hala")
    assert box.action_class == "Item"
    assert box.required_discard_other_cards == 3
    assert gh.action_class == "Supporter"
    assert gh.optional_discard_other_cards == 2

    box_targets = (
        group("sb_item", ITEM),
        group("sb_tool", POKEMON_TOOL),
        group("guzma_hala", SUPPORTER),
        group("sb_stadium", STADIUM),
    )
    gh_targets = (
        group("gh_stadium", STADIUM),
        group("gh_tool", POKEMON_TOOL),
        group("gh_special", SPECIAL_ENERGY),
    )
    box_option = PhysicalSearchOption(
        "Secret Box full",
        box,
        "secret_box",
        box_targets,
        full_action(box, box_targets),
        discard_candidates=(
            DiscardCandidate("fodder_a"),
            DiscardCandidate("fodder_b"),
            DiscardCandidate("fodder_c"),
        ),
    )
    gh_option = PhysicalSearchOption(
        "Guzma & Hala paid",
        gh,
        "guzma_hala",
        gh_targets,
        full_action(gh, gh_targets),
        discard_candidates=(
            DiscardCandidate("sb_item"),
            DiscardCandidate("sb_stadium"),
            DiscardCandidate("sb_tool", max_copies=0),
        ),
    )

    inventory = {
        ("secret_box", "hand"): 1,
        ("fodder_a", "hand"): 1,
        ("fodder_b", "hand"): 1,
        ("fodder_c", "hand"): 1,
        **{
            (t.card_class, "deck"): 1
            for t in box_targets + gh_targets
        },
    }
    initial = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(inventory)
    )
    goals = (
        TrainerExecutionRequirement(
            "retained Box Tool",
            "sb_tool",
            "Pokémon Tool",
            deadline_turn=0,
        ),
        TrainerExecutionRequirement(
            "second G&H Tool",
            "gh_tool",
            "Pokémon Tool",
            deadline_turn=0,
        ),
    )

    options = (gh_option, box_option)  # intentionally reverse legal order
    one = choose_physical_search_sequence(
        initial, options=options, execution_requirements=goals,
        max_actions=1,
    )
    assert one.completed_units == 1
    assert one.chosen_options == ("Secret Box full",)

    two = choose_physical_search_sequence(
        initial, options=options, execution_requirements=goals,
        max_actions=2,
    )
    assert two.all_goals_feasible
    assert two.chosen_options == (
        "Secret Box full", "Guzma & Hala paid"
    )
    assert two.discard_spent == 5
    assert len(two.transactions) == 2
    assert two.transactions[0].discard_cost == 3
    assert two.transactions[1].discard_cost == 2
    assert two.after.budget.supporter_plays_used == 1
    assert two.after.zones.count("sb_tool", "hand") == 1
    assert two.after.zones.count("gh_tool", "hand") == 1
    assert two.after.zones.count("sb_item", "discard") == 1
    assert two.after.zones.count("sb_stadium", "discard") == 1
    assert two.after.zones.count("gh_special", "hand") == 1
    assert two.after.zones.count("gh_stadium", "hand") == 1
    assert two.after.zones.count("guzma_hala", "discard") == 1
    assert two.after.zones.count("secret_box", "discard") == 1

    # The G&H optional discard comes from newly acquired Box outputs.
    assert two.transactions[0].after.zones.count("sb_item", "hand") == 1
    assert two.transactions[0].after.zones.count("sb_stadium", "hand") == 1
    assert two.transactions[0].after.zones.count("guzma_hala", "hand") == 1
    for name, _, _ in initial.zones.counts:
        assert initial.zones.total(name) == two.after.zones.total(name)

    no_fodder = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping({
            k: v for k, v in inventory.items()
            if k != ("fodder_c", "hand")
        })
    )
    unavailable = choose_physical_search_sequence(
        no_fodder, options=options,
        execution_requirements=goals,
    )
    assert unavailable.completed_units == 0

    supporter_locked = choose_physical_search_sequence(
        TrainerSearchExecutionState(
            zones=initial.zones,
            channels=PlayerChannels(supporter_play=False),
        ),
        options=options, execution_requirements=goals,
    )
    assert supporter_locked.completed_units == 1
    assert supporter_locked.chosen_options == ("Secret Box full",)

    tool_locked = choose_physical_search_sequence(
        TrainerSearchExecutionState(
            zones=initial.zones,
            channels=PlayerChannels(tool_play=False),
        ),
        options=options, execution_requirements=goals,
    )
    assert tool_locked.completed_units == 0

    ended_budget = TurnActionBudget().consume(TurnAction.ATTACK)
    assert ended_budget is not None
    ended = choose_physical_search_sequence(
        TrainerSearchExecutionState(
            zones=initial.zones,
            budget=ended_budget,
        ),
        options=options, execution_requirements=goals,
    )
    assert ended.completed_units == 0

    zero_steps = choose_physical_search_sequence(
        initial, options=options, execution_requirements=goals,
        max_actions=0,
    )
    assert zero_steps.completed_units == 0

    print(json.dumps({
        "physical_source_prints": (
            secret_print["id"], gh_print["id"]
        ),
        "one_action_units": one.completed_units,
        "two_action_units": two.completed_units,
        "two_action_route": two.chosen_options,
        "physical_discard_spent": two.discard_spent,
        "paid_from_generated_search_outputs": 2,
        "insufficient_first_payment_units": unavailable.completed_units,
        "supporter_locked_units": supporter_locked.completed_units,
        "tool_locked_units": tool_locked.completed_units,
        "ended_turn_units": ended.completed_units,
        "scope": "generic Tool-play capacity only; not board or match",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
