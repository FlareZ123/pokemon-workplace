"""Labeled physical-card oracle for Skyliner free retreat and paid Radiant lines."""
from __future__ import annotations

import json
import unittest
from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations
from math import comb, factorial
from pathlib import Path

from tools.shadow_rider_latias_pivot import exact_latias, five_category_draw_window


def physical_oracle(
    counts: tuple[int, ...], *, opening: int = 3, prizes: int = 1,
) -> dict[str, tuple[Fraction, ...]]:
    """Classes: Radiant, other Basic, Latias, VMAX, Psychic, Float, Ball, Valley, filler."""
    cards = [kind for kind, quantity in enumerate(counts) for _ in range(quantity)]
    n = len(cards)
    ids = tuple(range(n))
    wins = defaultdict(lambda: [0] * 5)
    for opener in combinations(ids, opening):
        if not any(cards[i] in (0, 1, 2) for i in opener):
            continue
        if not any(cards[i] in (1, 2) for i in opener):
            continue
        unknown = [i for i in ids if i not in opener]
        for prize in combinations(unknown, prizes):
            deck = [i for i in unknown if i not in prize]
            for first in deck:
                hand = [*opener, first]
                after_first = [i for i in deck if i != first]
                if any(cards[i] == 0 for i in hand):
                    route = "direct"
                else:
                    route = "psychic_paid_ball"
                    radiant = next((i for i in after_first if cards[i] == 0), None)
                    ball = next((i for i in hand if cards[i] == 6), None)
                    energy = next((i for i in hand if cards[i] == 4), None)
                    if radiant is None or ball is None or energy is None:
                        continue
                    hand = [i for i in hand if i not in (ball, energy)]
                    after_first = [i for i in after_first if i != radiant]
                vmax = [i for i in after_first if cards[i] == 3]
                if len(vmax) < 2:
                    continue
                after_launch = [i for i in after_first if i not in vmax[:2]]
                for second in after_launch:
                    remaining = [i for i in after_launch if i != second]
                    for order in permutations(remaining):
                        he = sum(cards[i] == 4 for i in (*hand, second))
                        hf = sum(cards[i] == 5 for i in (*hand, second))
                        hl = sum(cards[i] == 2 for i in (*hand, second))
                        hv = sum(cards[i] == 7 for i in (*hand, second))
                        attached, offset = 0, 0
                        for _ in range(2):
                            if he == 0:
                                continue
                            he -= 1
                            attached += 1
                            drawn = order[offset:offset+2]
                            he += sum(cards[i] == 4 for i in drawn)
                            hf += sum(cards[i] == 5 for i in drawn)
                            hl += sum(cards[i] == 2 for i in drawn)
                            hv += sum(cards[i] == 7 for i in drawn)
                            offset += len(drawn)
                        energy_total = attached+int(he > 0)
                        free_retreat = hf > 0 or hl > 0
                        normal = energy_total >= 3 and free_retreat
                        reduced = energy_total >= 2 and hv > 0 and free_retreat
                        outcome = wins[route]
                        outcome[0] += 1
                        outcome[1] += int(normal)
                        outcome[2] += int(reduced)
                        outcome[3] += int(normal or reduced)
                        outcome[4] += int(normal and reduced)
    accepted = comb(n, opening)-comb(
        n-counts[0]-counts[1]-counts[2], opening,
    )
    common = accepted*comb(n-opening, prizes)*(n-opening-prizes)
    answer = {}
    for route in ("direct", "psychic_paid_ball"):
        searched = int(route == "psychic_paid_ball")
        denominator = (
            common*(n-opening-prizes-3-searched)
            *factorial(n-opening-prizes-4-searched)
        )
        answer[route] = tuple(Fraction(x, denominator) for x in wins[route])
    return answer


class LatiasPivotTests(unittest.TestCase):
    def test_champion_source_and_prior_model(self) -> None:
        from tools.shadow_rider_paid_ball_attack import exact_paid

        results = exact_latias()
        previous = exact_paid()
        self.assertEqual(
            results["direct"].either_pivot,
            Fraction(2077325866094987, 119654885314764800),
        )
        self.assertEqual(
            results["psychic_paid_ball"].either_pivot,
            Fraction(76536944823113, 3751939768012800),
        )
        for route in ("direct", "psychic_paid_ball"):
            self.assertEqual(results[route].launch, previous[route].launch)
            self.assertGreater(
                results[route].normal_energy_pivot,
                previous[route].energy_three_float,
            )
            self.assertGreater(
                results[route].either_pivot,
                previous[route].either_float,
            )

    def test_independent_small_physical_card_population(self) -> None:
        for counts in (
            (1, 1, 1, 2, 2, 1, 1, 1, 1),
            (1, 2, 1, 2, 2, 1, 1, 1, 1),
            (1, 1, 1, 2, 3, 1, 1, 1, 1),
            (1, 1, 1, 2, 2, 1, 2, 1, 1),
        ):
            grouped = (
                counts[0], counts[1]+counts[2], counts[3], counts[4],
                counts[5], counts[6], counts[7]+counts[8],
            )
            model = exact_latias(counts=grouped, opening=3, prizes=1)
            baseline = physical_oracle(counts)
            for route, row in model.items():
                self.assertEqual(
                    (row.launch, row.normal_energy_pivot,
                     row.reduced_valley_pivot, row.either_pivot, row.overlap),
                    baseline[route], (route, counts),
                )

    def test_known_small_conditional_draw(self) -> None:
        self.assertEqual(
            five_category_draw_window(2, 1, 7, 0, 1, 0, 1, 0, 1)[2],
            Fraction(5, 7),
        )
        with self.assertRaises(ValueError):
            five_category_draw_window(1, 7, 8, 0, 1, 0, 1, 0, 1)

    def test_verified_printed_skyliner_and_decklist(self) -> None:
        root = Path(__file__).resolve().parents[3]
        cards = json.loads(
            (root / "resources" / "cards" / "en" / "sv8.json")
            .read_text(encoding="utf-8")
        )
        latias = next(x for x in cards if str(x["number"]) == "76")
        self.assertEqual(latias["name"], "Latias ex")
        self.assertEqual(latias["abilities"][0]["name"], "Skyliner")
        self.assertIn("Basic Pokémon in play have no Retreat Cost", latias["abilities"][0]["text"])
        readme = (
            root / "results" / "decks" / "shadow-rider-calyrex" / "README.md"
        ).read_text(encoding="utf-8")
        for row in (
            "| 1 | Latias ex |",
            "| 1 | Float Stone |",
            "| 1 | Dimension Valley |",
        ):
            self.assertIn(row, readme)


if __name__ == "__main__":
    unittest.main(verbosity=2)
