from __future__ import annotations

import itertools
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from mulligan_information_leakage import (  # noqa: E402
    MulliganModel,
    build_examples,
    conditional_diagnostic_count_given_mulligan,
    diagnostic_seen_given_mulligan,
    ever_diagnostic_before_acceptance,
    exact_mulligan_count_probability,
    mulligan_probability,
    posterior_from_mulligan_count,
    posterior_from_revealed_sequence,
    rejected_hand_exact_diagnostic_probability,
)


def exhaustive_rejected_hand_distribution(model: MulliganModel) -> dict[int, float]:
    cards = (
        [("B", i) for i in range(model.forced_basics)]
        + [("D", i) for i in range(model.diagnostic_cards)]
        + [
            ("F", i)
            for i in range(
                model.deck_size - model.forced_basics - model.diagnostic_cards
            )
        ]
    )
    total = math.comb(model.deck_size, model.hand_size)
    counts: Counter[int] = Counter()
    for hand in itertools.combinations(cards, model.hand_size):
        if any(kind == "B" for kind, _ in hand):
            continue
        diagnostic_count = sum(kind == "D" for kind, _ in hand)
        counts[diagnostic_count] += 1
    return {count: ways / total for count, ways in counts.items()}


def assert_close(actual: float, expected: float, tol: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    small = MulliganModel(
        "small", forced_basics=2, diagnostic_cards=2, deck_size=10, hand_size=3
    )
    exhaustive = exhaustive_rejected_hand_distribution(small)
    for diagnostic_count in range(0, 4):
        assert_close(
            rejected_hand_exact_diagnostic_probability(small, diagnostic_count),
            exhaustive.get(diagnostic_count, 0.0),
        )

    assert_close(sum(exhaustive.values()), mulligan_probability(small))
    conditional_total = sum(
        conditional_diagnostic_count_given_mulligan(small, count)
        for count in range(0, 4)
    )
    assert_close(conditional_total, 1.0)

    low_basic = MulliganModel("4-Basic candidate", 4, 4)
    high_basic = MulliganModel("12-Basic candidate", 12, 4)
    assert_close(mulligan_probability(low_basic), 0.6005003742553344)
    assert_close(mulligan_probability(high_basic), 0.1906466927107365)
    assert_close(diagnostic_seen_given_mulligan(low_basic), 0.4231370306842005)
    assert_close(diagnostic_seen_given_mulligan(high_basic), 0.47954568814883336)
    assert_close(ever_diagnostic_before_acceptance(low_basic), 0.3887644501857918)
    assert_close(ever_diagnostic_before_acceptance(high_basic), 0.10149436388352479)

    posteriors = {
        k: posterior_from_mulligan_count((low_basic, high_basic), k)[low_basic.name]
        for k in (0, 1, 2, 3, 5)
    }
    expected_posteriors = {
        0: 0.33047826979417416,
        1: 0.6085731846317793,
        2: 0.8304274821603669,
        3: 0.939117868005863,
        5: 0.9935080803082637,
    }
    for k, expected in expected_posteriors.items():
        assert_close(posteriors[k], expected)
        assert_close(
            exact_mulligan_count_probability(low_basic, k),
            mulligan_probability(low_basic) ** k
            * (1.0 - mulligan_probability(low_basic)),
        )

    four_copy = MulliganModel("4-copy diagnostic", 4, 4)
    two_copy = MulliganModel("2-copy diagnostic", 4, 2)
    content_posteriors = {
        "one": posterior_from_revealed_sequence(
            (four_copy, two_copy), (1,)
        )[four_copy.name],
        "one_one": posterior_from_revealed_sequence(
            (four_copy, two_copy), (1, 1)
        )[four_copy.name],
        "two": posterior_from_revealed_sequence(
            (four_copy, two_copy), (2,)
        )[four_copy.name],
        "zero_zero": posterior_from_revealed_sequence(
            (four_copy, two_copy), (0, 0)
        )[four_copy.name],
    }
    expected_content = {
        "one": 0.611879576891782,
        "one_one": 0.7130901236140237,
        "two": 0.8313891834570519,
        "zero_zero": 0.36332214249692657,
    }
    for key, expected in expected_content.items():
        assert_close(content_posteriors[key], expected)

    singleton = MulliganModel("singleton", 4, 1)
    assert_close(diagnostic_seen_given_mulligan(singleton), 0.125)
    assert_close(ever_diagnostic_before_acceptance(singleton), 0.15817220825309716)

    payload = build_examples()
    assert payload["density_examples"]
    print("All mulligan information leakage checks passed.")
    print(
        "Exact low-Basic posterior after 3 mulligans:",
        f"{posteriors[3]:.12%}",
    )
    print(
        "Ever reveal 4-copy diagnostic before acceptance, 4 Basics:",
        f"{ever_diagnostic_before_acceptance(low_basic):.12%}",
    )


if __name__ == "__main__":
    main()
