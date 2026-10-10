"""Independent physical simulation of Iono, N and Marnie opposing replies."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_supporter_reset import exact_supporter_reset


def can_complete(hand: list[str], mode: str) -> bool:
    target, payment = MODES[mode]
    b, t = "B" in hand, "T" in hand
    if b and t:
        return True
    if "C" not in hand or hand.count("F") + hand.count("E") < payment:
        return False
    return (
        (not b and t and target in ("pokemon","either"))
        or (b and not t and target in ("energy","either"))
    )


def simulate(B: int,T: int,d: int,mode: str,r: int,
             supporter: str,trials: int,seed: int):
    target,payment = MODES[mode]
    rng = Random(seed)
    original = ["B"]*B + ["T"]*T + ["C"] + ["F"]*(56-B-T)
    events = [0,0,0,0]

    for _ in range(trials):
        rng.shuffle(original)
        hand = list(original[:6])
        prizes = list(original[6:12])
        deck = list(original[12:])
        direct = "B" in hand and "T" in hand

        if not direct and "C" in hand and hand.count("F") >= payment:
            missing = None
            if "B" not in hand and "T" in hand and target in ("pokemon","either"):
                missing = "B"
            elif "T" not in hand and "B" in hand and target in ("energy","either"):
                missing = "T"
            if missing in deck:
                hand.remove("C")
                for _ in range(payment):
                    hand.remove("F")
                deck.remove(missing)
                hand.append(missing)

        if "B" not in hand or "T" not in hand:
            continue
        events[0] += 1
        hand.remove("B")
        hand.remove("T")
        deck.extend(("B","T","E"))
        assert len(deck) == (48 if direct else 47)
        rng.shuffle(prizes)
        hand.extend(prizes[:r])

        if supporter == "N":
            deck.extend(hand)
            rng.shuffle(deck)  # physical shuffled hand joins deck
            sample_count = 6-r+d
        else:
            rng.shuffle(hand)
            rng.shuffle(deck)
            deck.extend(hand)  # shuffled hand is physically at bottom
            sample_count = (6-r if supporter == "Iono" else 4)+d

        next_hand = deck[:sample_count]
        success = can_complete(next_hand,mode)
        events[1 if direct else 2] += int(success)
        events[3] += int(success)

    observed = [x/trials for x in events]
    expected = exact_supporter_reset(B,T,d,mode,r,supporter)
    for o,p in zip(observed,expected):
        pv = float(p)
        sigma = sqrt(max(pv*(1-pv),1/trials)/trials)
        assert abs(o-pv) < 6*sigma + 1/trials, (
            B,T,d,mode,r,supporter,o,pv,sigma
        )
    return {
        "B":B,"TAE":T,"draws":d,"tutor":mode,
        "Prizes_awarded":r,"opposing_Supporter":supporter,
        "trials":trials,"seed":seed,
        "observed_percent":[round(o*100,6) for o in observed],
        "exact_percent":[round(float(p)*100,6) for p in expected]
    }


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",0,"N",20261010),
        (4,4,1,"computer_search",1,"N",20261011),
        (4,4,1,"computer_search",2,"N",20261012),
        (4,4,1,"computer_search",2,"Marnie",20261013),
        (1,4,2,"mysterious_treasure",1,"Iono",20261014),
    )
    print(json.dumps([
        simulate(B,T,d,mode,r,supporter,200_000,seed)
        for B,T,d,mode,r,supporter,seed in cases
    ],indent=2))
