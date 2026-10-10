"""Exact staged Beheeyem setup and retained Basic tutor, including Buddy-Buddy Poffin.

Model: eligible Elgyem and anchor Basic each have <=70 HP.
A ready board has opening-active Elgyem and, by first-turn end,
a second Elgyem and an anchor Basic; T2 must retain or draw a post-T1
search Item capable of later Benching returned Elgyem.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb, lcm
import json


@lru_cache(maxsize=None)
def joint_access(vip: int, nest: int, poffin: int,
                 *, elgyem: int = 4, anchor: int = 4,
                 anchor_poffin_eligible: bool = True) -> tuple[Fraction, Fraction]:
    """Exact (first-turn-ready, ready-and-live-tutor-by-turn-two) probabilities."""
    if not all(0 <= c <= 4 for c in (vip, nest, poffin)):
        raise ValueError("Up to four copies per Item name")
    if not (2 <= elgyem <= 4 and 1 <= anchor <= 4):
        raise ValueError("Expected two to four Elgyem and one to four anchors")
    copies = (elgyem, anchor, vip, nest, poffin, 60 - elgyem - anchor - vip - nest - poffin)
    space = comb(60, 7) * 53 * comb(52, 6)
    denom = lcm(44, 45, 46)
    total = staged = joint_scaled = 0

    for first_five in product(*(range(min(7, c) + 1) for c in copies[:5])):
        other = 7 - sum(first_five)
        if not 0 <= other <= copies[-1]:
            continue
        opening = first_five + (other,)
        ways = comb(copies[-1], other)
        for n, k in zip(copies[:5], first_five):
            ways *= comb(n, k)
        remaining = tuple(n - k for n, k in zip(copies, opening))
        if not ways:
            continue

        for natural_draw, draw_ways in enumerate(remaining):
            if draw_ways == 0:
                continue
            seen = list(opening)
            seen[natural_draw] += 1
            after = list(remaining)
            after[natural_draw] -= 1
            missing_e = max(0, 2 - seen[0])
            missing_a = max(0, 1 - seen[1])
            missing = missing_e + missing_a
            # VIP can fetch two Basics on the first turn only.
            need_live = max(0, missing - 2 * seen[2])
            # Poffin covers two 70-HP-or-lower Basics, Nest covers one.
            if anchor_poffin_eligible:
                spent_poffin = min(seen[4], (need_live + 1) // 2)
                spent_nest = max(0, need_live - 2 * spent_poffin)
            elif seen[2]:
                # A VIP handles both missing eligible and ineligible Basics.
                spent_poffin = spent_nest = 0
            else:
                # Opening Active Elgyem means at most one more Elgyem is needed.
                spent_poffin = min(seen[4], missing_e)
                spent_nest = missing_a + missing_e - spent_poffin
            has_capacity = spent_nest <= seen[3]
            live_in_hand = seen[3] + seen[4] - spent_nest - spent_poffin
            live_in_deck = after[3] + after[4]
            other_for_prizes = 52 - after[0] - after[1] - live_in_deck

            for prize_e in range(min(6, after[0]) + 1):
                for prize_a in range(min(6 - prize_e, after[1]) + 1):
                    for prize_live in range(min(6 - prize_e - prize_a, live_in_deck) + 1):
                        prize_other = 6 - prize_e - prize_a - prize_live
                        if prize_other > other_for_prizes:
                            continue
                        weight = (
                            ways * draw_ways
                            * comb(after[0], prize_e)
                            * comb(after[1], prize_a)
                            * comb(live_in_deck, prize_live)
                            * comb(other_for_prizes, prize_other)
                        )
                        total += weight
                        if (
                            opening[0] == 0
                            or not has_capacity
                            or after[0] - prize_e < missing_e
                            or after[1] - prize_a < missing_a
                        ):
                            continue
                        staged += weight
                        if live_in_hand:
                            joint_scaled += weight * denom
                        else:
                            # Post-search deck has 46 cards less searched Basics.
                            live_tutors_in_deck = live_in_deck - prize_live
                            joint_scaled += weight * live_tutors_in_deck * (denom // (46 - missing))
    assert total == space, (total, space)
    return Fraction(staged, space), Fraction(joint_scaled, space * denom)


def main() -> None:
    regimes = {}
    for eligible in (True, False):
        rows = []
        for vip in range(5):
            for nest in range(5 - vip):
                poffin = 4 - vip - nest
                stage, joint = joint_access(
                    vip, nest, poffin, anchor_poffin_eligible=eligible
                )
                rows.append({
                    "vip": vip, "nest": nest, "poffin": poffin,
                    "staged_percent": round(100 * float(stage), 6),
                    "joint_percent": round(100 * float(joint), 6),
                })
        assert len(rows) == 15
        old = {(r["vip"], r["nest"]): r for r in rows if r["poffin"] == 0}
        assert [old[v, 4-v]["staged_percent"] for v in range(5)] == [
            11.775394, 13.452432, 15.12947, 16.806508, 18.483546]
        assert [old[v, 4-v]["joint_percent"] for v in range(5)] == [
            2.757941, 3.181558, 2.918123, 1.886791, 0.0]
        stage_max = max(r["staged_percent"] for r in rows)
        joint_max = max(r["joint_percent"] for r in rows)
        stage_bests = [r for r in rows if r["staged_percent"] == stage_max]
        joint_bests = [r for r in rows if r["joint_percent"] == joint_max]
        regimes["eligible" if eligible else "ineligible"] = {
            "rows": rows, "stage_bests": stage_bests, "joint_bests": joint_bests
        }
    assert (regimes["eligible"]["joint_bests"] ==
            [dict(vip=0, nest=0, poffin=4,
                  staged_percent=18.483546, joint_percent=4.510096)])
    assert all(r["poffin"] == 0 for r in regimes["ineligible"]["joint_bests"])
    print(json.dumps({"slot_budget": 4, "anchor_poffin_eligibility": regimes}, indent=2))


if __name__ == "__main__":
    main()
