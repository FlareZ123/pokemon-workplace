"""Reproduce continuation-aware discard safety under Prize uncertainty."""

from __future__ import annotations

import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from belief_weighted_discard_policy import (  # noqa: E402
    discard_safety_under_belief,
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
from typed_search_target_allocator import (  # noqa: E402
    POKEMON_TOOL,
    TargetGroup,
)


FODDER = "fodder"
TM_EVOLUTION = "tm_evolution"
ARVEN = "arven"
REPLACEMENT_GROUP = "replacement_tm"


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def selection_name(
    candidates: tuple[DiscardCandidate, ...],
    selection: DiscardSelection,
) -> str:
    selected = [
        candidate.card_class
        for candidate, count in zip(candidates, selection.counts, strict=True)
        for _ in range(count)
    ]
    if len(selected) != 1:
        raise AssertionError(f"expected one-card selection, got {selected!r}")
    return selected[0]


def state_factory(replacement_copies: int):
    def build(prize_counts):
        prized = prize_counts[REPLACEMENT_GROUP]
        deck = replacement_copies - prized
        if deck < 0:
            raise ValueError("belief prizes more replacements than exist")

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


def arven_continuation(
    profile,
    candidates: tuple[DiscardCandidate, ...],
):
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

        execution = TrainerSearchExecutionState(zones=after_discard)
        try:
            transaction = execute_trainer_retrieval_transaction(
                execution,
                profile=profile,
                action_card_class=ARVEN,
                targets=(target,),
                retrieval_action=matches[0],
            )
        except ValueError:
            return
        yield ("Arven restores TM Evolution", transaction.after.zones)

    return generate


def safety_by_name(
    belief,
    replacement_copies,
    arven,
    candidates,
):
    rows = discard_safety_under_belief(
        belief,
        state_factory(replacement_copies),
        candidates,
        1,
        arven_continuation(arven, candidates),
        {TM_EVOLUTION: 1},
    )
    return {
        selection_name(candidates, row.selection): row.safety_probability
        for row in rows
    }


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
    one_k0_safety = safety_by_name(
        one_k0,
        1,
        arven,
        candidates,
    )
    expected_one = comb(52, 6) / comb(53, 6)
    assert abs(one_k0_safety[FODDER] - 1.0) < 1e-12
    assert abs(one_k0_safety[TM_EVOLUTION] - expected_one) < 1e-12

    one_k1_unprized = PrizeBelief.from_exact(
        {REPLACEMENT_GROUP: 0},
        prize_count=6,
    )
    one_k1_unprized_safety = safety_by_name(
        one_k1_unprized,
        1,
        arven,
        candidates,
    )
    assert one_k1_unprized_safety[FODDER] == 1.0
    assert one_k1_unprized_safety[TM_EVOLUTION] == 1.0

    one_k1_prized = PrizeBelief.from_exact(
        {REPLACEMENT_GROUP: 1},
        prize_count=6,
    )
    one_k1_prized_safety = safety_by_name(
        one_k1_prized,
        1,
        arven,
        candidates,
    )
    assert one_k1_prized_safety[FODDER] == 1.0
    assert one_k1_prized_safety[TM_EVOLUTION] == 0.0

    two_k0 = PrizeBelief.from_hypergeometric(
        {REPLACEMENT_GROUP: 2},
        pool_size=53,
        prize_count=6,
    )
    two_k0_safety = safety_by_name(
        two_k0,
        2,
        arven,
        candidates,
    )
    expected_two = 1.0 - comb(2, 2) * comb(51, 4) / comb(53, 6)
    assert abs(two_k0_safety[FODDER] - 1.0) < 1e-12
    assert abs(two_k0_safety[TM_EVOLUTION] - expected_two) < 1e-12
    assert two_k0_safety[TM_EVOLUTION] > one_k0_safety[TM_EVOLUTION]

    print(
        json.dumps(
            {
                "one_replacement_k0": one_k0_safety,
                "one_replacement_k1_unprized": one_k1_unprized_safety,
                "one_replacement_k1_prized": one_k1_prized_safety,
                "two_replacements_k0": two_k0_safety,
                "one_replacement_tm_safety_expected": expected_one,
                "two_replacement_tm_safety_expected": expected_two,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
