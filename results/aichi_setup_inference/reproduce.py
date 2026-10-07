from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_setup_inference import (  # noqa: E402
    ExactListCandidate,
    common_only_given_mulligan,
    exact_count_classification_accuracy,
    family_unique_content_classification_accuracy,
    mulligan_probability,
    posterior_left_after_exact_mulligans,
    unique_content_classification_accuracy,
    unique_name_exposed_before_acceptance,
)


def assert_close(actual: float, expected: float, tol: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    vileplume = ExactListCandidate(
        "Takahiro Ando Vileplume Control",
        forced_basics=14,
        common_nonbasic_cards=16,
    )
    iron_thorns = ExactListCandidate(
        "Kazuma Kashi Iron Thorns",
        forced_basics=4,
        common_nonbasic_cards=17,
    )

    assert_close(mulligan_probability(vileplume), 0.1385906808712801)
    assert_close(mulligan_probability(iron_thorns), 0.6005003742553344)

    expected_iron_posteriors = (
        0.31683463533901846,
        0.6677178962428857,
        0.8969808734091667,
        0.9741777759679516,
        0.9939196657149556,
        0.9985901134063959,
    )
    for mulligans, expected in enumerate(expected_iron_posteriors):
        actual = 1.0 - posterior_left_after_exact_mulligans(
            vileplume,
            iron_thorns,
            mulligans,
        )
        assert_close(actual, expected)

    assert_close(
        common_only_given_mulligan(vileplume),
        0.00021373317878780406,
    )
    assert_close(
        common_only_given_mulligan(iron_thorns),
        0.0000838574423480084,
    )

    assert_close(
        unique_name_exposed_before_acceptance(vileplume),
        0.13856516394236412,
    )
    assert_close(
        unique_name_exposed_before_acceptance(iron_thorns),
        0.6004802558690977,
    )

    count_accuracy = exact_count_classification_accuracy(vileplume, iron_thorns)
    content_accuracy = unique_content_classification_accuracy(
        vileplume,
        iron_thorns,
    )

    assert_close(count_accuracy, 0.7309548466920271)
    assert_close(content_accuracy, 0.8002401280631699)
    assert_close(
        content_accuracy - count_accuracy,
        0.06928528137114276,
    )

    family_vileplume = ExactListCandidate(
        "Vileplume vs Iron family",
        forced_basics=14,
        common_nonbasic_cards=18,
    )
    iron_family = (
        ExactListCandidate("Kazuma", 4, 17),
        ExactListCandidate("Ryoya", 4, 16),
        ExactListCandidate("Kohei", 4, 17),
    )
    family_accuracy = family_unique_content_classification_accuracy(
        family_vileplume,
        iron_family,
    )
    assert_close(family_accuracy, 0.8002415086490129)

    print("All Aichi setup inference checks passed.")
    print("Count-only accuracy:", f"{count_accuracy:.12%}")
    print("Coarse content accuracy:", f"{content_accuracy:.12%}")
    print(
        "Increment from content:",
        f"{content_accuracy - count_accuracy:.12%}",
    )
    print("Three-list Iron family accuracy:", f"{family_accuracy:.12%}")


if __name__ == "__main__":
    main()
