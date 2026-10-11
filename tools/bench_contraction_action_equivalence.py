"""Exact action-sensitive equivalence classes for staged Bench contractions.

Five distinct Benched objects; Lunar Cycle requires two named in-play
Pokémon. Enumerate pure-contraction histories and optional use of one
printed ability in the intermediate state, then quotient by full physical
terminal state. This is a finite controlled model, not a full turn engine.
"""

from __future__ import annotations

import argparse
import json
import unittest
from collections import Counter
from dataclasses import dataclass

from bench_contraction_batch_conservation import (
    contract_with_choice,
    enumerate_contractions,
)
from bench_contraction_intermediate_action import (
    print_specific_fixture,
    use_lunar_cycle_once,
)
from identity_materialization import assert_conserved
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class EquivalenceCensus:
    staged_discard_histories: int
    histories_including_optional_action_branch: int
    distinct_terminal_survivor_sets: int
    distinct_terminal_physical_states: int
    early_available_late_available: int
    early_available_late_unavailable: int
    early_unavailable_late_unavailable: int


def can_use_cycle(state: StackBoardMaterialState) -> bool:
    if state.board is None:
        return False
    live = {
        card.card_class
        for card in state.ledger.instances
        if card.zone == "in_play"
    }
    return (
        "me1-74" in live
        and "pgo-39" in live
        and state.ledger.exchangeable.count("basic-fighting-energy", "hand") >= 1
        and state.ledger.exchangeable.count("non-target-card", "deck") >= 3
    )


def census() -> EquivalenceCensus:
    start = print_specific_fixture()
    assert start.board is not None
    direct = {
        item.state.board.bench_ids: item.state
        for item in enumerate_contractions(start, 3)
    }
    terminal: dict[
        tuple[tuple[str, ...], object],
        StackBoardMaterialState,
    ] = {}
    multiplicities: Counter[tuple[tuple[str, ...], object]] = Counter()
    type_counts: Counter[str] = Counter()
    histories = 0
    branched = 0

    for first in enumerate_contractions(start, 4):
        available_early = can_use_cycle(first.state)
        for second in enumerate_contractions(first.state, 3):
            histories += 1
            final_bench = second.state.board.bench_ids
            direct_state = direct[final_bench]
            available_late = can_use_cycle(direct_state)
            assert not available_late or available_early
            if available_early and available_late:
                category = "early_and_late"
            elif available_early:
                category = "early_only"
            else:
                category = "neither"
            type_counts[category] += 1

            # The printed Ability says 'may'. Every eligible intermediate
            # history has both the skip and use continuations.
            branches = (False, True) if available_early else (False,)
            branched += len(branches)
            for apply in branches:
                if apply:
                    after_first = use_lunar_cycle_once(first.state)
                    final = contract_with_choice(
                        after_first,
                        new_capacity=3,
                        discard_pokemon_ids=second.discarded_pokemon_ids,
                    )
                    assert final is not None
                    state = final.state
                    if available_late:
                        # Commuting case: action remains available after
                        # direct contraction, and its final effect agrees.
                        assert state == use_lunar_cycle_once(direct_state)
                    else:
                        assert state.board == direct_state.board
                        assert state.ledger != direct_state.ledger
                else:
                    state = second.state
                    assert state == direct_state
                assert_conserved(start.ledger, state.ledger)
                assert state.board is not None
                key = (
                    state.board.bench_ids,
                    state.ledger.exchangeable,
                )
                if key in terminal:
                    assert terminal[key] == state
                else:
                    terminal[key] = state
                multiplicities[key] += 1

    assert histories == 20
    assert branched == 32
    assert len(direct) == 10
    assert len(terminal) == 19
    assert len({key[0] for key in terminal}) == 10
    assert type_counts == {
        "early_and_late": 6,
        "early_only": 6,
        "neither": 8,
    }
    assert sum(multiplicities.values()) == 32

    # All three survivor sets retaining both partners have 2 physical
    # endpoints; all six with only one have 2; the one retaining neither
    # has 1. This yields 9*2+1 = 19 physical endpoints.
    endpoints_by_bench: Counter[tuple[str, ...]] = Counter(
        key[0] for key in terminal
    )
    assert Counter(endpoints_by_bench.values()) == {2: 9, 1: 1}
    return EquivalenceCensus(
        staged_discard_histories=histories,
        histories_including_optional_action_branch=branched,
        distinct_terminal_survivor_sets=len(direct),
        distinct_terminal_physical_states=len(terminal),
        early_available_late_available=type_counts["early_and_late"],
        early_available_late_unavailable=type_counts["early_only"],
        early_unavailable_late_unavailable=type_counts["neither"],
    )


class EquivalenceTests(unittest.TestCase):
    def test_optional_action_expands_exact_quotient(self) -> None:
        r = census()
        self.assertEqual(r.distinct_terminal_physical_states, 19)
        self.assertEqual(r.histories_including_optional_action_branch, 32)

    def test_all_counts_add_up(self) -> None:
        r = census()
        self.assertEqual(
            r.early_available_late_available
            + r.early_available_late_unavailable
            + r.early_unavailable_late_unavailable,
            r.staged_discard_histories,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        unittest.main(argv=["bench_contraction_action_equivalence"], verbosity=2)
    else:
        print(json.dumps(census().__dict__, indent=2))


if __name__ == "__main__":
    main()
