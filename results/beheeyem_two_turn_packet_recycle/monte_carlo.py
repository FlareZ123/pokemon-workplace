"""Independent physical 57-card simulation of T2/T3 Beheeyem packet recycling."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_recycle_packet_probability import exact_packet_outcomes


def estimate(b: int, tae: int, trials: int = 500_000,
             seed: int = 20261010) -> tuple[float, float, float]:
    rng = random.Random(seed + 101 * b + tae)
    pool = ["B"] * b + ["T"] * tae + ["X"] * (57 - b - tae)
    first = recycled = discarded = 0

    for _ in range(trials):
        cards = pool.copy()
        rng.shuffle(cards)
        hand = Counter(cards[:6])
        if hand["B"] == 0 or hand["T"] == 0:
            continue
        first += 1
        hand["B"] -= 1
        hand["T"] -= 1
        # Six unknown Prizes occupy cards[6:12].
        deck = cards[12:]
        # A counterfactual where the spent B and T go to discard.
        no_recycle_draw = deck[0]
        discarded += (
            hand["B"] + (no_recycle_draw == "B") >= 1 and
            hand["T"] + (no_recycle_draw == "T") >= 1
        )
        # Actual Mysterious Noise returns the Elgyem under Beheeyem, its
        # Stage1 and attached TAE to the deck before the next draw.
        recycled_deck = deck + ["E", "B", "T"]
        rng.shuffle(recycled_deck)
        draw = recycled_deck[0]
        recycled += (
            hand["B"] + (draw == "B") >= 1 and
            hand["T"] + (draw == "T") >= 1
        )

    return first / trials, recycled / trials, discarded / trials


def main() -> None:
    rows = []
    for b, tae in ((1, 1), (1, 4), (2, 2), (3, 4), (4, 4)):
        mc = estimate(b, tae)
        exact = exact_packet_outcomes(b, tae)
        refs = (
            float(exact.first_attack),
            float(exact.two_attacks_recycled),
            float(exact.two_attacks_discard_counterfactual),
        )
        assert abs(mc[0] - refs[0]) <= .0015, (b, tae, mc, refs)
        assert all(abs(a - x) <= .0004 for a, x in zip(mc[1:], refs[1:])), (b, tae, mc, refs)
        if (b, tae) == (1, 4):
            assert abs(mc[1] - refs[1]) <= .00007
            assert mc[2] == refs[2] == 0
        rows.append({
            "beheeyem": b,
            "tae": tae,
            "mc_percent": [round(100 * v, 6) for v in mc],
            "exact_percent": [round(100 * v, 6) for v in refs],
        })
    print(json.dumps({"trials_per_case": 500_000,
                      "seed": 20261010, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
