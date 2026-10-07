from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from interturn_bench_debt_policy import build_result, hit_probability


def main() -> None:
    result = build_result()
    mech = result["mechanical_continuation"]
    assert mech["no_spent_support_limit_1"] == (
        "play required Supporter",
        "Bench required Pokémon",
    )
    assert mech["spent_support_entry_only_limit_1"] == (
        "AZ removes spent support",
        "Bench required Pokémon",
    )
    assert mech["spent_support_plus_required_supporter_limit_1"] is None
    assert mech["spent_support_plus_required_supporter_limit_2"] == (
        "AZ removes spent support",
        "play required Supporter",
        "Bench required Pokémon",
    )

    assert hit_probability(40, 4, 2) == Fraction(5, 26)
    assert hit_probability(40, 4, 5) == Fraction(3903, 9139)
    assert hit_probability(40, 4, 6) == Fraction(22507, 45695)

    rows = result["probability_model"]["threshold_examples"]
    assert rows[1]["break_even_collision_fraction"] == "1309/7806"
    assert rows[2]["break_even_collision_fraction"] == "2992/22507"
    print("interturn_bench_debt_policy regression passed")


if __name__ == "__main__":
    main()
