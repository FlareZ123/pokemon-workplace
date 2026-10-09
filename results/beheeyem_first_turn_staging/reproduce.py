"""Exact turn-one Beheeyem pipeline staging with Battle VIP Pass or Nest Ball."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb
import json


def board_ready_probability(vip_copies: int, nest_copies: int) -> Fraction:
    """Open Elgyem Active; have two Elgyem plus partner Basic in play by turn one."""
    if not (0 <= vip_copies <= 4 and 0 <= nest_copies <= 4):
        raise ValueError("Each Item name is limited to four copies")
    # [Elgyem, partner Basic, Battle VIP Pass, Nest Ball, other].
    pool = (4, 4, vip_copies, nest_copies, 52 - vip_copies - nest_copies)
    space = comb(60, 7) * 53 * comb(52, 6)
    favorable = 0
    checked = 0

    for drawn in product(*(range(min(c, 7) + 1) for c in pool[:4])):
        other = 7 - sum(drawn)
        if not 0 <= other <= pool[-1]:
            continue
        opening = drawn + (other,)
        ways_hand = comb(pool[-1], other)
        for count, seen in zip(pool[:4], drawn):
            ways_hand *= comb(count, seen)
        remaining = [count - seen for count, seen in zip(pool, opening)]

        for natural_draw, multiplicity in enumerate(remaining):
            if not multiplicity:
                continue
            first_eight = list(opening)
            first_eight[natural_draw] += 1
            left = remaining.copy()
            left[natural_draw] -= 1
            needs_e = max(0, 2 - first_eight[0])
            needs_partner = max(0, 1 - first_eight[1])
            search_capacity = 2 * first_eight[2] + first_eight[3]

            for prize_e in range(min(6, left[0]) + 1):
                for prize_partner in range(min(6 - prize_e, left[1]) + 1):
                    prize_other = 6 - prize_e - prize_partner
                    other_left = 52 - left[0] - left[1]
                    if prize_other > other_left:
                        continue
                    prize_deals = (
                        comb(left[0], prize_e) * comb(left[1], prize_partner)
                        * comb(other_left, prize_other)
                    )
                    weight = ways_hand * multiplicity * prize_deals
                    checked += weight
                    if (
                        opening[0] >= 1
                        and search_capacity >= needs_e + needs_partner
                        and left[0] - prize_e >= needs_e
                        and left[1] - prize_partner >= needs_partner
                    ):
                        favorable += weight

    assert checked == space, "Opening, natural draw and Prize counts must conserve deals"
    return Fraction(favorable, space)


def main() -> None:
    rows = []
    for vip, nest in ((0, 0), (1, 0), (0, 1), (4, 0), (0, 4), (2, 2), (4, 4)):
        probability = board_ready_probability(vip, nest)
        rows.append({
            "battle_vip_pass_copies": vip,
            "nest_ball_copies": nest,
            "ready_percent": round(float(probability) * 100, 6),
        })
    assert [row["ready_percent"] for row in rows] == [
        3.034427, 7.586977, 5.125785, 18.483546, 11.775394,
        15.129470, 24.168324,
    ]
    print(json.dumps({"rows": rows, "prize_cards": 6, "opening_hand": 7}, indent=2))


if __name__ == "__main__":
    main()
