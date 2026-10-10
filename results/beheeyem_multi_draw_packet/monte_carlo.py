"""Independent physical-shuffle validation for multiple blind T3 draws."""
from collections import Counter
from pathlib import Path
import json
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_multi_draw_packet import exact_multi_draw_packet


def sample(b: int, tae: int, trials: int, seed: int) -> list[float]:
    rng = random.Random(seed + b * 100 + tae)
    pool = ["B"] * b + ["T"] * tae + ["X"] * (57 - b - tae)
    successes = [0] * 6
    for _ in range(trials):
        cards = pool.copy()
        rng.shuffle(cards)
        hand = Counter(cards[:6])
        if hand["B"] == 0 or hand["T"] == 0:
            continue
        hand["B"] -= 1
        hand["T"] -= 1
        # Six Prizes are cards[6:12].
        recycled = cards[12:] + ["B", "T", "E"]
        rng.shuffle(recycled)
        for draws in range(6):
            if draws:
                hand[recycled[draws - 1]] += 1
            if hand["B"] and hand["T"]:
                successes[draws] += 1
    return [n / trials for n in successes]


def main() -> None:
    rows = []
    for b, t, trials in ((4, 4, 750_000), (2, 2, 500_000)):
        measured = sample(b, t, trials, 20261010)
        exact = [float(exact_multi_draw_packet(b, t, d)[1])
                 for d in range(6)]
        assert all(abs(a - v) < 0.00065 for a, v in zip(measured, exact))
        rows.append({"beheeyem": b, "tae": t, "trials": trials,
                     "mc_percent": [round(100 * a, 6) for a in measured],
                     "exact_percent": [round(100 * a, 6) for a in exact]})
    print(json.dumps({"seed": 20261010, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
