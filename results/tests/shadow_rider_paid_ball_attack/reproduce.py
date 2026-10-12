"""Independent physical-card oracle for Energy-paid launch and next-turn charge."""
from __future__ import annotations

import json
import unittest
from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations
from math import comb, factorial
from pathlib import Path

from tools.shadow_rider_paid_ball_attack import COUNTS, exact_paid


def physical_oracle(
    counts: tuple[int, int, int, int, int, int, int, int],
    *, opening: int = 3, prizes: int = 1,
) -> dict[str, tuple[Fraction, ...]]:
    """Classes Radiant, other Basics, VMAX, Psychic, Float, Ball, Valley, filler."""
    cards = [category for category, copies in enumerate(counts) for _ in range(copies)]
    n = len(cards)
    ids = tuple(range(n))
    sums = defaultdict(lambda: [0] * 6)
    for opener in combinations(ids, opening):
        if not any(cards[i] in (0, 1) for i in opener):
            continue
        if not any(cards[i] == 1 for i in opener):
            continue
        unobserved = [i for i in ids if i not in opener]
        for prize in combinations(unobserved, prizes):
            deck = [i for i in unobserved if i not in prize]
            for first in deck:
                hand = [*opener, first]
                available = [i for i in deck if i != first]
                if any(cards[i] == 0 for i in hand):
                    route = "direct"
                else:
                    route = "psychic_paid_ball"
                    radiant = next((i for i in available if cards[i] == 0), None)
                    ball = next((i for i in hand if cards[i] == 5), None)
                    energy = next((i for i in hand if cards[i] == 3), None)
                    if radiant is None or ball is None or energy is None:
                        continue
                    hand = [i for i in hand if i not in (ball, energy)]
                    available = [i for i in available if i != radiant]
                vmax = [i for i in available if cards[i] == 2]
                if len(vmax) < 2:
                    continue
                after_launch = [i for i in available if i not in vmax[:2]]
                for natural in after_launch:
                    remaining = [i for i in after_launch if i != natural]
                    for order in permutations(remaining):
                        he = sum(cards[i] == 3 for i in (*hand, natural))
                        hf = sum(cards[i] == 4 for i in (*hand, natural))
                        hs = sum(cards[i] == 6 for i in (*hand, natural))
                        cursor, attached = 0, 0
                        for _ in range(2):
                            if he == 0:
                                continue
                            he -= 1
                            attached += 1
                            drawn = order[cursor:cursor+2]
                            he += sum(cards[i] == 3 for i in drawn)
                            hf += sum(cards[i] == 4 for i in drawn)
                            hs += sum(cards[i] == 6 for i in drawn)
                            cursor += len(drawn)
                        total = attached+int(he > 0)
                        regular = total >= 3
                        valley = total >= 2 and hs > 0
                        outcomes = sums[route]
                        outcomes[0] += 1
                        outcomes[1] += int(regular)
                        outcomes[2] += int(regular and hf > 0)
                        outcomes[3] += int(valley and hf > 0)
                        outcomes[4] += int((regular or valley) and hf > 0)
                        outcomes[5] += int(regular and hs > 0 and hf > 0)
    accepted = comb(n, opening)-comb(n-counts[0]-counts[1], opening)
    base = accepted*comb(n-opening, prizes)*(n-opening-prizes)
    probabilities = {}
    for route in ("direct", "psychic_paid_ball"):
        search = int(route == "psychic_paid_ball")
        denominator = (
            base*(n-opening-prizes-3-search)
            * factorial(n-opening-prizes-4-search)
        )
        probabilities[route] = tuple(Fraction(v, denominator) for v in sums[route])
    return probabilities


class PaidBallTests(unittest.TestCase):
    def test_published_champion_baselines_and_fractions(self) -> None:
        from tools.shadow_rider_valley_pivot_gate import exact_direct_valley
        self.assertEqual(sum(COUNTS), 60)
        data = exact_paid()
        direct = data["direct"]
        reference = exact_direct_valley()
        self.assertEqual(direct.launch, reference.launch)
        self.assertEqual(direct.energy_three_float, reference.cost_three_with_pivot)
        self.assertEqual(direct.valley_two_float, reference.cost_two_with_valley_and_pivot)
        self.assertEqual(direct.either_float, reference.either_cost_with_pivot)
        paid = data["psychic_paid_ball"]
        self.assertEqual(paid.launch, Fraction(68083905331, 231209574400))
        self.assertEqual(
            paid.energy_three, Fraction(1417049009313617, 26985105254553600),
        )
        self.assertEqual(
            paid.energy_three_float, Fraction(113809106294839, 13492552627276800),
        )
        self.assertEqual(
            paid.valley_two_float, Fraction(49196835502623, 17990070169702400),
        )
        self.assertEqual(paid.either_float, Fraction(2639576474979, 264559855436800))

    def test_independent_physical_decks(self) -> None:
        for counts in (
            (1, 2, 2, 2, 1, 1, 1, 1),
            (1, 2, 2, 3, 1, 1, 1, 1),
            (1, 3, 2, 2, 1, 1, 1, 1),
            (1, 2, 2, 2, 1, 2, 1, 1),
        ):
            grouped = (
                counts[0], counts[1], counts[2], counts[3],
                counts[4], counts[5], counts[6]+counts[7],
            )
            model = exact_paid(counts=grouped, opening=3, prizes=1)
            oracle = physical_oracle(counts)
            for route, answer in model.items():
                self.assertEqual(
                    (answer.launch, answer.energy_three, answer.energy_three_float,
                     answer.valley_two_float, answer.either_float, answer.overlap),
                    oracle[route], (counts, route),
                )

    def test_no_search_or_no_payment_blocks_paid_branch(self) -> None:
        self.assertEqual(
            exact_paid(counts=(1, 2, 2, 3, 1, 0, 2), opening=3, prizes=1)[
                "psychic_paid_ball"
            ].launch, 0,
        )
        self.assertEqual(
            exact_paid(counts=(1, 2, 2, 0, 1, 2, 4), opening=3, prizes=1)[
                "psychic_paid_ball"
            ].launch, 0,
        )

    def test_prints_and_decklist(self) -> None:
        root = Path(__file__).resolve().parents[3]
        print_specs = (
            ("sm6", "113", "Mysterious Treasure", "Discard a card"),
            ("swsh1", "179", "Quick Ball", "discard another card"),
        )
        for set_code, number, name, fragment in print_specs:
            cards = json.loads(
                (root / "resources" / "cards" / "en" / (set_code + ".json"))
                .read_text(encoding="utf-8")
            )
            item = next(x for x in cards if str(x["number"]) == number)
            self.assertEqual(item["name"], name)
            self.assertIn(fragment.lower(), " ".join(item["rules"]).lower())
        published = (
            root / "results" / "decks" / "shadow-rider-calyrex" / "README.md"
        ).read_text(encoding="utf-8")
        for row in (
            "| 4 | Mysterious Treasure |",
            "| 1 | Quick Ball |",
            "| 1 | Radiant Eternatus |",
            "| 11 | Basic Psychic Energy |",
        ):
            self.assertIn(row, published)


if __name__ == "__main__":
    unittest.main(verbosity=2)
