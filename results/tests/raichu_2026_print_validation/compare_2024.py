"""Exact comparison of Basic opening, all Raichu Prized and natural Raichu holding.

Compare Harto's 2024 thirteenth-place and Hosoda's 2026 fourth-place decks.
Only physical-zone probabilities, not tutoring or match success.
"""
from __future__ import annotations
import json
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "results/decks/raichu-electrode-aichi-2026/manifest.json"

def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0

def zone_probs(n: int, basics: int, targets: int,
               opening: int = 7, prizes: int = 6) -> dict[str, Fraction]:
    if not (0 < targets <= n - basics and 0 < basics <= n - targets
            and 0 < opening < n and 0 <= prizes < n - opening):
        raise ValueError("invalid source counts")
    accepted = choose(n, opening) - choose(n - basics, opening)
    if not accepted:
        raise ValueError("no valid opening")
    valid_and_unseen = choose(n-targets, opening) - choose(n-targets-basics, opening)
    return {
        "valid_opener": Fraction(accepted, choose(n, opening)),
        "all_raichu_prized": (Fraction(valid_and_unseen, accepted) *
                             Fraction(choose(prizes, targets), choose(n-opening, targets))),
        "raichu_held_after_draw": (
            1 - Fraction(valid_and_unseen, accepted) *
            Fraction(n-opening-targets, n-opening)),
    }

def physical_oracle(n: int, basics: int, targets: int, opening: int,
                    prizes: int) -> dict[str, Fraction]:
    target = set(range(targets))
    basic = set(range(targets, targets + basics))
    indices = set(range(n))
    accepted = 0
    all_prized = 0
    visibly_held = 0
    worlds = 0
    for hand in combinations(range(n), opening):
        visible = set(hand)
        if not (visible & basic):
            continue
        accepted += 1
        for prize in combinations(sorted(indices - visible), prizes):
            prize_set = set(prize)
            for draw in (indices - visible - prize_set):
                worlds += 1
                all_prized += target <= prize_set
                visibly_held += bool(target & visible) or draw in target
    return {
        "valid_opener": Fraction(accepted, choose(n, opening)),
        "all_raichu_prized": Fraction(all_prized, worlds),
        "raichu_held_after_draw": Fraction(visibly_held, worlds),
    }

def verify() -> None:
    for toy in ((9,2,1,3,2),(10,3,2,3,2),(11,4,2,4,3)):
        actual = physical_oracle(*toy)
        expected = zone_probs(*toy)
        assert actual == expected, (toy, actual, expected)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = data["cards"]
    assert data["source"]["url"] == "https://www.limitlesstcg.com/decks/list/26812"
    assert sum(row["quantity"] for row in rows) == 60
    assert sum(row["quantity"] for row in rows if row["name"] == "Alolan Raichu") == 2
    assert sum(row["quantity"] for row in rows if row["name"] == "Electrode-GX") == 3
    # 18 Pokémon minus five Stage 1s gives 13 Basic openers.
    baseline = zone_probs(60, 16, 1)  # 2024 16 Basics and one Raichu
    current = zone_probs(60, 13, 2)
    assert baseline["valid_opener"] > current["valid_opener"]
    assert baseline["all_raichu_prized"] > current["all_raichu_prized"]
    assert baseline["raichu_held_after_draw"] < current["raichu_held_after_draw"]
    print("PASS: three independent physical 7/opening-Prize-draw toy oracles")
    for title, row in (("Harto 2024", baseline), ("Hosoda 2026", current)):
        print(title + ": " + ", ".join(
            f"{key}={float(value)*100:.9f}%"
            for key, value in row.items()))
    # The 2024 list has one Raichu and two Gladion; the 2026 list has
    # two Raichu and one Gladion. All are non-Basic and all three
    # landing in the six Prizes is a necessary condition for complete
    # initial loss of both target and direct unrestricted Prize rescue.
    all_2024 = zone_probs(60, 16, 3)["all_raichu_prized"]
    all_2026 = zone_probs(60, 13, 3)["all_raichu_prized"]
    assert all_2024 < Fraction(1, 1000)
    assert all_2026 < Fraction(1, 1000)
    print(f"Harto 2024: Raichu + 2 Gladion all Prized={float(all_2024)*100:.9f}%")
    print(f"Hosoda 2026: 2 Raichu + Gladion all Prized={float(all_2026)*100:.9f}%")
    print("LIMIT: source-only physical access, no search, sequencing, knockout or match win rate")

if __name__ == "__main__":
    verify()
