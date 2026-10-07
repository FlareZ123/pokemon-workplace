"""Reproduce value of exact Prize information before a discard deadline."""

from __future__ import annotations

import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from belief_discard_decision import (  # noqa: E402
    evaluate_discard_decision_under_belief,
)
from discard_cost_witness import (  # noqa: E402
    DiscardCandidate,
    DiscardSelection,
    apply_discard_selection,
)
from multicopy_zone_state import ZoneCountState  # noqa: E402
from prize_belief_kernel import PrizeBelief  # noqa: E402
from search_zone_transition import SearchZoneTarget  # noqa: E402
from trainer_search_profile_compiler import (  # noqa: E402
    compile_multi_output_trainer_profiles,
)
from trainer_search_transaction import (  # noqa: E402
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
)
from typed_search_retrieval import (  # noqa: E402
    enumerate_typed_retrieval_actions,
)
from typed_search_target_allocator import POKEMON_TOOL, TargetGroup  # noqa: E402


FODDER = "fodder"
TM_EVOLUTION = "tm_evolution"
ARVEN = "arven"
REPLACEMENT_GROUP = "replacement_tm"


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def state_factory(replacement_copies: int):
    def build(prize_counts):
        prized = prize_counts[REPLACEMENT_GROUP]
        deck = replacement_copies - prized
        counts = {
            (FODDER, "hand"): 1,
            (TM_EVOLUTION, "hand"): 1,
            (ARVEN, "hand"): 1,
        }
        if deck:
            counts[(TM_EVOLUTION, "deck")] = deck
        if prized:
            counts[(TM_EVOLUTION, "prize")] = prized
        return ZoneCountState.from_mapping(counts)

    return build


def arven_continuation(profile, candidates):
    def generate(state: ZoneCountState, selection: DiscardSelection):
        after_discard = apply_discard_selection(
            state,
            candidates,
            selection,
        ).after
        yield ("after discard", after_discard)

        copies = after_discard.count(TM_EVOLUTION, "deck")
        if copies <= 0:
            return

        target = SearchZoneTarget(
            TM_EVOLUTION,
            TargetGroup(
                "Replacement TM Evolution",
                copies,
                frozenset({POKEMON_TOOL}),
            ),
        )
        actions = enumerate_typed_retrieval_actions(
            profile.base_outputs,
            (target.group,),
        )
        matches = [
            action
            for action in actions
            if action.target_cost == (1,)
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"expected one Arven TM retrieval, found {len(matches)}"
            )
        transaction = execute_trainer_retrieval_transaction(
            TrainerSearchExecutionState(zones=after_discard),
            profile=profile,
            action_card_class=ARVEN,
            targets=(target,),
            retrieval_action=matches[0],
        )
        yield ("Arven restores TM Evolution", transaction.after.zones)

    return generate


def selection_name(candidates, selection):
    chosen = [
        candidate.card_class
        for candidate, amount in zip(candidates, selection.counts, strict=True)
        for _ in range(amount)
    ]
    if len(chosen) != 1:
        raise AssertionError(chosen)
    return chosen[0]


def utility(candidates):
    def score(selection: DiscardSelection, endpoint_safe: bool) -> float:
        name = selection_name(candidates, selection)
        if not endpoint_safe:
            return 0.0
        if name == FODDER:
            return 0.9
        if name == TM_EVOLUTION:
            return 1.0
        raise AssertionError(name)

    return score


def named_values(candidates, decision):
    return {
        selection_name(candidates, selection): value
        for selection, value in decision.fixed_selection_values
    }


def evaluate(belief, replacement_copies, arven, candidates):
    return evaluate_discard_decision_under_belief(
        belief,
        state_factory(replacement_copies),
        candidates,
        1,
        arven_continuation(arven, candidates),
        {TM_EVOLUTION: 1},
        utility(candidates),
    )


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    arven = representative(profiles, "Arven")
    candidates = (
        DiscardCandidate(FODDER),
        DiscardCandidate(TM_EVOLUTION),
    )

    one_k0 = PrizeBelief.from_hypergeometric(
        {REPLACEMENT_GROUP: 1},
        pool_size=53,
        prize_count=6,
    )
    one_decision = evaluate(one_k0, 1, arven, candidates)
    one_values = named_values(candidates, one_decision)
    p_one = comb(52, 6) / comb(53, 6)
    expected_one_exact = p_one * 1.0 + (1.0 - p_one) * 0.9

    assert abs(one_values[FODDER] - 0.9) < 1e-12
    assert abs(one_values[TM_EVOLUTION] - p_one) < 1e-12
    assert selection_name(
        candidates,
        one_decision.best_fixed_selection,
    ) == FODDER
    assert abs(one_decision.fixed_value - 0.9) < 1e-12
    assert abs(
        one_decision.exact_information_value - expected_one_exact
    ) < 1e-12
    assert abs(
        one_decision.value_of_exact_information
        - (expected_one_exact - 0.9)
    ) < 1e-12

    k1_unprized = evaluate(
        PrizeBelief.from_exact(
            {REPLACEMENT_GROUP: 0},
            prize_count=6,
        ),
        1,
        arven,
        candidates,
    )
    assert selection_name(
        candidates,
        k1_unprized.best_fixed_selection,
    ) == TM_EVOLUTION
    assert k1_unprized.fixed_value == 1.0
    assert abs(k1_unprized.value_of_exact_information) < 1e-12

    k1_prized = evaluate(
        PrizeBelief.from_exact(
            {REPLACEMENT_GROUP: 1},
            prize_count=6,
        ),
        1,
        arven,
        candidates,
    )
    assert selection_name(
        candidates,
        k1_prized.best_fixed_selection,
    ) == FODDER
    assert k1_prized.fixed_value == 0.9
    assert abs(k1_prized.value_of_exact_information) < 1e-12

    two_k0 = PrizeBelief.from_hypergeometric(
        {REPLACEMENT_GROUP: 2},
        pool_size=53,
        prize_count=6,
    )
    two_decision = evaluate(two_k0, 2, arven, candidates)
    two_values = named_values(candidates, two_decision)
    p_two = 1.0 - comb(2, 2) * comb(51, 4) / comb(53, 6)
    expected_two_exact = p_two * 1.0 + (1.0 - p_two) * 0.9

    assert abs(two_values[FODDER] - 0.9) < 1e-12
    assert abs(two_values[TM_EVOLUTION] - p_two) < 1e-12
    assert selection_name(
        candidates,
        two_decision.best_fixed_selection,
    ) == TM_EVOLUTION
    assert abs(two_decision.fixed_value - p_two) < 1e-12
    assert abs(
        two_decision.exact_information_value - expected_two_exact
    ) < 1e-12
    assert two_decision.value_of_exact_information < one_decision.value_of_exact_information

    print(
        json.dumps(
            {
                "one_replacement_k0": {
                    "fixed_values": one_values,
                    "best_fixed": selection_name(
                        candidates,
                        one_decision.best_fixed_selection,
                    ),
                    "fixed_value": one_decision.fixed_value,
                    "perfect_information_value": one_decision.exact_information_value,
                    "value_of_information": one_decision.value_of_exact_information,
                },
                "one_replacement_k1_unprized_best": selection_name(
                    candidates,
                    k1_unprized.best_fixed_selection,
                ),
                "one_replacement_k1_prized_best": selection_name(
                    candidates,
                    k1_prized.best_fixed_selection,
                ),
                "two_replacements_k0": {
                    "fixed_values": two_values,
                    "best_fixed": selection_name(
                        candidates,
                        two_decision.best_fixed_selection,
                    ),
                    "fixed_value": two_decision.fixed_value,
                    "perfect_information_value": two_decision.exact_information_value,
                    "value_of_information": two_decision.value_of_exact_information,
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
