from __future__ import annotations

import itertools
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_setup_inference import (
    KAZUMA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
    RYOYA_IRON_NONBASIC_COUNTS,
)
from iron_thorns_named_line_probability import (
    NamedLineCounts,
    exact_named_line_probability,
)


def thunder_count(counts: dict[str, int]) -> int:
    return counts["Thunder Mountain ♢"]


def assert_published_structure(counts: dict[str, int], dce: int) -> None:
    assert counts["Tag Call"] == 2
    assert counts["Guzma & Hala"] == 2
    assert thunder_count(counts) == 1
    assert counts["Double Colorless Energy"] == dce


def brute_force_small() -> Fraction:
    cards = (
        "T1", "T2", "C1", "G1", "M1", "E1",
        "O1", "O2", "O3", "O4",
    )
    category = {card: card[0] for card in cards}
    successes = 0
    total = 0

    for opening in itertools.combinations(cards, 3):
        if not any(category[card] == "T" for card in opening):
            continue
        remaining_after_opening = tuple(
            card for card in cards if card not in opening
        )

        for prizes in itertools.combinations(remaining_after_opening, 2):
            after_prizes = tuple(
                card for card in remaining_after_opening if card not in prizes
            )
            for draw in after_prizes:
                total += 1
                hand = list(opening) + [draw]
                active = next(card for card in hand if category[card] == "T")
                hand.remove(active)
                hand_counts = Counter(category[card] for card in hand)
                deck_counts = Counter(
                    category[card]
                    for card in after_prizes
                    if card != draw
                )

                direct = hand_counts["M"] >= 1 and hand_counts["E"] >= 1
                resources_available = (
                    (hand_counts["M"] >= 1 or deck_counts["M"] >= 1)
                    and (hand_counts["E"] >= 1 or deck_counts["E"] >= 1)
                )
                gh_accessible = (
                    hand_counts["G"] >= 1
                    or (
                        hand_counts["C"] >= 1
                        and deck_counts["G"] >= 1
                    )
                )
                if direct or (resources_available and gh_accessible):
                    successes += 1

    return Fraction(successes, total)


def main() -> None:
    assert_published_structure(KAZUMA_IRON_NONBASIC_COUNTS, 1)
    assert_published_structure(RYOYA_IRON_NONBASIC_COUNTS, 3)
    assert_published_structure(KOHEI_IRON_NONBASIC_COUNTS, 1)

    one_dce = exact_named_line_probability(
        NamedLineCounts(double_colorless=1)
    )
    three_dce = exact_named_line_probability(
        NamedLineCounts(double_colorless=3)
    )

    assert math.isclose(
        float(one_dce.accepted_opening_probability),
        0.3994996257446656,
        abs_tol=1e-15,
    )
    assert math.isclose(
        float(one_dce.success_probability_given_accepted_opening),
        0.33781505710593564,
        abs_tol=1e-15,
    )
    assert math.isclose(
        float(three_dce.success_probability_given_accepted_opening),
        0.3910785062734527,
        abs_tol=1e-15,
    )

    for result in (one_dce, three_dce):
        partition = (
            result.direct_package_probability
            + result.mediated_discard_probability
            + result.mediated_no_discard_probability
            + result.unavailable_resource_probability
            + result.connector_access_failure_probability
        )
        assert partition == 1

    small = exact_named_line_probability(
        NamedLineCounts(
            iron_thorns=2,
            tag_call=1,
            guzma_hala=1,
            thunder_mountain=1,
            double_colorless=1,
            deck_size=10,
            opening_hand_size=3,
            prize_count=2,
        )
    )
    assert small.success_probability_given_accepted_opening == Fraction(563, 1680)
    assert brute_force_small() == small.success_probability_given_accepted_opening

    print("iron_thorns_named_line_probability: all assertions passed")
    print(
        "Kazuma/Kohei named line:",
        f"{float(one_dce.success_probability_given_accepted_opening):.9%}",
    )
    print(
        "Ryoya named line:",
        f"{float(three_dce.success_probability_given_accepted_opening):.9%}",
    )


if __name__ == "__main__":
    main()
