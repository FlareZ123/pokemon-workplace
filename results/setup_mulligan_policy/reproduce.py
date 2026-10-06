"""Reproduce optional-setup mulligan-policy findings and exact validations."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.setup_eligibility import build_setup_catalog  # noqa: E402
from tools.setup_mulligan_policy import (  # noqa: E402
    conditioned_prize_class_distribution,
    expected_mulligans_before_acceptance,
    mulligan_count_probability,
    mulligan_tail_probability,
    opening_acceptance,
    specific_card_prize_probability,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_distribution(
    deck_size: int,
    prize_count: int,
    hand_size: int,
    forced: int,
    optional: int,
    q: float,
) -> dict[tuple[int, int, int], float]:
    classes = [0] * forced + [1] * optional + [2] * (deck_size - forced - optional)
    all_cards = set(range(deck_size))
    weights: dict[tuple[int, int, int], float] = {}
    total_weight = 0.0
    for hand_tuple in combinations(range(deck_size), hand_size):
        hand = set(hand_tuple)
        has_forced = any(classes[i] == 0 for i in hand)
        has_optional = any(classes[i] == 1 for i in hand)
        weight = 1.0 if has_forced else q if has_optional else 0.0
        if weight == 0.0:
            continue
        remaining = all_cards - hand
        for prize_tuple in combinations(sorted(remaining), prize_count):
            counts = [0, 0, 0]
            for i in prize_tuple:
                counts[classes[i]] += 1
            key = tuple(counts)
            weights[key] = weights.get(key, 0.0) + weight
            total_weight += weight
    return {key: value / total_weight for key, value in weights.items()}


def validate() -> None:
    cases = [
        (9, 2, 3, 2, 2, 0.0),
        (9, 2, 3, 2, 2, 1.0),
        (10, 3, 3, 3, 2, 0.25),
        (10, 3, 4, 2, 3, 0.75),
    ]
    for deck, prizes, hand, forced, optional, q in cases:
        exact = dict(
            conditioned_prize_class_distribution(
                deck,
                prizes,
                forced_starters=forced,
                optional_starters=optional,
                opening_hand_size=hand,
                optional_only_acceptance=q,
            )
        )
        brute = exhaustive_distribution(deck, prizes, hand, forced, optional, q)
        if set(exact) != set(brute):
            raise AssertionError((deck, prizes, hand, forced, optional, q, set(exact), set(brute)))
        for key in exact:
            if abs(exact[key] - brute[key]) > 1e-14:
                raise AssertionError((deck, prizes, hand, forced, optional, q, key, exact[key], brute[key]))
        if abs(sum(exact.values()) - 1.0) > 1e-14:
            raise AssertionError((deck, prizes, hand, forced, optional, q, sum(exact.values())))

    # Mulligan counts are geometric under a fixed policy.
    for forced, optional, q in [(1, 4, 0.0), (1, 4, 1.0), (4, 4, 0.5)]:
        first_500 = sum(
            mulligan_count_probability(
                60, forced, optional, k, optional_only_acceptance=q
            )
            for k in range(500)
        )
        if abs(first_500 - 1.0) > 1e-14:
            raise AssertionError((forced, optional, q, first_500))
        for minimum in [0, 1, 3, 5, 10]:
            tail = sum(
                mulligan_count_probability(
                    60, forced, optional, k, optional_only_acceptance=q
                )
                for k in range(minimum, 500)
            )
            exact_tail = mulligan_tail_probability(
                60, forced, optional, minimum, optional_only_acceptance=q
            )
            if abs(tail - exact_tail) > 1e-14:
                raise AssertionError((forced, optional, q, minimum, tail, exact_tail))

    # With q=1, forced and optional cards are symmetric: acceptance is simply
    # "at least one card from the combined starter pool".
    for forced, optional in [(2, 3), (4, 4), (8, 4)]:
        pf = specific_card_prize_probability(
            60, 6, forced_starters=forced, optional_starters=optional,
            card_class="forced", optional_only_acceptance=1.0
        )
        po = specific_card_prize_probability(
            60, 6, forced_starters=forced, optional_starters=optional,
            card_class="optional", optional_only_acceptance=1.0
        )
        if abs(pf - po) > 1e-15:
            raise AssertionError((forced, optional, pf, po))


def main() -> None:
    validate()
    catalog = build_setup_catalog(ROOT / "resources")
    print("Setup exception catalog")
    print("legal prints", catalog.legal_print_count)
    print("legal Basic prints", catalog.legal_basic_print_count)
    print("forced Basic prints", catalog.forced_basic_count())
    for row in catalog.optional_exceptions:
        print("OPTIONAL", row.card_id, row.name, row.ability_name, "second-only" if row.requires_going_second else "both")
    for row in catalog.forbidden_basic_exceptions:
        print("FORBIDDEN", row.card_id, row.name, row.ability_name)

    print("\nFour forced Basics + four optional setup cards")
    print("policy q | accept/attempt | expected mulligans | forced Prize | optional Prize | other Prize")
    for q in [0.0, 0.25, 0.5, 0.75, 1.0]:
        a = opening_acceptance(60, 4, 4, optional_only_acceptance=q)
        em = expected_mulligans_before_acceptance(60, 4, 4, optional_only_acceptance=q)
        pf = specific_card_prize_probability(60, 6, forced_starters=4, optional_starters=4, card_class="forced", optional_only_acceptance=q)
        po = specific_card_prize_probability(60, 6, forced_starters=4, optional_starters=4, card_class="optional", optional_only_acceptance=q)
        pn = specific_card_prize_probability(60, 6, forced_starters=4, optional_starters=4, card_class="other", optional_only_acceptance=q)
        print(f"{q:8.2f} | {pct(a.accepted):>14} | {em:18.6f} | {pct(pf):>12} | {pct(po):>14} | {pct(pn):>11}")

    print("\nMulligan tail: chance opponent can choose at least this many bonus draws if they did not mulligan")
    print("forced optional q | >=1 | >=3 | >=5 | >=10")
    for forced, optional, q in [(4,4,0.0),(4,4,1.0),(1,4,0.0),(1,4,1.0)]:
        tails = [
            mulligan_tail_probability(
                60, forced, optional, minimum, optional_only_acceptance=q
            )
            for minimum in [1,3,5,10]
        ]
        print(f"{forced:6d} {optional:8d} {q:3.1f} | " + " | ".join(f"{pct(value):>10}" for value in tails))

    print("\nBoundary-policy sensitivity by forced/optional counts")
    print("forced optional | accept q=0 | accept q=1 | mulligans q=0 | mulligans q=1 | optional Prize q=0 | optional Prize q=1")
    for forced, optional in [(2,4),(4,4),(6,4),(8,4),(12,4)]:
        a0=opening_acceptance(60,forced,optional,optional_only_acceptance=0).accepted
        a1=opening_acceptance(60,forced,optional,optional_only_acceptance=1).accepted
        m0=expected_mulligans_before_acceptance(60,forced,optional,optional_only_acceptance=0)
        m1=expected_mulligans_before_acceptance(60,forced,optional,optional_only_acceptance=1)
        o0=specific_card_prize_probability(60,6,forced_starters=forced,optional_starters=optional,card_class="optional",optional_only_acceptance=0)
        o1=specific_card_prize_probability(60,6,forced_starters=forced,optional_starters=optional,card_class="optional",optional_only_acceptance=1)
        print(f"{forced:6d} {optional:8d} | {pct(a0):>10} | {pct(a1):>10} | {m0:13.6f} | {m1:13.6f} | {pct(o0):>18} | {pct(o1):>18}")


if __name__ == "__main__":
    main()
