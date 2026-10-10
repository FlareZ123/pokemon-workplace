"""Independent physical 60-card T2 rescue versus T3 deferred tutor simulation."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_tutor_timing import exact_deferred_or_rescue


def simulate(B: int, T: int, d: int, mode: str, n: int, seed: int):
    target, payment = MODES[mode]
    rng = Random(seed)
    residual = ["B"] * B + ["T"] * T + ["C"] + ["F"] * (56-B-T)
    events = [0, 0, 0, 0]

    for _ in range(n):
        rng.shuffle(residual)
        hand = list(residual[:6])
        deck = list(residual[12:])  # middle six cards are face-down Prizes
        already = "B" in hand and "T" in hand
        rescue = False
        if not already and "C" in hand and hand.count("F") >= payment:
            target_card = None
            if "B" not in hand and "T" in hand and target in ("pokemon", "either"):
                target_card = "B"
            if "T" not in hand and "B" in hand and target in ("energy", "either"):
                target_card = "T"
            if target_card in deck:
                hand.remove("C")
                for _ in range(payment):
                    hand.remove("F")
                deck.remove(target_card)
                hand.append(target_card)
                rescue = True

        if "B" not in hand or "T" not in hand:
            continue
        events[0] += 1
        events[2] += int(rescue)
        hand.remove("B")
        hand.remove("T")
        deck.extend(("B", "T", "E"))
        rng.shuffle(deck)
        hand.extend(deck[:d])
        have_b = "B" in hand
        have_t = "T" in hand
        can_search = "C" in hand and hand.count("F") >= payment
        second = (have_b and have_t) or (
            can_search and (
                (not have_b and have_t and target in ("pokemon", "either"))
                or (have_b and not have_t and target in ("energy", "either"))
            )
        )
        events[1] += int(second)
        events[3] += int(rescue and second)

    observed = [x / n for x in events]
    expected = exact_deferred_or_rescue(B, T, d, mode)
    for x, p in zip(observed, expected):
        pv = float(p)
        sigma = sqrt(max(pv * (1-pv), 1/n) / n)
        assert abs(x-pv) < 6*sigma + 1/n, (B,T,d,mode,x,pv,sigma)
    return {"B":B,"TAE":T,"draws":d,"tutor":mode,"trials":n,"seed":seed,
            "observed_percent":[round(x*100,6) for x in observed],
            "exact_percent":[round(float(x)*100,6) for x in expected]}


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",20261010),
        (4,4,3,"mysterious_treasure",20261011),
        (1,4,2,"mysterious_treasure",20261012),
        (4,1,3,"guzma_hala",20261013),
    )
    print(json.dumps([simulate(B,T,d,mode,200_000,seed)
        for B,T,d,mode,seed in cases], indent=2))
