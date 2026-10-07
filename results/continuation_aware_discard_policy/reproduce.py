"""Reproduce look-ahead discard legality from exact future Trainer continuations."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from continuation_discard_policy import (
    continuation_feasible_discards,
    feasible_selections,
    rank_continuation_discards,
)
from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
)
from typed_search_retrieval import enumerate_typed_retrieval_actions
from typed_search_target_allocator import (
    ITEM,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
    SUPPORTER,
    TargetGroup,
)

SECRET_BOX = "secret_box"
FILLER = "initial_filler"
TAG_CALL = "tag_call"
TM_EVOLUTION = "tm_evolution"
GUZMA_HALA = "guzma_hala"
ARTAZON = "artazon"
JET_ENERGY = "jet_energy"


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def action_for_cost(profile, targets, target_cost):
    actions = enumerate_typed_retrieval_actions(
        profile.base_outputs + profile.conditional_outputs,
        tuple(target.group for target in targets),
    )
    matches = [action for action in actions if action.target_cost == target_cost]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one retrieval for {target_cost}, found {len(matches)}"
        )
    return matches[0]


def selection_classes(
    candidates: tuple[DiscardCandidate, ...],
    selection: DiscardSelection,
) -> tuple[str, ...]:
    return tuple(
        candidate.card_class
        for candidate, amount in zip(candidates, selection.counts, strict=True)
        for _ in range(amount)
    )


def after_secret_box(
    secret_box_profile,
    *,
    tm_copies: int,
    artazon_copies: int,
) -> TrainerSearchExecutionState:
    if tm_copies < 1 or artazon_copies < 1:
        raise ValueError("Secret Box witness needs at least one TM and Artazon")

    targets = (
        SearchZoneTarget(
            TAG_CALL,
            TargetGroup("Tag Call", 1, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            TM_EVOLUTION,
            TargetGroup("TM Evolution", tm_copies, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            GUZMA_HALA,
            TargetGroup("Guzma & Hala", 1, frozenset({SUPPORTER})),
        ),
        SearchZoneTarget(
            ARTAZON,
            TargetGroup("Artazon", artazon_copies, frozenset({STADIUM})),
        ),
    )
    action = action_for_cost(secret_box_profile, targets, (1, 1, 1, 1))
    initial = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                (SECRET_BOX, "hand"): 1,
                (FILLER, "hand"): 3,
                (TAG_CALL, "deck"): 1,
                (TM_EVOLUTION, "deck"): tm_copies,
                (GUZMA_HALA, "deck"): 1,
                (ARTAZON, "deck"): artazon_copies,
                (JET_ENERGY, "deck"): 2,
            }
        )
    )
    candidates = (DiscardCandidate(FILLER),)
    selections = enumerate_discard_selections(initial.zones, candidates, 3)
    assert len(selections) == 1

    transaction = execute_trainer_retrieval_transaction(
        initial,
        profile=secret_box_profile,
        action_card_class=SECRET_BOX,
        targets=targets,
        retrieval_action=action,
        discard_candidates=candidates,
        discard_selection=selections[0],
    )
    return transaction.after


def gnh_continuation(
    guzma_hala_profile,
    execution_template: TrainerSearchExecutionState,
    candidates: tuple[DiscardCandidate, ...],
):
    """Enumerate every exact G&H retrieval after one chosen discard witness."""

    def generate(state: ZoneCountState, selection: DiscardSelection):
        if state != execution_template.zones:
            raise ValueError("continuation state disagrees with execution template")

        targets = (
            SearchZoneTarget(
                ARTAZON,
                TargetGroup(
                    "Remaining Artazon",
                    state.count(ARTAZON, "deck"),
                    frozenset({STADIUM}),
                ),
            ),
            SearchZoneTarget(
                TM_EVOLUTION,
                TargetGroup(
                    "Remaining TM Evolution",
                    state.count(TM_EVOLUTION, "deck"),
                    frozenset({POKEMON_TOOL}),
                ),
            ),
            SearchZoneTarget(
                JET_ENERGY,
                TargetGroup(
                    "Jet Energy",
                    state.count(JET_ENERGY, "deck"),
                    frozenset({SPECIAL_ENERGY}),
                ),
            ),
        )
        actions = enumerate_typed_retrieval_actions(
            guzma_hala_profile.base_outputs
            + guzma_hala_profile.conditional_outputs,
            tuple(target.group for target in targets),
        )
        current = TrainerSearchExecutionState(
            zones=state,
            budget=execution_template.budget,
            channels=execution_template.channels,
        )
        for action in actions:
            try:
                transaction = execute_trainer_retrieval_transaction(
                    current,
                    profile=guzma_hala_profile,
                    action_card_class=GUZMA_HALA,
                    targets=targets,
                    retrieval_action=action,
                    discard_candidates=candidates,
                    discard_selection=selection,
                    pay_optional_discard=True,
                )
            except ValueError:
                continue
            yield (
                f"gnh_target_cost={action.target_cost}",
                transaction.after.zones,
            )

    return generate


def feasible_class_pairs(
    secret_box_profile,
    guzma_hala_profile,
    *,
    tm_copies: int,
    artazon_copies: int,
    require_tag_call: bool = False,
):
    box_state = after_secret_box(
        secret_box_profile,
        tm_copies=tm_copies,
        artazon_copies=artazon_copies,
    )
    candidates = (
        DiscardCandidate(TAG_CALL),
        DiscardCandidate(TM_EVOLUTION),
        DiscardCandidate(ARTAZON),
    )
    requirements = {
        TM_EVOLUTION: 1,
        ARTAZON: 1,
        JET_ENERGY: 1,
    }
    if require_tag_call:
        requirements[TAG_CALL] = 1

    witnesses = continuation_feasible_discards(
        box_state.zones,
        candidates,
        2,
        gnh_continuation(guzma_hala_profile, box_state, candidates),
        requirements,
    )
    selections = feasible_selections(witnesses)
    pairs = tuple(
        sorted(
            selection_classes(candidates, selection)
            for selection in selections
        )
    )
    return candidates, witnesses, pairs


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    secret_box = representative(profiles, "Secret Box")
    guzma_hala = representative(profiles, "Guzma & Hala")

    both = feasible_class_pairs(
        secret_box, guzma_hala, tm_copies=2, artazon_copies=2
    )
    tm_only = feasible_class_pairs(
        secret_box, guzma_hala, tm_copies=2, artazon_copies=1
    )
    artazon_only = feasible_class_pairs(
        secret_box, guzma_hala, tm_copies=1, artazon_copies=2
    )
    neither = feasible_class_pairs(
        secret_box, guzma_hala, tm_copies=1, artazon_copies=1
    )
    tag_required = feasible_class_pairs(
        secret_box,
        guzma_hala,
        tm_copies=2,
        artazon_copies=2,
        require_tag_call=True,
    )

    assert both[2] == tuple(
        sorted(
            (
                (TAG_CALL, TM_EVOLUTION),
                (TAG_CALL, ARTAZON),
                (TM_EVOLUTION, ARTAZON),
            )
        )
    )
    assert tm_only[2] == ((TAG_CALL, TM_EVOLUTION),)
    assert artazon_only[2] == ((TAG_CALL, ARTAZON),)
    assert neither[2] == ()
    assert tag_required[2] == ((TM_EVOLUTION, ARTAZON),)

    scores = {
        TAG_CALL: 0.8,
        TM_EVOLUTION: 1.0,
        ARTAZON: 0.1,
    }
    ranked = rank_continuation_discards(both[1], both[0], scores)
    assert ranked
    best_pair = selection_classes(
        both[0],
        ranked[0].witness.selection,
    )
    assert best_pair == (TAG_CALL, TM_EVOLUTION)
    assert abs(ranked[0].desirability - 1.8) < 1e-12

    print(
        json.dumps(
            {
                "both_replacements_safe_pairs": both[2],
                "tm_only_safe_pairs": tm_only[2],
                "artazon_only_safe_pairs": artazon_only[2],
                "no_replacement_safe_pairs": neither[2],
                "tag_required_with_both_safe_pairs": tag_required[2],
                "best_dci_ranked_safe_pair": best_pair,
                "best_dci_score": ranked[0].desirability,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
