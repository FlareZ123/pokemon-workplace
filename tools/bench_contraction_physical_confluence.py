"""Confluence of pure staged Bench contractions with exact physical-card ledgers.

A contraction from n to a then b has C(n,a)*C(a,b) histories, but
C(n,b) terminal physical states if no actions intervene and all discarded
Pokémon stacks and attachments use the same destinations. Verify that this
projection is exact in the existing stack-bearing conservation engine.
"""

from __future__ import annotations

import argparse
import json
import unittest
from collections import Counter
from dataclasses import dataclass
from math import comb

from bench_contraction_batch_conservation import (
    enumerate_contractions,
    materialized_fixture,
)
from identity_materialization import assert_conserved
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class ConfluenceCensus:
    starting_occupancy: int
    intermediate_capacity: int
    final_capacity: int
    staged_paths: int
    final_states: int
    paths_per_final: int


def census(
    start: StackBoardMaterialState,
    *,
    intermediate_capacity: int,
    final_capacity: int,
) -> ConfluenceCensus:
    """Check exact physical equality of every staged path and direct target."""
    if start.board is None:
        raise ValueError("expected a nonterminal physical board")
    n = len(start.board.bench_ids)
    a, b = intermediate_capacity, final_capacity
    if not 0 <= b <= a <= n:
        raise ValueError("expected 0 <= final <= intermediate <= occupancy")

    direct = {
        outcome.state.board.bench_ids: outcome.state
        for outcome in enumerate_contractions(start, b)
    }
    assert len(direct) == comb(n, b)

    multiplicities: Counter[tuple[str, ...]] = Counter()
    for first in enumerate_contractions(start, a):
        for second in enumerate_contractions(first.state, b):
            final_state = second.state
            assert final_state.board is not None
            survivors = final_state.board.bench_ids
            assert survivors in direct
            # This compares the entire physical board and its full identity
            # ledger, including stack cards, attachments and discard counts.
            assert final_state == direct[survivors]
            assert_conserved(start.ledger, final_state.ledger)
            multiplicities[survivors] += 1

    expected_paths = comb(n, a) * comb(a, b)
    expected_multiplicity = comb(n - b, a - b)
    assert sum(multiplicities.values()) == expected_paths
    assert set(multiplicities) == set(direct)
    assert all(count == expected_multiplicity for count in multiplicities.values())

    return ConfluenceCensus(
        starting_occupancy=n,
        intermediate_capacity=a,
        final_capacity=b,
        staged_paths=expected_paths,
        final_states=len(direct),
        paths_per_final=expected_multiplicity,
    )


class BenchConfluenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.initial, self.state = materialized_fixture()

    def test_every_descending_pair_from_five(self) -> None:
        # Covers 21 different capacity pairs, including 0 and equal capacities.
        for a in range(6):
            for b in range(a + 1):
                with self.subTest(a=a, b=b):
                    result = census(
                        self.state,
                        intermediate_capacity=a,
                        final_capacity=b,
                    )
                    self.assertEqual(result.staged_paths, comb(5, a) * comb(a, b))
                    self.assertEqual(result.final_states, comb(5, b))

    def test_evolved_stack_and_attachments_survive_path_merging(self) -> None:
        result = census(
            self.state,
            intermediate_capacity=4,
            final_capacity=3,
        )
        self.assertEqual((result.staged_paths, result.final_states,
                          result.paths_per_final), (20, 10, 2))
        target = next(
            x for x in enumerate_contractions(self.state, 3)
            if "pair-a" not in x.state.board.bench_ids
        )
        for card_class in (
            "tarountula", "spidops", "grass-energy", "muscle-band"
        ):
            self.assertEqual(
                target.state.ledger.exchangeable.count(card_class, "discard"),
                1,
            )
        assert_conserved(self.initial, target.state.ledger)

    def test_expanding_after_discard_does_not_resurrect_pokemon(self) -> None:
        first = next(
            x for x in enumerate_contractions(self.state, 4)
            if x.discarded_pokemon_ids == ("pair-a",)
        )
        expanded = enumerate_contractions(first.state, 5)
        self.assertEqual(len(expanded), 1)
        final = expanded[0].state
        self.assertEqual(len(final.board.bench_ids), 4)
        self.assertEqual(final.board.bench_capacity, 5)
        self.assertNotEqual(final, self.state)
        self.assertEqual(final.ledger.exchangeable.count("spidops", "discard"), 1)
        assert_conserved(self.initial, final.ledger)

    def test_invalid_capacity_order_rejected(self) -> None:
        with self.assertRaises(ValueError):
            census(self.state, intermediate_capacity=3, final_capacity=4)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_contraction_physical_confluence"], verbosity=2)
        return
    _initial, state = materialized_fixture()
    print(json.dumps([
        census(state, intermediate_capacity=a, final_capacity=b).__dict__
        for a, b in ((4, 3), (5, 3), (3, 2))
    ], indent=2))


if __name__ == "__main__":
    main()
