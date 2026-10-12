"""Source-checked natural Regidrago V / Guzma / VSTAR draw event."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
import json
from pathlib import Path

from tools.regidrago_legacy_star_launch import launch
from results.aichi_regidrago_gust_deadlines.reproduce import validate_prints


def physical_oracle(other: int, v: int, star: int, guzma: int,
                    total: int = 10, hand_size: int = 3, prizes: int = 2
                    ) -> Fraction:
    """Enumerate independently labeled opening, Prizes and ordered draws."""
    deck = (["B"] * other + ["V"] * v + ["S"] * star +
            ["G"] * guzma + ["F"] * (total - other - v - star - guzma))
    ids = set(range(total))
    accepted = successes = 0
    for opening_ids in combinations(range(total), hand_size):
        opening = [deck[i] for i in opening_ids]
        if "B" not in opening and "V" not in opening:
            continue
        remainder = ids - set(opening_ids)
        for prized in combinations(sorted(remainder), prizes):
            available_deck = remainder - set(prized)
            for draw1, draw2 in permutations(sorted(available_deck), 2):
                accepted += 1
                turn1 = opening + [deck[draw1]]
                turn2 = turn1 + [deck[draw2]]
                if "V" in turn1 and "G" in turn1 and "S" in turn2:
                    successes += 1
    return Fraction(successes, accepted)


def verify() -> None:
    validate_prints()
    root = Path(__file__).resolve().parents[2]
    rows = json.loads((root / "results" / "competitive_deck_baselines" /
                      "regidrago_haruku_2026.json").read_text(
                          encoding="utf-8"))["cards"]
    qty = {row["name"]: row["quantity"] for row in rows}
    assert qty["Regidrago V"] == 4
    assert qty["Regidrago VSTAR"] == 3
    assert qty["Guzma"] == 2

    vstar_cards = json.loads(
        (root / "resources" / "cards" / "en" / "swsh12.json")
        .read_text(encoding="utf-8"))
    star = next(row for row in vstar_cards if row["id"] == "swsh12-136")
    basic = next(row for row in vstar_cards if row["id"] == "swsh12-135")
    assert star["name"] == "Regidrago VSTAR"
    assert basic["name"] == "Regidrago V"
    assert "Basic" in basic["subtypes"]
    assert any(a["name"] == "Legacy Star" and
               "up to 2 cards from your discard pile" in a["text"]
               for a in star["abilities"])

    for other in (1, 2):
        for star_count in (1, 2):
            for g in (1, 2):
                exact = launch(other, 2, star_count, g,
                               total=10, hand_size=3, prize_count=2)
                physical = physical_oracle(other, 2, star_count, g)
                assert exact == physical, (
                    other, star_count, g, exact, physical)
    print("PASS: 8 independent labeled toy-zone physical oracles")
    baseline = launch(11, 4, 3, 2)
    variant = launch(11, 4, 3, 1)
    assert baseline > variant
    print(f"Published 2-Guzma natural launch: {float(baseline*100):.9f}%")
    print(f"Experimental 1-Guzma natural launch: {float(variant*100):.9f}%")
    print(f"Loss: {float((baseline-variant)*100):.9f} percentage points")
    print("PASS: natural V+Guzma T1 and VSTAR T2 scenario print proof")


if __name__ == "__main__":
    verify()
