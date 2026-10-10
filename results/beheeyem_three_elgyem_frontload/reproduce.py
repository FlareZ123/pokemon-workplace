"""Exact alternative early Basic-availability certificates for a T4 Beheeyem attacker.

A: Stage 2 Elgyem + anchor T1, reserve a live Basic tutor by T2 for T3 use.
B: Stage 3 Elgyem + anchor T1, preloading an alternate mature line for T4.
The result is the union A OR B. No evolution/Energy access is modeled.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb, lcm
import json


def continuation_access(
    vip: int, nest: int, poffin: int, *,
    anchor_poffin_eligible: bool = True,
    elgyem: int = 4, anchor: int = 4
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """(stage-two, reserve-path, stage-three, union) exact probabilities."""
    if not all(0 <= c <= 4 for c in (vip, nest, poffin)):
        raise ValueError("At most four of each search Item")
    if not (3 <= elgyem <= 4 and 1 <= anchor <= 4):
        raise ValueError("Need 3-4 Elgyem and 1-4 anchor Basics")
    copies = (elgyem, anchor, vip, nest, poffin,
              60 - elgyem - anchor - vip - nest - poffin)
    sample_space = comb(60, 7) * 53 * comb(52, 6)
    denominator = lcm(44, 45, 46)
    total = stage_two = stage_three = reserve_scaled = union_scaled = 0

    for first_five in product(*(range(min(7, c) + 1) for c in copies[:5])):
        filler = 7 - sum(first_five)
        if not 0 <= filler <= copies[-1]:
            continue
        opening = first_five + (filler,)
        ways = comb(copies[-1], filler)
        for total_copies, opening_copies in zip(copies[:5], first_five):
            ways *= comb(total_copies, opening_copies)
        remaining = tuple(n - k for n, k in zip(copies, opening))

        for draw_cat, multiplicity in enumerate(remaining):
            if not multiplicity:
                continue
            seen = list(opening)
            seen[draw_cat] += 1
            after = list(remaining)
            after[draw_cat] -= 1
            missing_two_e = max(0, 2 - seen[0])
            missing_three_e = max(0, 3 - seen[0])
            missing_anchor = max(0, 1 - seen[1])
            missing_two = missing_two_e + missing_anchor
            missing_three = missing_three_e + missing_anchor
            vip_count, nest_count, poffin_count = seen[2:5]

            # Stage-two path's minimum spend of live Basic-search Items.
            if anchor_poffin_eligible:
                after_vip = max(0, missing_two - 2 * vip_count)
                spend_poffin = min(poffin_count, (after_vip + 1) // 2)
                spend_nest = max(0, after_vip - 2 * spend_poffin)
            elif vip_count:
                spend_poffin = spend_nest = 0
            else:
                spend_poffin = min(poffin_count, missing_two_e)
                spend_nest = missing_anchor + missing_two_e - spend_poffin
            capacity_two = spend_nest <= nest_count

            # An alternative stateful path has a third Elgyem already in play.
            if anchor_poffin_eligible or vip_count:
                capacity_three = (
                    2 * vip_count + 2 * poffin_count + nest_count >= missing_three
                )
            else:
                capacity_three = (
                    nest_count >= missing_anchor
                    and 2 * poffin_count + nest_count - missing_anchor >= missing_three_e
                )

            live_hand = poffin_count + nest_count - spend_poffin - spend_nest
            live_deck = after[3] + after[4]
            pooled_other = 52 - after[0] - after[1] - live_deck

            for prize_e in range(min(6, after[0]) + 1):
                for prize_anchor in range(min(6 - prize_e, after[1]) + 1):
                    for prize_live in range(min(6 - prize_e - prize_anchor, live_deck) + 1):
                        prize_other = 6 - prize_e - prize_anchor - prize_live
                        if prize_other > pooled_other:
                            continue
                        w = (
                            ways * multiplicity * comb(after[0], prize_e)
                            * comb(after[1], prize_anchor)
                            * comb(live_deck, prize_live)
                            * comb(pooled_other, prize_other)
                        )
                        total += w
                        if opening[0] == 0:
                            continue
                        enough_anchor = after[1] - prize_anchor >= missing_anchor
                        enough_two_e = after[0] - prize_e >= missing_two_e
                        enough_three_e = after[0] - prize_e >= missing_three_e
                        two = capacity_two and enough_anchor and enough_two_e
                        three = capacity_three and enough_anchor and enough_three_e

                        if two:
                            stage_two += w
                            if live_hand:
                                q_scaled = denominator
                            else:
                                q_scaled = (
                                    (live_deck - prize_live)
                                    * (denominator // (46 - missing_two))
                                )
                            reserve_scaled += w * q_scaled
                        if three:
                            stage_three += w
                            union_scaled += w * denominator
                        elif two:
                            union_scaled += w * q_scaled

    assert total == sample_space
    return (
        Fraction(stage_two, sample_space),
        Fraction(reserve_scaled, sample_space * denominator),
        Fraction(stage_three, sample_space),
        Fraction(union_scaled, sample_space * denominator),
    )


def main() -> None:
    regimes = {}
    for eligible in (True, False):
        rows = []
        for vip in range(5):
            for nest in range(5 - vip):
                poffin = 4 - vip - nest
                two, reserve, three, union = continuation_access(
                    vip, nest, poffin, anchor_poffin_eligible=eligible
                )
                assert three <= two
                assert union >= max(three, reserve)
                assert union <= three + reserve
                rows.append({
                    "vip": vip, "nest": nest, "poffin": poffin,
                    "two_staged_percent": round(float(two) * 100, 6),
                    "reserve_path_percent": round(float(reserve) * 100, 6),
                    "three_staged_percent": round(float(three) * 100, 6),
                    "either_path_percent": round(float(union) * 100, 6),
                })
        best = max(rows, key=lambda r: r["either_path_percent"])
        regimes["eligible" if eligible else "ineligible"] = {
            "best": best, "rows": rows
        }
    assert tuple(regimes["eligible"]["best"][k] for k in ("vip","nest","poffin")) == (0,0,4)
    assert tuple(regimes["ineligible"]["best"][k] for k in ("vip","nest","poffin")) == (4,0,0)
    assert regimes["eligible"]["best"]["either_path_percent"] == 10.282682
    assert regimes["ineligible"]["best"]["either_path_percent"] == 9.637382
    print(json.dumps({"slot_budget": 4, "regimes": regimes}, indent=2))


if __name__ == "__main__":
    main()
