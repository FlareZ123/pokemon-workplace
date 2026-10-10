"""Independent physical-deck simulation of two Beheeyem continuation paths."""

from __future__ import annotations

from collections import Counter
import json
import random

from reproduce import continuation_access


def estimate(vip: int, nest: int, poffin: int, eligible: bool,
             trials: int = 250_000, seed: int = 20261010) -> tuple[float, ...]:
    rng = random.Random(seed)
    source = (
        ["E"] * 4 + ["A"] * 4 + ["V"] * vip + ["N"] * nest
        + ["P"] * poffin + ["X"] * (52 - vip - nest - poffin)
    )
    counts = [0, 0, 0, 0]

    for _ in range(trials):
        cards = source.copy()
        rng.shuffle(cards)
        hand = cards[:7]
        prize = cards[7:13]
        deck = cards[13:]
        if "E" not in hand:
            continue
        hand.append(deck.pop(0))
        have = Counter(hand)
        needs_e2 = max(0, 2 - have["E"])
        needs_e3 = max(0, 3 - have["E"])
        needs_a = max(0, 1 - have["A"])
        miss2 = needs_e2 + needs_a
        miss3 = needs_e3 + needs_a
        have_v, have_n, have_p = have["V"], have["N"], have["P"]

        if eligible or have_v:
            possible3 = 2 * have_v + have_n + 2 * have_p >= miss3
        else:
            possible3 = have_n >= needs_a and (
                2 * have_p + have_n - needs_a >= needs_e3
            )
        three = possible3 and deck.count("E") >= needs_e3 and deck.count("A") >= needs_a

        remainder = max(0, miss2 - 2 * have_v)
        if eligible:
            spend_p = min(have_p, (remainder+1)//2)
            spend_n = max(0, remainder-2*spend_p)
        elif have_v:
            spend_p = spend_n = 0
        else:
            spend_p = min(have_p,needs_e2)
            spend_n = needs_a + needs_e2 - spend_p
        two = spend_n <= have_n and (
            deck.count("E") >= needs_e2 and deck.count("A") >= needs_a
        )

        reserve = False
        if two:
            if have_n + have_p - spend_n - spend_p > 0:
                reserve = True
            else:
                after_search = deck.copy()
                for _ in range(needs_e2):
                    after_search.remove("E")
                for _ in range(needs_a):
                    after_search.remove("A")
                if miss2:
                    rng.shuffle(after_search)
                reserve = after_search[0] in ("N","P")

        counts[0] += two
        counts[1] += reserve
        counts[2] += three
        counts[3] += reserve or three

    return tuple(x / trials for x in counts)


def main() -> None:
    cases = [(0,0,4,True),(1,3,0,True),(4,0,0,True),
             (0,0,4,False),(1,3,0,False),(4,0,0,False)]
    rows = []
    for vip,nest,poffin,eligible in cases:
        mc = estimate(vip,nest,poffin,eligible)
        exact = continuation_access(vip,nest,poffin,anchor_poffin_eligible=eligible)
        assert all(abs(a-float(b)) < 0.003 for a,b in zip(mc,exact))
        rows.append({
            "vip":vip,"nest":nest,"poffin":poffin,"eligible":eligible,
            "mc_percent":[round(x*100,5) for x in mc],
            "exact_percent":[round(float(x)*100,5) for x in exact],
        })
    print(json.dumps({"trials_per_case":250_000,"seed":20261010,"rows":rows},indent=2))


if __name__ == "__main__":
    main()
