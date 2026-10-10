"""Independent shuffled-card Monte Carlo for KO-awarded Prizes in Beheeyem loop."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES
from beheeyem_prize_packet import exact_prize_take


def simulate(B: int, T: int, d: int, mode: str, awarded: int,
             trials: int, seed: int) -> dict:
    target, payment = MODES[mode]
    rng = Random(seed)
    residual = ["B"]*B + ["T"]*T + ["C"] + ["F"]*(56-B-T)
    events = [0, 0, 0, 0]

    for _ in range(trials):
        rng.shuffle(residual)
        hand = list(residual[:6])
        prizes = list(residual[6:12])
        deck = list(residual[12:])
        direct = "B" in hand and "T" in hand
        rescued = False
        if not direct and "C" in hand and hand.count("F") >= payment:
            missing = None
            if "B" not in hand and "T" in hand and target in ("pokemon","either"):
                missing = "B"
            elif "T" not in hand and "B" in hand and target in ("energy","either"):
                missing = "T"
            if missing in deck:
                deck.remove(missing)
                hand.remove("C")
                for _ in range(payment):
                    hand.remove("F")
                hand.append(missing)
                rescued = True

        if "B" not in hand or "T" not in hand:
            continue
        events[0] += 1
        hand.remove("B")
        hand.remove("T")
        deck.extend(("B", "T", "E"))
        assert len(deck) == (47 if rescued else 48)

        rng.shuffle(prizes)
        hand.extend(prizes[:awarded])
        rng.shuffle(deck)
        hand.extend(deck[:d])
        has_b, has_t = "B" in hand, "T" in hand
        can_tutor = "C" in hand and hand.count("F") >= payment
        complete = (has_b and has_t) or (
            can_tutor and (
                (not has_b and has_t and target in ("pokemon","either"))
                or (has_b and not has_t and target in ("energy","either"))
            )
        )
        events[1 if direct else 2] += int(complete)
        events[3] += int(complete)

    observed = [v / trials for v in events]
    exact = exact_prize_take(B, T, d, mode, awarded)
    for o,p in zip(observed, exact):
        pv = float(p)
        sigma = sqrt(max(pv*(1-pv),1/trials)/trials)
        assert abs(o-pv) < 6*sigma + 1/trials, (
            B,T,d,mode,awarded,o,pv,sigma
        )
    return {
        "B":B,"TAE":T,"T3_draws":d,"tutor":mode,
        "Prizes_awarded":awarded,"trials":trials,"seed":seed,
        "observed_percent":[round(o*100,6) for o in observed],
        "exact_percent":[round(float(p)*100,6) for p in exact]
    }


if __name__ == "__main__":
    cases = (
        (4,4,1,"computer_search",1,20261010),
        (4,4,1,"computer_search",2,20261011),
        (1,4,1,"mysterious_treasure",1,20261012),
        (4,1,3,"guzma_hala",2,20261013),
    )
    print(json.dumps([
        simulate(B,T,d,mode,r,200_000,seed)
        for B,T,d,mode,r,seed in cases
    ],indent=2))
