"""Enumerate every legal survivor set of a Bench-capacity contraction.

This is a physical choice-space kernel. It leaves strategy to the caller,
preserves full board objects and does not conflate forced discards with Knock Outs.
"""
from __future__ import annotations

import argparse
import json
import unittest
from dataclasses import dataclass, replace
from itertools import combinations
from typing import Iterator

from bench_synergy_contraction import PairBonus, utility
from board_object_kernel import (
    BoardPokemon, BoardState, contract_bench, make_board, make_pokemon,
)


@dataclass(frozen=True)
class ContractionChoice:
    board: BoardState
    discarded: tuple[BoardPokemon, ...]


def contraction_choices(state: BoardState, new_capacity: int) -> Iterator[ContractionChoice]:
    """Yield all exact legal choices of which Benched Pokémon leave play."""
    state.validate()
    if new_capacity < 0:
        raise ValueError("Bench capacity cannot be negative")
    keep_count = min(new_capacity, len(state.bench_ids))
    for kept in combinations(state.bench_ids, keep_count):
        kept_ids = set(kept)
        removed_ids = set(state.bench_ids) - kept_ids
        after = replace(
            state,
            bench_capacity=new_capacity,
            bench_ids=kept,
            objects=tuple(
                occupant for occupant in state.objects
                if occupant.object_id not in removed_ids
            ),
        )
        after.validate()
        removed = tuple(
            state.get(object_id) for object_id in state.bench_ids
            if object_id in removed_ids
        )
        yield ContractionChoice(after, removed)


def score_choice(choice: ContractionChoice, pairs: tuple[PairBonus, ...]) -> int:
    values = {
        p.object_id: int(p.retention_value) for p in choice.board.objects
    }
    return utility(choice.board.bench_ids, values, pairs)


def synergy_best(
    state: BoardState, new_capacity: int, pairs: tuple[PairBonus, ...]
) -> ContractionChoice:
    return max(
        contraction_choices(state, new_capacity),
        key=lambda option: (
            score_choice(option, pairs),
            option.board.bench_ids,
        ),
    )


def physical_fixture() -> BoardState:
    active = make_pokemon("X", "Bidoof")
    bench = (
        make_pokemon("E", "Primary attacker", retention_value=100),
        make_pokemon("A", "Lunatone", print_id="me1-74", retention_value=0),
        make_pokemon("B", "Solrock", print_id="pgo-39", retention_value=0),
        make_pokemon("C", "Second attacker", retention_value=22),
        make_pokemon("D", "Alternative attacker", retention_value=20),
    )
    return make_board(active, bench, bench_capacity=5)


PAIR = (PairBonus("A", "B", 30),)


class ContractionChoiceTests(unittest.TestCase):
    def test_complete_five_to_four_and_three_choice_counts(self) -> None:
        state = physical_fixture()
        self.assertEqual(len(list(contraction_choices(state, 4))), 5)
        self.assertEqual(len(list(contraction_choices(state, 3))), 10)
        for choice in contraction_choices(state, 4):
            self.assertEqual(len(choice.discarded), 1)
            self.assertEqual(len(choice.board.bench_ids), 4)
            self.assertEqual(len(choice.board.objects), 5)
            self.assertEqual(choice.board.active_id, "X")

    def test_joint_value_changes_discard_vs_additive_default(self) -> None:
        state = physical_fixture()
        default_after, default_removed = contract_bench(state, new_capacity=4)
        self.assertIn(default_removed[0].object_id, {"A", "B"})
        self.assertFalse({"A", "B"}.issubset(default_after.bench_ids))
        joint = synergy_best(state, 4, PAIR)
        self.assertEqual(tuple(p.object_id for p in joint.discarded), ("D",))
        self.assertEqual(set(joint.board.bench_ids), {"E", "A", "B", "C"})
        self.assertEqual(score_choice(joint, PAIR), 152)

    def test_nonnested_two_stage_physical_transition(self) -> None:
        original = physical_fixture()
        first = synergy_best(original, 4, PAIR)
        second = synergy_best(first.board, 3, PAIR)
        direct = synergy_best(original, 3, PAIR)
        self.assertEqual(score_choice(second, PAIR), 130)
        self.assertEqual(score_choice(direct, PAIR), 142)
        self.assertEqual(set(second.board.bench_ids), {"E", "A", "B"})
        self.assertEqual(set(direct.board.bench_ids), {"E", "C", "D"})

    def test_exact_small_choice_counts_and_conservation(self) -> None:
        original = physical_fixture()
        all_ids = {p.object_id for p in original.objects}
        for capacity, expected in ((0, 1), (1, 5), (2, 10), (3, 10), (4, 5), (5, 1), (8, 1)):
            choices = list(contraction_choices(original, capacity))
            self.assertEqual(len(choices), expected)
            for outcome in choices:
                held_ids = {p.object_id for p in outcome.board.objects}
                gone_ids = {p.object_id for p in outcome.discarded}
                self.assertEqual(held_ids | gone_ids, all_ids)
                self.assertFalse(held_ids & gone_ids)

    def test_does_not_trigger_prize_or_knock_out(self) -> None:
        original = physical_fixture()
        alternative = next(
            choice for choice in contraction_choices(original, 4)
            if choice.discarded[0].object_id == "D"
        )
        self.assertEqual(alternative.discarded[0].card_name, "Alternative attacker")
        self.assertNotIn("D", alternative.board.bench_ids)
        self.assertEqual(alternative.board.get("E").retention_value, 100)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_contraction_choice_space"], verbosity=2)
    else:
        starting = physical_fixture()
        additive_after, additive_discards = contract_bench(starting, new_capacity=4)
        joint = synergy_best(starting, 4, PAIR)
        print(json.dumps({
            "legal_choices_5_to_4": len(list(contraction_choices(starting, 4))),
            "additive_discards": [p.object_id for p in additive_discards],
            "additive_keeping": list(additive_after.bench_ids),
            "joint_discards": [p.object_id for p in joint.discarded],
            "joint_keeping": list(joint.board.bench_ids),
            "joint_utility": score_choice(joint, PAIR),
        }, indent=2))


if __name__ == "__main__":
    main()
