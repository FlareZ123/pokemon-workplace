"""Exact hand-packet and discard-payment access for one Beheeyem recycle."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb
import json


def _choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def full_packet_probability(hand_size: int, fodder_copies: int) -> Fraction:
    """Draw Nest, Evolution Incense, Guzma & Hala, and >=2 discardable cards."""
    assert 0 <= fodder_copies <= 48
    capacities = (4, 4, 4, fodder_copies, 48 - fodder_copies)
    favorable = 0
    normalized = 0
    for nest, incense, guzma, fodder in product(
        range(5), range(5), range(5), range(fodder_copies + 1)
    ):
        other = hand_size - nest - incense - guzma - fodder
        if not 0 <= other <= capacities[-1]:
            continue
        ways = (
            comb(4, nest) * comb(4, incense) * comb(4, guzma)
            * comb(fodder_copies, fodder) * comb(capacities[-1], other)
        )
        normalized += ways
        if nest and incense and guzma and fodder >= 2:
            favorable += ways
    assert normalized == comb(60, hand_size)
    return Fraction(favorable, normalized)


def conditional_payment_probability(hand_size: int, fodder_copies: int) -> Fraction:
    """Given 3 distinct connectors held, sample the other hand slots from 57."""
    slots = hand_size - 3
    numerator = sum(
        _choose(fodder_copies, k) * _choose(57 - fodder_copies, slots - k)
        for k in range(2, slots + 1)
    )
    return Fraction(numerator, comb(57, slots))


def main() -> None:
    rows = []
    for hand_size in (7, 9):
        for fodder_copies in (8, 16, 24, 32):
            unconditional = full_packet_probability(hand_size, fodder_copies)
            conditional = conditional_payment_probability(hand_size, fodder_copies)
            rows.append({
                "hand_size": hand_size,
                "discardable_deck_copies": fodder_copies,
                "whole_packet_percent": round(float(unconditional) * 100, 6),
                "pay_two_given_three_connectors_percent": round(float(conditional) * 100, 6),
            })
    assert rows[0]["whole_packet_percent"] == 0.49242
    assert rows[3]["whole_packet_percent"] == 3.939161
    assert rows[1]["pay_two_given_three_connectors_percent"] == 31.184021
    assert rows[3]["pay_two_given_three_connectors_percent"] == 78.16511
    assert all(
        rows[i]["whole_packet_percent"] < rows[i + 1]["whole_packet_percent"]
        for i in (0, 1, 2, 4, 5, 6)
    )
    assert all(
        rows[i]["whole_packet_percent"] < rows[i + 4]["whole_packet_percent"]
        for i in range(4)
    )
    print(json.dumps({"rows": rows, "maximum_cycles_without_reclaiming_each_connector": 4}, indent=2))


if __name__ == "__main__":
    main()
