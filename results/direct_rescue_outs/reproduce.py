"""Reproduce and validate clean direct-out Prize-rescue access."""

from __future__ import annotations

from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from direct_rescue_outs import (  # noqa: E402
    critical_prized_probability_given_valid_start,
    first_rescue_access_probability,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    direct_out_nonstarter: int,
    cards_seen: int,
    opening_hand_size: int,
) -> tuple[float, float]:
    categories = (
        ["C"] * critical_nonstarter
        + ["G"] * rescue_nonstarter
        + ["O"] * direct_out_nonstarter
        + ["S"] * starter_cards
        + ["F"] * (
            deck_size
            - starter_cards
            - critical_nonstarter
            - rescue_nonstarter
            - direct_out_nonstarter
        )
    )

    valid = critical = access = 0
    extra_seen = cards_seen - opening_hand_size

    for order in permutations(range(deck_size)):
        opening = order[:opening_hand_size]
        if not any(categories[index] == "S" for index in opening):
            continue
        valid += 1

        prizes = order[
            opening_hand_size : opening_hand_size + prize_count
        ]
        if not any(categories[index] == "C" for index in prizes):
            continue
        critical += 1

        later = order[
            opening_hand_size + prize_count :
            opening_hand_size + prize_count + extra_seen
        ]
        exposed = opening + later

        rescue_seen = any(categories[index] == "G" for index in exposed)
        out_seen = any(categories[index] == "O" for index in exposed)

        searchable_deck = order[
            opening_hand_size + prize_count + extra_seen :
        ]
        rescue_in_deck = any(
            categories[index] == "G" for index in searchable_deck
        )

        if rescue_seen or (out_seen and rescue_in_deck):
            access += 1

    return access / critical, critical / valid


def validate() -> None:
    case = dict(
        deck_size=8,
        prize_count=2,
        starter_cards=3,
        critical_nonstarter=2,
        rescue_nonstarter=1,
        direct_out_nonstarter=1,
        cards_seen=3,
        opening_hand_size=2,
    )
    exact_access = first_rescue_access_probability(**case)
    exact_critical = critical_prized_probability_given_valid_start(
        case["deck_size"],
        case["prize_count"],
        starter_cards=case["starter_cards"],
        critical_nonstarter=case["critical_nonstarter"],
        opening_hand_size=case["opening_hand_size"],
    )
    brute_access, brute_critical = exhaustive_access(**case)

    if abs(exact_access - brute_access) > 1e-15:
        raise AssertionError((exact_access, brute_access))
    if abs(exact_critical - brute_critical) > 1e-15:
        raise AssertionError((exact_critical, brute_critical))


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        starter_cards=12,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        opening_hand_size=7,
    )

    critical = critical_prized_probability_given_valid_start(
        base["deck_size"],
        base["prize_count"],
        starter_cards=base["starter_cards"],
        critical_nonstarter=base["critical_nonstarter"],
        opening_hand_size=base["opening_hand_size"],
    )
    print(f"P(any critical Prized | valid start): {pct(critical)}")

    print("\nEight random non-Prize cards seen")
    print("clean direct outs | P(first rescue access | critical Prized)")
    for outs in range(0, 9):
        probability = first_rescue_access_probability(
            **base,
            direct_out_nonstarter=outs,
            cards_seen=8,
        )
        print(f"{outs:17d} | {pct(probability):>39}")

    print("\nExposure sensitivity")
    print("cards seen | 0 outs | 2 outs | 4 outs | 6 outs | 8 outs")
    for cards_seen in [7, 8, 10, 12, 16]:
        row = []
        for outs in [0, 2, 4, 6, 8]:
            row.append(
                first_rescue_access_probability(
                    **base,
                    direct_out_nonstarter=outs,
                    cards_seen=cards_seen,
                )
            )
        print(
            f"{cards_seen:10d} | "
            + " | ".join(f"{pct(value):>10}" for value in row)
        )


if __name__ == "__main__":
    main()
