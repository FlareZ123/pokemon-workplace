"""Show that replacement reachability can fail under shared Supporter bandwidth."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bounded_state_planner import shortest_bounded_plan  # noqa: E402
from continuation_discard_policy import (  # noqa: E402
    continuation_feasible_discards,
    feasible_selections,
)
from discard_cost_witness import (  # noqa: E402
    DiscardCandidate,
    apply_discard_selection,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState  # noqa: E402
from search_zone_transition import SearchZoneTarget  # noqa: E402
from trainer_search_profile_compiler import (  # noqa: E402
    compile_multi_output_trainer_profiles,
)
from trainer_search_transaction import (  # noqa: E402
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
)
from turn_action_budget import TurnActionBudget  # noqa: E402
from typed_search_retrieval import (  # noqa: E402
    enumerate_typed_retrieval_actions,
)
from typed_search_target_allocator import (  # noqa: E402
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    TargetGroup,
)


FODDER = "fodder"
TM_EVOLUTION = "tm_evolution"
JET_ENERGY = "jet_energy"
ARVEN = "arven"
COLRESS = "colress_tenacity"
GUZMA_HALA = "guzma_hala"


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def one_target_action(profile, target: SearchZoneTarget):
    actions = enumerate_typed_retrieval_actions(
        profile.base_outputs + profile.conditional_outputs,
        (target.group,),
    )
    matches = [action for action in actions if action.target_cost == (1,)]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one one-target action for {profile.name}, found {len(matches)}"
        )
    return matches[0]


def arven_generator(profile):
    def generate(state: TrainerSearchExecutionState):
        copies = state.zones.count(TM_EVOLUTION, "deck")
        if copies <= 0:
            return
        target = SearchZoneTarget(
            TM_EVOLUTION,
            TargetGroup("TM Evolution", copies, frozenset({POKEMON_TOOL})),
        )
        action = one_target_action(profile, target)
        try:
            transaction = execute_trainer_retrieval_transaction(
                state,
                profile=profile,
                action_card_class=ARVEN,
                targets=(target,),
                retrieval_action=action,
            )
        except ValueError:
            return
        yield ("Arven -> TM Evolution", transaction.after)

    return generate


def colress_generator(profile):
    def generate(state: TrainerSearchExecutionState):
        copies = state.zones.count(JET_ENERGY, "deck")
        if copies <= 0:
            return
        target = SearchZoneTarget(
            JET_ENERGY,
            TargetGroup("Jet Energy", copies, frozenset({SPECIAL_ENERGY})),
        )
        action = one_target_action(profile, target)
        try:
            transaction = execute_trainer_retrieval_transaction(
                state,
                profile=profile,
                action_card_class=COLRESS,
                targets=(target,),
                retrieval_action=action,
            )
        except ValueError:
            return
        yield ("Colress's Tenacity -> Jet Energy", transaction.after)

    return generate


def guzma_hala_generator(profile):
    def generate(state: TrainerSearchExecutionState):
        tm_copies = state.zones.count(TM_EVOLUTION, "deck")
        jet_copies = state.zones.count(JET_ENERGY, "deck")
        if tm_copies <= 0 or jet_copies <= 0:
            return

        targets = (
            SearchZoneTarget(
                TM_EVOLUTION,
                TargetGroup("TM Evolution", tm_copies, frozenset({POKEMON_TOOL})),
            ),
            SearchZoneTarget(
                JET_ENERGY,
                TargetGroup("Jet Energy", jet_copies, frozenset({SPECIAL_ENERGY})),
            ),
        )
        actions = enumerate_typed_retrieval_actions(
            profile.base_outputs + profile.conditional_outputs,
            tuple(target.group for target in targets),
        )
        retrievals = [
            action
            for action in actions
            if action.target_cost == (1, 1)
        ]
        if len(retrievals) != 1:
            raise AssertionError(
                f"expected one TM+Jet G&H retrieval, found {len(retrievals)}"
            )

        discard_candidates = (
            DiscardCandidate(ARVEN),
            DiscardCandidate(COLRESS),
        )
        selections = enumerate_discard_selections(
            state.zones,
            discard_candidates,
            2,
        )
        if len(selections) != 1:
            return

        try:
            transaction = execute_trainer_retrieval_transaction(
                state,
                profile=profile,
                action_card_class=GUZMA_HALA,
                targets=targets,
                retrieval_action=retrievals[0],
                discard_candidates=discard_candidates,
                discard_selection=selections[0],
                pay_optional_discard=True,
            )
        except ValueError:
            return
        yield ("Guzma & Hala -> TM Evolution + Jet Energy", transaction.after)

    return generate


def goal(state: TrainerSearchExecutionState) -> bool:
    return (
        state.zones.count(TM_EVOLUTION, "hand") >= 1
        and state.zones.count(JET_ENERGY, "hand") >= 1
    )


def selection_names(candidates, selection):
    return tuple(
        candidate.card_class
        for candidate, count in zip(candidates, selection.counts, strict=True)
        for _ in range(count)
    )


def continuation_with_planner(
    candidates,
    actions,
    *,
    supporter_limit: int,
):
    def generate(state: ZoneCountState, selection):
        discarded = apply_discard_selection(
            state,
            candidates,
            selection,
        ).after
        initial = TrainerSearchExecutionState(
            zones=discarded,
            budget=TurnActionBudget(
                supporter_play_limit=supporter_limit,
            ),
        )
        plan = shortest_bounded_plan(
            initial,
            actions,
            goal,
            max_depth=2,
        )
        if plan is not None:
            yield (" -> ".join(plan.labels), plan.final_state.zones)

    return generate


def safe_discards(
    state,
    candidates,
    actions,
    *,
    supporter_limit,
):
    witnesses = continuation_feasible_discards(
        state,
        candidates,
        1,
        continuation_with_planner(
            candidates,
            actions,
            supporter_limit=supporter_limit,
        ),
        {
            TM_EVOLUTION: 1,
            JET_ENERGY: 1,
        },
    )
    return tuple(
        sorted(
            selection_names(candidates, selection)
            for selection in feasible_selections(witnesses)
        )
    )


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    arven = representative(profiles, "Arven")
    colress = representative(profiles, "Colress's Tenacity")
    guzma_hala = representative(profiles, "Guzma & Hala")

    state = ZoneCountState.from_mapping(
        {
            (FODDER, "hand"): 1,
            (TM_EVOLUTION, "hand"): 1,
            (ARVEN, "hand"): 1,
            (COLRESS, "hand"): 1,
            (GUZMA_HALA, "hand"): 1,
            (TM_EVOLUTION, "deck"): 1,
            (JET_ENERGY, "deck"): 1,
        }
    )
    candidates = (
        DiscardCandidate(FODDER),
        DiscardCandidate(TM_EVOLUTION),
    )

    arven_action = arven_generator(arven)
    colress_action = colress_generator(colress)
    gnh_action = guzma_hala_generator(guzma_hala)

    one_supporter_separate = safe_discards(
        state,
        candidates,
        (arven_action, colress_action),
        supporter_limit=1,
    )
    assert one_supporter_separate == ((FODDER,),)

    two_supporters_separate = safe_discards(
        state,
        candidates,
        (arven_action, colress_action),
        supporter_limit=2,
    )
    assert two_supporters_separate == tuple(
        sorted(((FODDER,), (TM_EVOLUTION,)))
    )

    one_supporter_multi_axis = safe_discards(
        state,
        candidates,
        (arven_action, colress_action, gnh_action),
        supporter_limit=1,
    )
    assert one_supporter_multi_axis == tuple(
        sorted(((FODDER,), (TM_EVOLUTION,)))
    )

    tm_selection = next(
        selection
        for selection in enumerate_discard_selections(
            state,
            candidates,
            1,
        )
        if selection_names(candidates, selection) == (TM_EVOLUTION,)
    )
    after_tm_discard = apply_discard_selection(
        state,
        candidates,
        tm_selection,
    ).after
    tm_discard_exec = TrainerSearchExecutionState(
        zones=after_tm_discard,
        budget=TurnActionBudget(supporter_play_limit=1),
    )
    tm_individually_reachable = shortest_bounded_plan(
        tm_discard_exec,
        (arven_action, colress_action),
        lambda current: current.zones.count(TM_EVOLUTION, "hand") >= 1,
        max_depth=1,
    )
    jet_individually_reachable = shortest_bounded_plan(
        tm_discard_exec,
        (arven_action, colress_action),
        lambda current: current.zones.count(JET_ENERGY, "hand") >= 1,
        max_depth=1,
    )
    joint_reachable = shortest_bounded_plan(
        tm_discard_exec,
        (arven_action, colress_action),
        goal,
        max_depth=2,
    )
    assert tm_individually_reachable is not None
    assert jet_individually_reachable is not None
    assert joint_reachable is None

    print(
        json.dumps(
            {
                "one_supporter_separate_search_safe_discards": one_supporter_separate,
                "two_supporters_separate_search_safe_discards": two_supporters_separate,
                "one_supporter_with_multi_axis_gnh_safe_discards": one_supporter_multi_axis,
                "after_tm_discard_tm_individually_reachable": True,
                "after_tm_discard_jet_individually_reachable": True,
                "after_tm_discard_joint_endpoint_reachable": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
