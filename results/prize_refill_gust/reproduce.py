"""Exact independent sequential-deal check for Boss recovery from Prize cards."""
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.gust_prize_minimax import enumerate_boards
from tools.prize_refill_gust import (
    expected_attacks, expected_opening_deal_attacks,
    initial_partitions, two_attack_boss_probability,
)
from tools.stochastic_gust_draw import expected_attacks as no_prize_kernel


def next_draw(gusts, fillers):
    n = gusts + fillers
    if gusts:
        yield 1, gusts - 1, fillers, Fraction(gusts, n)
    if fillers:
        yield 0, gusts, fillers - 1, Fraction(fillers, n)


def sample_prizes(prized_gusts, prizes_left, amount):
    for got in range(
        max(0, amount - (prizes_left - prized_gusts)),
        min(prized_gusts, amount) + 1
    ):
        weight = Fraction(
            comb(prized_gusts, got)
            * comb(prizes_left - prized_gusts, amount - got),
            comb(prizes_left, amount)
        )
        yield got, weight


def independent_two_turn_probability(copies, collect):
    """Enumerate hand, Prize, deck, draws and 3-Prize collection sequentially."""
    result = Fraction(0)
    for hand, prized, deck, partition in initial_partitions(copies):
        for draw_one, remain, filler, p1 in next_draw(deck, 47 - deck):
            if hand + draw_one < 1:
                continue
            hand_after_one = hand + draw_one - 1
            for from_prize, p_prize in sample_prizes(prized, 6, 3):
                after_prizes = hand_after_one + (from_prize if collect else 0)
                for draw_two, d2, f2, p2 in next_draw(remain, filler):
                    if after_prizes + draw_two >= 1:
                        result += partition * p1 * p_prize * p2
    return result


def main():
    for copies in range(5):
        assert sum(p for _, _, _, p in initial_partitions(copies)) == 1

    expected = {
        0: (Fraction(4), Fraction(4)),
        1: (Fraction(4), Fraction(4)),
        2: (Fraction(1387, 354), Fraction(2333, 590)),
        3: (Fraction(2233, 590), Fraction(13259, 3422)),
        4: (Fraction(588821, 162545), Fraction(122593, 32509)),
    }
    expected_two_turn = {
        0: (Fraction(0), Fraction(0)),
        1: (Fraction(0), Fraction(0)),
        2: (Fraction(2, 59), Fraction(6, 295)),
        3: (Fraction(774, 8555), Fraction(96, 1711)),
        4: (Fraction(78542, 487635), Fraction(3354, 32509)),
    }
    for copies, (want_with, want_without) in expected.items():
        with_prizes = expected_opening_deal_attacks(copies, 1, (1, 3, 3), True)
        without = expected_opening_deal_attacks(copies, 1, (1, 3, 3), False)
        assert (with_prizes, without) == (want_with, want_without)
        assert with_prizes <= without
        result = (
            two_attack_boss_probability(copies, True),
            two_attack_boss_probability(copies, False),
        )
        assert result == expected_two_turn[copies]
        assert result == (
            independent_two_turn_probability(copies, True),
            independent_two_turn_probability(copies, False),
        )
        print(
            f"Boss copies {copies}: E[attacks] with/without Prize refill "
            f"{with_prizes} / {without}; P(two-turn win) {result[0]} / {result[1]}"
        )

    # Independent baseline kernel: when taking Prize cards cannot replenish
    # Boss, the large DP reduces exactly to stochastic_gust_draw for any
    # fixed initial K1 zone partition and any attacking board.
    reductions = 0
    boards = tuple(enumerate_boards())
    for a, b, values in boards:
        for copies in range(5):
            for h, p, d, prob in initial_partitions(copies):
                baseline = no_prize_kernel(a, b, h, d, 47 - d, 6)
                actual = expected_attacks(a, b, h, d, 47 - d, p, 6, False)
                assert baseline == actual, (a, b, h, p, d)
                reductions += 1
    assert reductions == 5110, reductions
    print("PASS", reductions, "cross-kernel no-Prize-refill reductions")
    print("PASS independent sequential-deal probability and Prize-draw checks")


if __name__ == "__main__":
    main()
