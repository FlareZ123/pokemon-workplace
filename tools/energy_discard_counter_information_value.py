"""Exact toy value-of-information for an opposing Enhanced Hammer response.

The opponent's counter status is binary and has an explicitly hypothetical
probability. The printed tactical payments are fixed; utility weights are not.
"""
from __future__ import annotations

import json
from fractions import Fraction
from typing import Any


def decision_values(
    counter_probability: Fraction,
    *,
    attack_value: Fraction,
    basic_value: Fraction,
    dde_value: Fraction,
) -> dict[str, Fraction | str]:
    q = counter_probability
    w = attack_value
    v = basic_value
    s = dde_value
    if q < 0 or q > 1:
        raise ValueError("counter probability must lie in [0,1]")
    if min(w, v, s) < 0:
        raise ValueError("utility weights must be nonnegative")

    # DDE-only discard: three Basics, no immediate next Apex readiness.
    discard_dde = 3 * v
    # Two-Basic discard: one Basic plus DDE. The DDE remains ready only
    # in worlds where the opponent cannot/will not Enhanced Hammer it.
    retain_dde = v + (1 - q) * (w + s)
    no_information = max(discard_dde, retain_dde)

    # Perfect information: choose the payment separately in each
    # opponent-Hammer state, as a deliberately optimistic benchmark.
    no_counter_payoff = max(3 * v, v + w + s)
    counter_payoff = max(3 * v, v)
    perfect_information = (1 - q) * no_counter_payoff + q * counter_payoff
    assert perfect_information >= no_information

    preferred = "discard_dde" if discard_dde > retain_dde else (
        "retain_dde" if retain_dde > discard_dde else "tied"
    )
    return {
        "discard_dde_expected_utility": discard_dde,
        "retain_dde_expected_utility": retain_dde,
        "best_policy_without_signal": preferred,
        "best_expected_utility_without_signal": no_information,
        "perfect_information_upper_bound": perfect_information,
        "value_of_perfect_information": perfect_information - no_information,
    }


def _fraction_as_string(value: Fraction | str) -> str:
    return str(value)


def verify() -> dict[str, Any]:
    # Vary the counter probability and toy utility parameters. The
    # info upper bound must dominate the advance commitment in each.
    tests = 0
    for qi in range(21):
        q = Fraction(qi, 20)
        for w in (Fraction(0), Fraction(1), Fraction(10)):
            for v in (Fraction(0), Fraction(1), Fraction(3)):
                for s in (Fraction(0), Fraction(2)):
                    decision_values(q, attack_value=w, basic_value=v, dde_value=s)
                    tests += 1
    assert tests == 378
    sample = decision_values(
        Fraction(4, 5),
        attack_value=Fraction(10),
        basic_value=Fraction(1),
        dde_value=Fraction(0),
    )
    assert sample["best_policy_without_signal"] == "tied"
    assert sample["discard_dde_expected_utility"] == 3
    assert sample["retain_dde_expected_utility"] == 3
    assert sample["perfect_information_upper_bound"] == Fraction(23, 5)
    assert sample["value_of_perfect_information"] == Fraction(8, 5)

    return {
        "parameter_grid_checks": tests,
        "illustrative_q": "4/5",
        "illustrative_utility": {
            k: _fraction_as_string(v) for k, v in sample.items()
        },
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
