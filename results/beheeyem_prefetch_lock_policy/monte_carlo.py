"""Independent physical-card Monte Carlo of K1 prefetch under future lock."""
import json
from fractions import Fraction
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_prefetch_lock_policy import (
    blind_packet, held_tutor_packet, prefetch_targets, exact_prefetch_policy,
)


def simulate(B: int, T: int, d: int, mode: str, q: Fraction, n: int, seed: int):
    target, cost = MODES[mode]
    rng = Random(seed)
    original = ["B"]*B + ["T"]*T + ["C"] + ["F"]*(56-B-T)
    first = both = prefetched = 0

    for _ in range(n):
        rng.shuffle(original)
        hand = list(original[:6])
        # Six physical Prize cards are positions 6..11.
        deck = list(original[12:])
        direct = "B" in hand and "T" in hand

        if direct and "C" in hand and hand.count("F") >= cost:
            db, dt = deck.count("B")+1, deck.count("T")+1
            options = prefetch_targets(hand.count("B"),hand.count("T"),db,dt,d,mode)
            if options:
                hb, ht = hand.count("B")-1, hand.count("T")-1
                blind = blind_packet(hb,ht,db,dt,48,d)
                open_search = held_tutor_packet(hb,ht,db,dt,d,mode)
                defer = (1-q)*open_search + q*blind
                choice = max(options, key=options.get)
                if options[choice] > defer:
                    hand.remove("C")
                    for _ in range(cost):
                        hand.remove("F")
                    deck.remove(choice)
                    hand.append(choice)
                    prefetched += 1

        if not direct and "C" in hand and hand.count("F") >= cost:
            missing = None
            if "B" not in hand and "T" in hand and target in ("pokemon","either"):
                missing = "B"
            elif "T" not in hand and "B" in hand and target in ("energy","either"):
                missing = "T"
            if missing in deck:
                deck.remove(missing)
                hand.remove("C")
                for _ in range(cost):
                    hand.remove("F")
                hand.append(missing)

        if "B" not in hand or "T" not in hand:
            continue
        first += 1
        hand.remove("B")
        hand.remove("T")
        deck.extend(("B","T","E"))
        rng.shuffle(deck)
        hand.extend(deck[:d])

        blocked = rng.random() < float(q)
        hb, ht = "B" in hand, "T" in hand
        available = not blocked and "C" in hand and hand.count("F") >= cost
        success = (hb and ht) or (
            available and (
                (not hb and ht and target in ("pokemon","either"))
                or (hb and not ht and target in ("energy","either"))
            )
        )
        both += int(success)

    observed = (first/n, both/n)
    expected = exact_prefetch_policy(B,T,d,mode,q)
    for x,p in zip(observed,(expected[0],expected[2])):
        p=float(p)
        sigma=sqrt(max(p*(1-p),1/n)/n)
        assert abs(x-p) < 6*sigma + 1/n, (B,T,d,mode,q,x,p,sigma)
    return {"B":B,"TAE":T,"draws":d,"mode":mode,"denial":str(q),
            "trials":n,"seed":seed,"prefetched_trials":prefetched,
            "observed_percent":[round(x*100,6) for x in observed],
            "exact_percent":[round(float(x)*100,6) for x in (expected[0],expected[2])]}


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",Fraction(1),20261010),
        (4,4,1,"computer_search",Fraction(1,10),20261011),
        (4,4,2,"ultra_ball",Fraction(0),20261012),
        (1,4,1,"mysterious_treasure",Fraction(1),20261013),
    )
    print(json.dumps([simulate(B,T,d,mode,q,200_000,seed)
        for B,T,d,mode,q,seed in cases], indent=2))
