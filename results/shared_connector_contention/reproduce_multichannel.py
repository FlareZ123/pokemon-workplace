"""Reproduce and validate the multichannel shared-connector generalization."""

from __future__ import annotations

from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from shared_connector_contention import shared_connector_contention  # noqa: E402
from shared_connector_multichannel import (  # noqa: E402
    multichannel_shared_connector_contention,
)


ABS_TOLERANCE = 1e-12


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_multichannel(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_copies: tuple[int, ...],
    shared_connector_copies: int,
    opening_hand_size: int,
    extra_random_draws: int,
) -> tuple[float, float, float, float]:
    """Return labeled-state mass, true joint, naive joint, and contention."""

    categories: list[str] = []
    for target_index, copies in enumerate(target_copies):
        categories.extend([f"T{target_index}"] * copies)
    categories.extend(["C"] * shared_connector_copies)
    categories.extend(["S"] * starter_cards)
    categories.extend(
        ["F"]
        * (
            deck_size
            - sum(target_copies)
            - shared_connector_copies
            - starter_cards
        )
    )

    target_names = tuple(
        f"T{target_index}"
        for target_index in range(len(target_copies))
    )
    cards = tuple(range(deck_size))
    valid_states = 0
    true_joint = 0
    naive_joint = 0
    contention = 0

    for hand in combinations(cards, opening_hand_size):
        if not any(categories[index] == "S" for index in hand):
            continue

        hand_set = set(hand)
        after_hand = tuple(
            index for index in cards
            if index not in hand_set
        )
        for prizes in combinations(after_hand, prize_count):
            prize_set = set(prizes)
            after_prizes = tuple(
                index for index in after_hand
                if index not in prize_set
            )

            for draws in combinations(
                after_prizes,
                extra_random_draws,
            ):
                draw_set = set(draws)
                searchable = tuple(
                    index for index in after_prizes
                    if index not in draw_set
                )
                exposed = hand + draws
                connectors_in_hand = sum(
                    categories[index] == "C"
                    for index in exposed
                )

                in_hand = tuple(
                    sum(
                        categories[index] == target_name
                        for index in exposed
                    )
                    for target_name in target_names
                )
                in_deck = tuple(
                    sum(
                        categories[index] == target_name
                        for index in searchable
                    )
                    for target_name in target_names
                )

                accessible = tuple(
                    hand_count > 0
                    or (
                        connectors_in_hand > 0
                        and deck_count > 0
                    )
                    for hand_count, deck_count in zip(
                        in_hand,
                        in_deck,
                    )
                )
                naive = all(accessible)
                missing = sum(
                    hand_count == 0
                    for hand_count in in_hand
                )
                true = (
                    all(
                        hand_count > 0 or deck_count > 0
                        for hand_count, deck_count in zip(
                            in_hand,
                            in_deck,
                        )
                    )
                    and connectors_in_hand >= missing
                )

                valid_states += 1
                true_joint += true
                naive_joint += naive
                contention += naive and not true

    return (
        1.0,
        true_joint / valid_states,
        naive_joint / valid_states,
        contention / valid_states,
    )


def validate_two_channel_reduction() -> None:
    cases = [
        dict(
            deck_size=9,
            prize_count=2,
            starter_cards=2,
            target_a_copies=2,
            target_b_copies=2,
            shared_connector_copies=2,
            opening_hand_size=2,
            extra_random_draws=1,
        ),
        dict(
            deck_size=60,
            prize_count=6,
            starter_cards=12,
            target_a_copies=2,
            target_b_copies=2,
            shared_connector_copies=1,
            opening_hand_size=7,
            extra_random_draws=0,
        ),
    ]

    for case in cases:
        two = shared_connector_contention(**case)
        multi = multichannel_shared_connector_contention(
            case["deck_size"],
            case["prize_count"],
            starter_cards=case["starter_cards"],
            target_copies=(
                case["target_a_copies"],
                case["target_b_copies"],
            ),
            shared_connector_copies=case["shared_connector_copies"],
            opening_hand_size=case["opening_hand_size"],
            extra_random_draws=case["extra_random_draws"],
        )

        pairs = [
            (
                two.true_joint_access_probability,
                multi.true_joint_access_probability,
            ),
            (
                two.naive_joint_access_probability,
                multi.naive_joint_access_probability,
            ),
            (
                two.connector_contention_probability,
                multi.connector_contention_probability,
            ),
        ]
        for left, right in pairs:
            if not isclose(
                left,
                right,
                rel_tol=0.0,
                abs_tol=ABS_TOLERANCE,
            ):
                raise AssertionError((left, right))


def validate_labeled_three_channel_case() -> None:
    case = dict(
        deck_size=10,
        prize_count=2,
        starter_cards=2,
        target_copies=(1, 1, 1),
        shared_connector_copies=2,
        opening_hand_size=2,
        extra_random_draws=1,
    )
    exact = multichannel_shared_connector_contention(**case)
    brute = exhaustive_multichannel(**case)

    values = (
        exact.state_mass,
        exact.true_joint_access_probability,
        exact.naive_joint_access_probability,
        exact.connector_contention_probability,
    )
    for exact_value, brute_value in zip(values, brute):
        if not isclose(
            exact_value,
            brute_value,
            rel_tol=0.0,
            abs_tol=ABS_TOLERANCE,
        ):
            raise AssertionError((exact_value, brute_value))


def validate() -> None:
    validate_two_channel_reduction()
    validate_labeled_three_channel_case()


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        starter_cards=12,
        target_copies=(2, 2, 2),
        opening_hand_size=7,
        extra_random_draws=0,
    )

    print("Three target channels, two copies of each")
    print(
        "connectors | true joint | naive joint | overstatement "
        "| overstatement given naive"
    )
    for connectors in [0, 1, 2, 3, 4, 5, 6]:
        result = multichannel_shared_connector_contention(
            **base,
            shared_connector_copies=connectors,
        )
        print(
            f"{connectors:10d} | "
            f"{pct(result.true_joint_access_probability):>10} | "
            f"{pct(result.naive_joint_access_probability):>11} | "
            f"{pct(result.connector_contention_probability):>13} | "
            f"{pct(result.contention_given_naive_joint):>24}"
        )

    print("\nExposure sensitivity with two shared connectors")
    print(
        "extra random draws | true joint | naive joint | overstatement"
    )
    for extra_draws in [0, 1, 2, 5, 10]:
        result = multichannel_shared_connector_contention(
            **{
                **base,
                "extra_random_draws": extra_draws,
            },
            shared_connector_copies=2,
        )
        print(
            f"{extra_draws:18d} | "
            f"{pct(result.true_joint_access_probability):>10} | "
            f"{pct(result.naive_joint_access_probability):>11} | "
            f"{pct(result.connector_contention_probability):>13}"
        )


if __name__ == "__main__":
    main()
