from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from typed_bench_release_execution import build_result, repeated_coin_release_success


def main() -> None:
    result = build_result()
    mech = result["mechanical_same_turn_collision"]
    assert mech["supporter_limit_1"] is None
    assert mech["supporter_limit_2"] is not None
    assert mech["deterministic_item"] is not None
    assert mech["deterministic_item_under_item_lock"] is None
    assert mech["coin_item_heads_branch"] is not None
    assert mech["attack_release"] is None
    assert mech["ability_release_ready"] is not None
    assert mech["ability_release_not_ready"] is None

    assert repeated_coin_release_success(0) == Fraction(0, 1)
    assert repeated_coin_release_success(1) == Fraction(1, 2)
    assert repeated_coin_release_success(2) == Fraction(3, 4)
    assert repeated_coin_release_success(3) == Fraction(7, 8)

    rows = result["coin_release_probability"]["super_scoop_up_attempts"]
    assert rows[1]["break_even_collision_fraction"] == "1309/3903"
    assert rows[2]["break_even_collision_fraction"] == "2618/3903"
    assert rows[3]["support_wins_for_all_collision_probabilities"] is True
    print("typed_bench_release_execution regression passed")


if __name__ == "__main__":
    main()
