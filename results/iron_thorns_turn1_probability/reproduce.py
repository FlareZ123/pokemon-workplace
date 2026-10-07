from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from iron_thorns_mulligan_bonus import (  # noqa: E402
    exact_probability as bonus_probability,
    matchup_adjusted_probability,
    opponent_mulligan_probability,
)
from iron_thorns_turn1_probability import (  # noqa: E402
    accepted_opening_probability,
    baseline_route,
    exact_probability,
    information_aware_route,
)


def assert_close(actual: float, expected: float, tol: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    assert_close(
        accepted_opening_probability(),
        0.3994996257446656,
    )

    baseline, baseline_parts = exact_probability(baseline_route)
    assert_close(baseline, 0.3378150571059306)
    assert_close(baseline_parts["direct"], 0.012783551339066857)
    assert_close(
        baseline_parts["guzma_hala"],
        0.32503150576686375,
    )

    informed, informed_parts = exact_probability(information_aware_route)
    assert_close(informed, 0.34008906143861073)
    assert_close(
        informed_parts["tag_call_k1_then_gladion_for_thunder"],
        0.00023008082767211687,
    )
    assert_close(
        informed_parts["tag_call_k1_then_gladion_for_dce"],
        0.00023008082767211687,
    )
    assert_close(
        informed_parts["gladion_only_for_thunder"],
        0.000906921338669032,
    )
    assert_close(
        informed_parts["gladion_only_for_dce"],
        0.000906921338669032,
    )
    assert_close(informed - baseline, 0.002274004332680123)

    expected_bonus = (
        0.34008906143861073,
        0.3788457812695931,
        0.4155138839854457,
        0.4501309200874209,
        0.4827411487803291,
        0.5133947243143232,
        0.5421469139646088,
    )
    for bonus_draws, expected in enumerate(expected_bonus):
        assert_close(bonus_probability(bonus_draws), expected)

    assert_close(opponent_mulligan_probability(4), 0.6005003742553344)
    assert_close(opponent_mulligan_probability(14), 0.1385906808712801)
    assert_close(matchup_adjusted_probability(4), 0.39378236641861847)
    assert_close(matchup_adjusted_probability(14), 0.3462706610445084)

    print("All Iron Thorns turn-one probability checks passed.")
    print("Baseline represented route:", f"{baseline:.12%}")
    print("Information-aware route:", f"{informed:.12%}")
    print("Increment:", f"{informed - baseline:.12%}")


if __name__ == "__main__":
    main()
