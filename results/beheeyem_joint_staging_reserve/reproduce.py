"""Exact joint first-turn staging and reserved Nest Ball through turn two."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb, lcm
import json


def joint_access(\n    vip: int, nest: int, *, elgyem_copies: int = 4, partner_copies: int = 4\n) -> tuple[Fraction, Fraction]:
    """Return (ready first turn, ready and unused Nest in hand by turn two)."""
    if not 0 <= vip <= 4 or not 0 <= nest <= 4:
        raise ValueError("Each Item name has at most four copies")
    # Disjoint categories: Elgyem, partner Basic, VIP, Nest, other.
    copies = (4, 4, vip, nest, 52 - vip - nest)
    sample_space = comb(60, 7) * 53 * comb(52, 6)
    continuation_denominator = lcm(44, 45, 46)
    normalized = ready = reserved_nest = 0

    for opening_four in product(*(range(min(7, count) + 1) for count in copies[:4])):
        other_opening = 7 - sum(opening_four)
        if not 0 <= other_opening <= copies[-1]:
            continue
        opening = opening_four + (other_opening,)
        opening_ways = comb(copies[-1], other_opening)
        for total, drawn in zip(copies[:4], opening_four):
            opening_ways *= comb(total, drawn)
        remaining = [total - drawn for total, drawn in zip(copies, opening)]

        for first_turn_draw, multiplicity in enumerate(remaining):
            if not multiplicity:
                continue
            seen = list(opening)
            seen[first_turn_draw] += 1
            after_draw = remaining.copy()
            after_draw[first_turn_draw] -= 1
            missing_elgyem = max(0, 2 - seen[0])
            missing_partner = max(0, 1 - seen[1])
            missing_total = missing_elgyem + missing_partner
            output_capacity = 2 * seen[2] + seen[3]

            for prize_elgyem in range(min(6, after_draw[0]) + 1):
                for prize_partner in range(min(6 - prize_elgyem, after_draw[1]) + 1):
                    for prize_nest in range(min(6 - prize_elgyem - prize_partner, after_draw[3]) + 1):
                        prize_other = 6 - prize_elgyem - prize_partner - prize_nest
                        remaining_other = 52 - after_draw[0] - after_draw[1] - after_draw[3]
                        if prize_other > remaining_other:
                            continue
                        prize_ways = (
                            comb(after_draw[0], prize_elgyem)
                            * comb(after_draw[1], prize_partner)
                            * comb(after_draw[3], prize_nest)
                            * comb(remaining_other, prize_other)
                        )
                        weight = opening_ways * multiplicity * prize_ways
                        normalized += weight
                        if not (
                            opening[0] >= 1
                            and output_capacity >= missing_total
                            and after_draw[0] - prize_elgyem >= missing_elgyem
                            and after_draw[1] - prize_partner >= missing_partner
                        ):
                            continue
                        ready += weight
                        # Use available VIP outputs first to preserve Nest copies.
                        nest_spent = max(0, missing_total - 2 * seen[2])
                        nest_in_hand = seen[3] - nest_spent
                        if nest_in_hand:
                            reserved_nest += weight * continuation_denominator
                        else:
                            nest_in_deck = after_draw[3] - prize_nest
                            deck_size = 46 - missing_total
                            reserved_nest += (
                                weight * nest_in_deck
                                * (continuation_denominator // deck_size)
                            )

    assert normalized == sample_space
    return (
        Fraction(ready, sample_space),
        Fraction(reserved_nest, sample_space * continuation_denominator),
    )


def main() -> None:
    rows = []
    for vip in range(5):
        nest = 4 - vip
        staged, joint = joint_access(vip, nest)
        rows.append({
            "vip": vip,
            "nest": nest,
            "first_turn_ready_percent": round(float(staged) * 100, 6),
            "first_turn_ready_and_nest_reserved_percent": round(float(joint) * 100, 6),
        })
    assert [row["first_turn_ready_percent"] for row in rows] == [
        11.775394, 13.452432, 15.129470, 16.806508, 18.483546
    ]
    assert [row["first_turn_ready_and_nest_reserved_percent"] for row in rows] == [
        2.757941, 3.181558, 2.918123, 1.886791, 0.0
    ]
    assert max(rows, key=lambda r: r["first_turn_ready_percent"])["vip"] == 4
    assert max(rows, key=lambda r: r["first_turn_ready_and_nest_reserved_percent"])["vip"] == 1
    print(json.dumps({"fixed_item_slots": 4, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
