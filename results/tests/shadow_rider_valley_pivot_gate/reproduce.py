"""Independent labeled physical oracle for singleton Valley and Float access."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction
from itertools import combinations, permutations
from math import comb, factorial
from pathlib import Path

from tools.shadow_rider_valley_pivot_gate import (
    exact_direct_valley, dual_card_draw_probability,
)


def physical_oracle(
    classes: tuple[int, int, int, int, int, int, int],
    *, opening: int = 3, prizes: int = 1,
) -> tuple[Fraction, ...]:
    """Classes: Radiant, other Basics, VMAX, Psychic, Float, Valley, filler."""
    cards = [category for category, count in enumerate(classes) for _ in range(count)]
    n = len(cards)
    ids = tuple(range(n))
    success = [0] * 6
    for opener in combinations(ids, opening):
        if not any(cards[i] in (0, 1) for i in opener):
            continue
        if not any(cards[i] == 1 for i in opener):
            continue
        outside = [i for i in ids if i not in opener]
        for prize in combinations(outside, prizes):
            available = [i for i in outside if i not in prize]
            for first in available:
                if not any(cards[i] == 0 for i in (*opener, first)):
                    continue
                remaining = [i for i in available if i != first]
                vmax = [i for i in remaining if cards[i] == 2]
                if len(vmax) < 2:
                    continue
                after_launch = [i for i in remaining if i not in vmax[:2]]
                for natural in after_launch:
                    residual = [i for i in after_launch if i != natural]
                    for order in permutations(residual):
                        he = sum(cards[i] == 3 for i in (*opener, first, natural))
                        hp = sum(cards[i] == 4 for i in (*opener, first, natural))
                        hs = sum(cards[i] == 5 for i in (*opener, first, natural))
                        attached, cursor = 0, 0
                        for _ in range(2):
                            if he == 0:
                                continue
                            he -= 1
                            attached += 1
                            drawn = order[cursor:cursor+2]
                            he += sum(cards[i] == 3 for i in drawn)
                            hp += sum(cards[i] == 4 for i in drawn)
                            hs += sum(cards[i] == 5 for i in drawn)
                            cursor += len(drawn)
                        total = attached + int(he > 0)
                        regular = total >= 3
                        valley = total >= 2 and hs > 0
                        success[0] += 1
                        success[1] += int(regular and hp > 0)
                        success[2] += int(valley)
                        success[3] += int(valley and hp > 0)
                        success[4] += int((regular or valley) and hp > 0)
                        success[5] += int(regular and valley and hp > 0)
    accepted = comb(n, opening) - comb(n-classes[0]-classes[1], opening)
    denominator = (
        accepted * comb(n-opening, prizes) * (n-opening-prizes)
        * (n-opening-prizes-3) * factorial(n-opening-prizes-4)
    )
    return tuple(Fraction(value, denominator) for value in success)


class ValleyGateTests(unittest.TestCase):
    def test_exact_champion_fractions(self) -> None:
        r = exact_direct_valley()
        self.assertEqual(r.launch, Fraction(2431309737, 20230837760))
        self.assertEqual(
            r.cost_three_with_pivot, Fraction(70767776772269, 9204221947289600),
        )
        self.assertEqual(
            r.cost_two_with_valley, Fraction(43117466834961, 3346989799014400),
        )
        self.assertEqual(
            r.cost_two_with_valley_and_pivot,
            Fraction(7969026626217, 3681688778915840),
        )
        self.assertEqual(
            r.either_cost_with_pivot, Fraction(3392929014049, 391669019033600),
        )
        self.assertEqual(
            r.cost_three_with_valley_and_pivot,
            Fraction(10336331611, 8683228252160),
        )
        self.assertEqual(r.residual_states, 2541)

    def test_independent_small_physical_decks(self) -> None:
        for classes in (
            (1, 2, 2, 2, 1, 1, 1),
            (1, 2, 2, 3, 1, 1, 1),
            (1, 3, 2, 2, 1, 1, 1),
            (1, 2, 3, 2, 1, 1, 1),
        ):
            grouped = (
                classes[0], classes[1], classes[2], classes[3],
                classes[4], classes[5] + classes[6],
            )
            model = exact_direct_valley(counts=grouped, opening=3, prizes=1)
            self.assertEqual(
                (
                    model.launch, model.cost_three_with_pivot,
                    model.cost_two_with_valley, model.cost_two_with_valley_and_pivot,
                    model.either_cost_with_pivot, model.cost_three_with_valley_and_pivot,
                ),
                physical_oracle(classes), classes,
            )

    def test_draw_edge_cases(self) -> None:
        self.assertEqual(
            dual_card_draw_probability(2, 1, 7, 0, 1, 0, 1, 3),
            Fraction(4, 35),
        )
        self.assertEqual(
            dual_card_draw_probability(0, 2, 7, 0, 1, 0, 1, 2),
            0,
        )
        with self.assertRaises(ValueError):
            dual_card_draw_probability(1, 6, 7, 0, 1, 0, 1, 3)

    def test_source_prints_and_deck_count(self) -> None:
        root = Path(__file__).resolve().parents[3]
        printed = (
            ("xy4", "93", "Dimension Valley", "attacks"),
            ("xy8", "137", "Float Stone", "no Retreat Cost"),
            ("xy6", "89", "Sky Field", "8 Pokémon"),
        )
        for set_code, number, name, fragment in printed:
            cards = json.loads(
                (root / "resources" / "cards" / "en" / (set_code + ".json"))
                .read_text(encoding="utf-8")
            )
            card = next(x for x in cards if str(x["number"]) == number)
            self.assertEqual(card["name"], name)
            self.assertIn(fragment, " ".join(card["rules"]))
        published = (
            root / "results" / "decks" / "shadow-rider-calyrex" / "README.md"
        ).read_text(encoding="utf-8")
        for line in (
            "| 1 | Radiant Eternatus |",
            "| 4 | Shadow Rider Calyrex VMAX |",
            "| 1 | Float Stone |",
            "| 1 | Dimension Valley |",
        ):
            self.assertIn(line, published)


if __name__ == "__main__":
    unittest.main(verbosity=2)
