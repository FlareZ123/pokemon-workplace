"""Exhaustive independently enumerated toy worlds for opening allocation."""
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from dream_ball_muk_opening_allocation import opening_allocation


def exhaustive(n: int, b: int, d: int, h: int, p: int, k: int):
    basics = set(range(b))
    dream_balls = set(range(b, b + d))
    muk = b + d
    total = valid = hit = 0
    for hand in combinations(range(n), h):
        hand_set = set(hand)
        for prizes in combinations((x for x in range(n) if x not in hand_set), p):
            prize_set = set(prizes)
            for awarded in combinations(prizes, k):
                total += 1
                is_valid = bool(hand_set & basics)
                valid += int(is_valid)
                hit += int(
                    is_valid and muk not in hand_set and muk not in prize_set
                    and bool(set(awarded) & dream_balls)
                )
    return Fraction(valid, total), Fraction(hit, total), Fraction(hit, valid)


def test() -> None:
    for params in (
        (10, 3, 2, 2, 3, 1),
        (12, 4, 3, 3, 3, 2),
        (11, 2, 1, 3, 3, 3),
    ):
        model = opening_allocation(
            deck_size=params[0], basic_count=params[1],
            dream_ball_count=params[2], opening_hand=params[3],
            prize_count=params[4], prizes_awarded=params[5],
        )
        brute = exhaustive(*params)
        assert model == brute, (params, model, brute)

    results = []
    for balls in (1, 2, 3, 4):
        for k in (1, 2, 3, 6):
            valid, joint, given_valid = opening_allocation(
                deck_size=60, basic_count=14, dream_ball_count=balls,
                opening_hand=7, prize_count=6, prizes_awarded=k,
            )
            assert 0 < joint < given_valid < 1
            results.append({
                "dream_balls": balls, "random_awarded_prizes": k,
                "unconditional_percent": round(float(joint) * 100, 6),
                "conditional_valid_percent": round(float(given_valid) * 100, 6),
            })
    assert results[0]["conditional_valid_percent"] == 1.344856
    assert results[-1]["conditional_valid_percent"] == 28.271322
    print(json.dumps({
        "toy_exact_checks": 3,
        "valid_opening_percent": round(float(valid) * 100, 6),
        "scenarios": results,
        "status": "PASS",
    }, indent=2))


if __name__ == "__main__":
    test()
