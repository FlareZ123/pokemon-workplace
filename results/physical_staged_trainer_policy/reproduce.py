"""Reproduce exact physical connector selection with downstream Supporter deadlines."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from acquired_trainer_execution_capacity import TrainerExecutionRequirement
from discard_cost_witness import DiscardCandidate
from multicopy_zone_state import ZoneCountState
from physical_staged_trainer_policy import (
    PhysicalSearchOption,
    choose_physical_search,
)
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import (
    CompiledTrainerSearchProfile,
    SearchOutput,
)
from trainer_search_transaction import TrainerSearchExecutionState
from turn_action_budget import TurnAction, TurnActionBudget
from typed_search_retrieval import enumerate_typed_retrieval_actions
from typed_search_target_allocator import SUPPORTER, TargetGroup


def card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == card_id)


def state(
    hand: dict[str, int],
    *,
    budget: TurnActionBudget | None = None,
) -> TrainerSearchExecutionState:
    return TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping({
            **{(name, "hand"): copies for name, copies in hand.items()},
            ("boss", "deck"): 1,
        }),
        budget=budget if budget is not None else TurnActionBudget(),
    )


def main() -> None:
    computer_print = card("bw7-137")
    green_print = card("sm10-175")
    boss_print = card("swsh2-154")
    assert computer_print["name"] == "Computer Search"
    assert "Search your deck for a card" in " ".join(computer_print["rules"])
    assert green_print["name"] == "Green's Exploration"
    assert "Search your deck for up to 2 Trainer cards" in " ".join(
        green_print["rules"]
    )
    assert boss_print["name"] == "Boss's Orders"

    # The Computer Search branch is intentionally narrowed to the one
    # possible target in the represented deck: a single Boss Supporter.
    computer = CompiledTrainerSearchProfile(
        card_id="bw7-137",
        name="Computer Search",
        action_class="Item",
        base_outputs=(SearchOutput("Trainer card", 1),),
        required_discard_other_cards=2,
    )
    green = CompiledTrainerSearchProfile(
        card_id="sm10-175",
        name="Green's Exploration",
        action_class="Supporter",
        base_outputs=(SearchOutput("Trainer card", 2),),
        play_condition="no Pokémon with Abilities in play",
    )
    targets = (
        SearchZoneTarget(
            "boss",
            TargetGroup("Boss Supporter", 1, frozenset({SUPPORTER})),
        ),
    )

    def search_action(profile: CompiledTrainerSearchProfile):
        return next(
            action
            for action in enumerate_typed_retrieval_actions(
                profile.base_outputs,
                tuple(target.group for target in targets),
            )
            if action.target_cost == (1,)
        )

    def computer_option(candidates: tuple[DiscardCandidate, ...]):
        return PhysicalSearchOption(
            "Computer Search -> Boss",
            computer,
            "computer",
            targets,
            search_action(computer),
            discard_candidates=candidates,
        )

    green_option = PhysicalSearchOption(
        "Green -> Boss",
        green,
        "green",
        targets,
        search_action(green),
        play_condition_met=True,
    )
    goal = (
        TrainerExecutionRequirement(
            "Boss played this turn",
            "boss",
            "Supporter",
            deadline_turn=0,
        ),
    )

    # The low-cost Supporter connector acquires Boss, but blocks the
    # ordinary Supporter use required to execute it this same turn.
    # Computer Search pays two actual physical fodder cards and preserves
    # the Supporter slot.
    baseline = state({
        "computer": 1, "green": 1,
        "junk_a": 1, "junk_b": 1,
    })
    options = (
        green_option,
        computer_option((
            DiscardCandidate("junk_a"),
            DiscardCandidate("junk_b"),
        )),
    )
    best = choose_physical_search(
        baseline, options=options, execution_requirements=goal
    )
    assert best.all_goals_feasible
    assert best.chosen_option == "Computer Search -> Boss"
    assert best.discard_spent == 2
    assert best.after.zones.count("computer", "discard") == 1
    assert best.after.zones.count("green", "hand") == 1
    assert best.after.zones.count("boss", "hand") == 1
    assert best.after.zones.count("junk_a", "discard") == 1
    assert best.after.zones.count("junk_b", "discard") == 1

    # The same card count can fail if one physical card is protected.
    # A numeric "2 cards in hand" projection is too optimistic when the
    # only other source is a strategically indispensable protected card.
    protected = state({
        "computer": 1, "green": 1, "junk_a": 1,
        "protected": 1,
    })
    protected_option = computer_option((
        DiscardCandidate("junk_a"),
        DiscardCandidate("protected", max_copies=0),
    ))
    blocked = choose_physical_search(
        protected,
        options=(green_option, protected_option),
        execution_requirements=goal,
    )
    assert blocked.completed_units == 0
    assert not blocked.all_goals_feasible

    # The source card cannot pay its own "other cards" requirement,
    # even if the caller accidentally lists that source as a candidate.
    self_payment = choose_physical_search(
        state({"computer": 1, "junk_a": 1}),
        options=(computer_option((
            DiscardCandidate("computer"),
            DiscardCandidate("junk_a"),
        )),),
        execution_requirements=goal,
    )
    assert not self_payment.all_goals_feasible

    # A real two-Supporter quota changes the best option, holding
    # targets fixed. Green now leaves an additional Supporter use.
    dual = choose_physical_search(
        state(
            {"green": 1},
            budget=TurnActionBudget(supporter_play_limit=2),
        ),
        options=(green_option,),
        execution_requirements=goal,
    )
    assert dual.all_goals_feasible
    assert dual.chosen_option == "Green -> Boss"
    assert dual.discard_spent == 0
    assert dual.after.budget.supporter_plays_used == 1

    # A completed attack closes *all* ordinary same-turn Trainer plays.
    ended_budget = TurnActionBudget().consume(TurnAction.ATTACK)
    assert ended_budget is not None
    ended = choose_physical_search(
        state(
            {"computer": 1, "junk_a": 1, "junk_b": 1},
            budget=ended_budget,
        ),
        options=(options[1],),
        execution_requirements=goal,
    )
    assert ended.completed_units == 0

    # When the required card is already in hand, spending a search
    # connector provides no additional objective units and is dominated.
    already_have_boss = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping({
            ("computer", "hand"): 1,
            ("junk_a", "hand"): 1,
            ("junk_b", "hand"): 1,
            ("boss", "hand"): 1,
        })
    )
    no_op = choose_physical_search(
        already_have_boss,
        options=(options[1],),
        execution_requirements=goal,
    )
    assert no_op.all_goals_feasible
    assert no_op.chosen_option is None
    assert no_op.discard_spent == 0

    print(json.dumps({
        "source_prints": [
            computer_print["id"], green_print["id"], boss_print["id"]
        ],
        "ordinary_same_turn_optimal": best.chosen_option,
        "ordinary_same_turn_discarded": best.discard_spent,
        "protected_hand_same_turn_feasible": blocked.all_goals_feasible,
        "source_card_self_payment_feasible": self_payment.all_goals_feasible,
        "dual_supporter_optimal": dual.chosen_option,
        "after_attack_same_turn_feasible": ended.all_goals_feasible,
        "already_held_boss_optimal": "no action",
        "scope": "physical single-connector witness, not match outcomes",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
