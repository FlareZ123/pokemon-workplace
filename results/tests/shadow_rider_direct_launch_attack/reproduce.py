"""Independent labeled-card oracle for direct Radiant launch and Max Geist."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction
from itertools import combinations, permutations
from math import comb, factorial
from pathlib import Path

from tools.shadow_rider_direct_launch_attack import COUNTS, exact_direct


def physical_oracle(counts: tuple[int, ...], *, opening: int = 3, prizes: int = 1,
                    cost: int = 3) -> tuple[Fraction, Fraction, Fraction]:
    cards = [category for category, count in enumerate(counts) for _ in range(count)]
    n = len(cards)
    ids = tuple(range(n))
    launched, ready, float_ready = 0, 0, 0
    for opener in combinations(ids, opening):
        if not any(cards[i] in (0, 1) for i in opener):
            continue
        if not any(cards[i] == 1 for i in opener):
            continue
        unseen = [i for i in ids if i not in opener]
        for prize in combinations(unseen, prizes):
            spared = [i for i in unseen if i not in prize]
            for first in spared:
                if not any(cards[i] == 0 for i in opener) and cards[first] != 0:
                    continue
                remaining = [i for i in spared if i != first]
                vmax = [i for i in remaining if cards[i] == 2]
                if len(vmax) < 2:
                    continue
                # All VMAX in this narrow card-class model have identical properties.
                after_launch = [i for i in remaining if i not in vmax[:2]]
                for second in after_launch:
                    rest = [i for i in after_launch if i != second]
                    for order in permutations(rest):
                        launched += 1
                        hand_energy = sum(cards[i] == 3 for i in (*opener, first, second))
                        hand_float = sum(cards[i] == 4 for i in (*opener, first, second))
                        attached = 0
                        offset = 0
                        for _ in range(2):
                            if hand_energy == 0:
                                continue
                            hand_energy -= 1
                            attached += 1
                            drawn = order[offset:offset + 2]
                            hand_energy += sum(cards[i] == 3 for i in drawn)
                            hand_float += sum(cards[i] == 4 for i in drawn)
                            offset += len(drawn)
                        if attached + int(hand_energy > 0) >= cost:
                            ready += 1
                            if hand_float:
                                float_ready += 1
    accepted = comb(n, opening) - comb(n - counts[0] - counts[1], opening)
    denominator = (
        accepted * comb(n - opening, prizes) * (n - opening - prizes)
        * (n - opening - prizes - 3) * factorial(n - opening - prizes - 4)
    )
    return tuple(Fraction(x, denominator) for x in (launched, ready, float_ready))


class DirectLaunchTests(unittest.TestCase):
    def test_baseline_and_exact_fractions(self) -> None:
        self.assertEqual(sum(COUNTS), 60)
        normal = exact_direct(attack_cost=3)
        self.assertEqual(normal.launch, Fraction(2431309737, 20230837760))
        self.assertEqual(normal.ready, Fraction(65620165128879, 1472675511566336))
        self.assertEqual(normal.ready_and_float, Fraction(70767776772269, 9204221947289600))
        reduced = exact_direct(attack_cost=2)
        self.assertEqual(reduced.launch, normal.launch)
        self.assertEqual(reduced.ready, Fraction(2919538623833, 41837372487680))
        self.assertEqual(reduced.ready_and_float, Fraction(43117466834961, 3346989799014400))
        self.assertTrue(0 < normal.ready_and_float < normal.ready < normal.launch < 1)

    def test_independent_physical_toys(self) -> None:
        for counts in ((1, 2, 2, 2, 1, 2), (1, 2, 3, 2, 1, 2),
                       (1, 1, 2, 3, 1, 2), (1, 3, 2, 1, 1, 2)):
            for cost in (2, 3):
                result = exact_direct(counts=counts, opening=3, prizes=1, attack_cost=cost)
                self.assertEqual(
                    (result.launch, result.ready, result.ready_and_float),
                    physical_oracle(counts, cost=cost),
                    (counts, cost),
                )

    def test_source_deck_counts(self) -> None:
        root = Path(__file__).resolve().parents[3]
        text = (root / "results" / "decks" / "shadow-rider-calyrex" / "README.md").read_text(encoding="utf-8")
        for line in (
            "| 1 | Radiant Eternatus |", "| 4 | Shadow Rider Calyrex VMAX |",
            "| 1 | Float Stone |", "| 11 | Basic Psychic Energy |",
        ):
            self.assertIn(line, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
