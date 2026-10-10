"""Independent physical-shuffle Monte Carlo of one-copy search-tutor packet access."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_physical_tutor import MODES, exact_physical_tutor


def simulate(B: int, T: int, d: int, mode: str, trials: int, seed: int):
    target, payment = MODES[mode]
    rng = Random(seed)
    residual = ["B"] * B + ["T"] * T + ["C"] + ["F"] * (56 - B - T)
    events = [0, 0, 0]

    for _ in range(trials):
        rng.shuffle(residual)
        hand = list(residual[:6])
        # Prize cards are the following six physical positions.
        if "B" not in hand or "T" not in hand:
            continue
        events[0] += 1
        hand.remove("B")
        hand.remove("T")
        deck = list(residual[12:])
        deck.extend(("B", "T", "E"))  # the attacked evolutionary stack
        rng.shuffle(deck)
        hand.extend(deck[:d])
        haveB = "B" in hand
        haveT = "T" in hand
        complete = haveB and haveT
        can_pay = "C" in hand and hand.count("F") >= payment
        searchable = (
            (not haveB and haveT and target in ("pokemon", "either"))
            or (haveB and not haveT and target in ("energy", "either"))
        )
        events[1] += int(complete)
        events[2] += int(complete or (can_pay and searchable))

    observed = [count / trials for count in events]
    expected = exact_physical_tutor(B, T, d, mode)[:3]
    for x, p in zip(observed, expected):
        pv = float(p)
        sigma = sqrt(max(pv * (1 - pv), 1 / trials) / trials)
        assert abs(x - pv) < 6 * sigma + 1 / trials, (
            B, T, d, mode, x, pv, sigma
        )
    return {
        "B": B, "TAE": T, "draws": d, "tutor": mode, "trials": trials,
        "seed": seed, "observed_percent": [round(v * 100, 6) for v in observed],
        "exact_percent": [round(float(v) * 100, 6) for v in expected],
    }


if __name__ == "__main__":
    cases = (
        (4, 4, 1, "computer_search", 20261010),
        (4, 4, 3, "computer_search", 20261011),
        (1, 4, 1, "mysterious_treasure", 20261012),
        (4, 1, 2, "guzma_hala", 20261013),
    )
    print(json.dumps([simulate(B, T, d, mode, 200_000, seed)
                      for B, T, d, mode, seed in cases], indent=2))
