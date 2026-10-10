"""Independent physical-hand-bottoming Monte Carlo of opposing Iono after Prize award."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_iono_prize import exact_iono_after_prizes


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


def simulate(B: int, T: int, d: int, mode: str, awards: int,
             trials: int, seed: int) -> dict:
    target, payment = MODES[mode]
    rng = Random(seed)
    pool = ["B"]*B+["T"]*T+["C"]+["F"]*(56-B-T)
    first = direct_second = rescue_second = 0

    for _ in range(trials):
        rng.shuffle(pool)
        hand = list(pool[:6])
        prizes = list(pool[6:12])
        deck = list(pool[12:])
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
        first += 1
        hand.remove("B")
        hand.remove("T")
        deck.extend(("B","T","E"))
        assert len(deck) == (48 if direct else 47)

        rng.shuffle(prizes)
        hand.extend(prizes[:awards])
        rng.shuffle(hand)
        rng.shuffle(deck)
        deck.extend(hand)  # opposing Iono puts current player hand at bottom
        hand = []
        iono_draw = 6-awards
        hand.extend(deck[:iono_draw])
        hand.extend(deck[iono_draw:iono_draw+d])
        # No consumed Supporter or other action costs on our T3.
        success = can_complete(hand,mode)
        if success and direct:
            direct_second += 1
        if success and not direct:
            rescue_second += 1

    observed = [
        first/trials,direct_second/trials,rescue_second/trials,
        (direct_second+rescue_second)/trials
    ]
    expected = exact_iono_after_prizes(B,T,d,mode,awards)
    for o,p in zip(observed,expected):
        pv = float(p)
        sigma = sqrt(max(pv*(1-pv),1/trials)/trials)
        assert abs(o-pv) < 6*sigma + 1/trials, (
            B,T,d,mode,awards,o,pv,sigma
        )
    return {
        "B":B,"TAE":T,"T3_natural_draws":d,"tutor":mode,
        "Prizes_awarded":awards,"trials":trials,"seed":seed,
        "observed_percent":[round(o*100,6) for o in observed],
        "exact_percent":[round(float(p)*100,6) for p in expected]
    }


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",0,20261010),
        (4,4,1,"computer_search",1,20261011),
        (4,4,1,"computer_search",2,20261012),
        (1,4,2,"mysterious_treasure",2,20261013),
    )
    print(json.dumps([
        simulate(B,T,d,mode,r,200_000,seed)
        for B,T,d,mode,r,seed in cases
    ],indent=2))
