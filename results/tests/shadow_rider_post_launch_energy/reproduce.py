"""Independent deck-order oracle and pinned card-text checks for Shadow Rider."""
from __future__ import annotations
import json
import unittest
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
from tools.shadow_rider_post_launch_energy import EnergyWindow, attack_ready_probability


def exhaustive_deck_orders(window: EnergyWindow, cost: int) -> Fraction:
    success = 0
    for energy_positions in map(set, combinations(range(window.deck_size), window.deck_energy)):
        hand, offset, attached = window.hand_energy, 0, 0
        for _ in range(window.doors):
            if hand == 0:
                continue
            attached += 1
            hand -= 1
            count = min(window.cards_per_draw, window.deck_size - offset)
            hand += sum(p in energy_positions for p in range(offset, offset + count))
            offset += count
        success += attached + int(window.manual_attachment and hand > 0) >= cost
    return Fraction(success, comb(window.deck_size, window.deck_energy))


class ShadowRiderEnergyTests(unittest.TestCase):
    def test_pinned_card_text(self) -> None:
        root = Path(__file__).resolve().parents[3] / "resources" / "cards" / "en"

        def card(set_code: str, number: str) -> dict:
            cards = json.loads((root / (set_code + ".json")).read_text(encoding="utf-8"))
            return next(c for c in cards if str(c["number"]) == number)

        vmax = card("swsh6", "75")
        self.assertEqual(vmax["name"], "Shadow Rider Calyrex VMAX")
        self.assertEqual(vmax["attacks"][0]["cost"], ["Colorless"] * 3)
        self.assertEqual(vmax["abilities"][0]["name"], "Underworld Door")
        self.assertIn("Benched Psychic Pokémon", vmax["abilities"][0]["text"])
        self.assertIn("draw 2 cards", vmax["abilities"][0]["text"])
        self.assertIn("your turn ends", card("swsh12pt5", "105")["abilities"][0]["text"])
        valley = card("xy4", "93")
        self.assertIn("cost", valley["rules"][0])
        self.assertIn("less", valley["rules"][0])

    def test_all_small_decks(self) -> None:
        for size in range(9):
            for energy in range(size + 1):
                for hand in range(4):
                    for cost in range(5):
                        window = EnergyWindow(hand, energy, size)
                        self.assertEqual(
                            attack_ready_probability(window, cost),
                            exhaustive_deck_orders(window, cost),
                            (hand, energy, size, cost),
                        )

    def test_closed_forms(self) -> None:
        n, e = 41, 8
        one = EnergyWindow(1, e, n)
        self.assertEqual(
            attack_ready_probability(one, 2),
            1 - Fraction(comb(n - e, 2), comb(n, 2)),
        )
        p2 = Fraction(comb(e, 2), comb(n, 2))
        p1 = Fraction(e * (n - e), comb(n, 2))
        second = 1 - Fraction(comb(n - e - 1, 2), comb(n - 2, 2))
        self.assertEqual(attack_ready_probability(one, 3), p2 + p1 * second)
        self.assertEqual(
            attack_ready_probability(EnergyWindow(2, e, n), 3),
            1 - Fraction(comb(n - e, 4), comb(n, 4)),
        )

    def test_constraints(self) -> None:
        self.assertEqual(attack_ready_probability(EnergyWindow(0, 8, 41), 2), 0)
        self.assertEqual(attack_ready_probability(EnergyWindow(3, 8, 41), 3), 1)
        self.assertEqual(
            attack_ready_probability(EnergyWindow(2, 8, 41, manual_attachment=False), 3),
            0,
        )
        with self.assertRaises(ValueError):
            EnergyWindow(1, 9, 8)
        with self.assertRaises(ValueError):
            attack_ready_probability(EnergyWindow(1, 8, 41), -1)


    def test_joint_pivot_exhaustive(self) -> None:
        from tools.shadow_rider_post_launch_energy import attack_and_pivot_ready_probability

        for n in range(8):
            for e in range(n + 1):
                for p in range(n - e + 1):
                    for h in range(4):
                        for cost in (2, 3):
                            w = EnergyWindow(h, e, n)
                            success = 0
                            total = 0
                            for e_indices in combinations(range(n), e):
                                energy = set(e_indices)
                                available = [i for i in range(n) if i not in energy]
                                for p_indices in combinations(available, p):
                                    pivots = set(p_indices)
                                    hand, held_pivots, offset, attached = h, 0, 0, 0
                                    total += 1
                                    for _ in range(w.doors):
                                        if hand == 0:
                                            continue
                                        hand -= 1
                                        attached += 1
                                        count = min(w.cards_per_draw, n - offset)
                                        hand += sum(i in energy for i in range(offset, offset + count))
                                        held_pivots += sum(i in pivots for i in range(offset, offset + count))
                                        offset += count
                                    success += (attached + int(w.manual_attachment and hand > 0) >= cost
                                                and held_pivots > 0)
                            expected = Fraction(success, total)
                            self.assertEqual(
                                attack_and_pivot_ready_probability(w, cost, pivots_in_deck=p),
                                expected,
                                (h, e, p, n, cost),
                            )

    def test_float_stone_print_and_dependency(self) -> None:
        from tools.shadow_rider_post_launch_energy import attack_and_pivot_ready_probability

        root = Path(__file__).resolve().parents[3] / "resources" / "cards" / "en"
        cards = json.loads((root / "xy8.json").read_text(encoding="utf-8"))
        float_stone = next(c for c in cards if str(c["number"]) == "137")
        self.assertEqual(float_stone["name"], "Float Stone")
        self.assertTrue(any("no Retreat Cost" in line for line in float_stone["rules"]))

        window = EnergyWindow(1, 8, 41)
        energy = attack_ready_probability(window, 3)
        joint = attack_and_pivot_ready_probability(window, 3, pivots_in_deck=1)
        self.assertEqual(joint, Fraction(1204, 151905))
        self.assertGreater(energy * Fraction(4, 41), joint)
        self.assertEqual(
            attack_and_pivot_ready_probability(window, 3, pivots_in_deck=0, pivots_in_hand=1),
            energy,
        )



if __name__ == "__main__":
    unittest.main(verbosity=2)
