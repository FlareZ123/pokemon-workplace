"""Reproduce and validate discard-gated multichannel connector access."""

from __future__ import annotations

from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_gated_multichannel_access import (  # noqa: E402
    discard_gated_multichannel_access,
)
from discard_gated_supporter_access import (  # noqa: E402
    discard_gated_supporter_access,
)
from shared_connector_multichannel import (  # noqa: E402
    multichannel_shared_connector_contention,
)


ABS_TOLERANCE = 1e-12


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_small(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_copies: tuple[int, ...],
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int,
    extra_random_draws: int,
) -> tuple[float, float, float]:
    """Return labeled-state raw naive, cost-aware naive, and exact access."""

    categories: list[str] = []
    for target_index, copies in enumerate(target_copies):
        categories.extend([f"T{target_index}"] * copies)
    categories.extend(["C"] * connector_copies)
    categories.extend(["D"] * disposable_nonstarters)
    categories.extend(["S"] * starter_cards)
    categories.extend(
        ["F"]
        * (
            deck_size
            - sum(target_copies)
            - connector_copies
            - disposable_nonstarters
            - starter_cards
        )
    )

    target_names = tuple(
        f"T{index}"
        for index in range(len(target_copies))
    )
    cards = tuple(range(deck_size))
    valid_states = 0
    raw_naive = 0
    cost_aware = 0
    exact = 0

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
                exposed = hand + draws
                searchable = tuple(
                    index for index in after_prizes
                    if index not in draw_set
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
                connectors = sum(
                    categories[index] == "C"
                    for index in exposed
                )
                disposable = sum(
                    categories[index] == "D"
                    for index in exposed
                )
                usable = (
                    connectors
                    if discard_cost == 0
                    else min(
                        connectors,
                        disposable // discard_cost,
                    )
                )

                def naive(connector_count: int) -> bool:
                    return all(
                        hand_count > 0
                        or (
                            connector_count > 0
                            and deck_count > 0
                        )
                        for hand_count, deck_count in zip(
                            in_hand,
                            in_deck,
                        )
                    )

                raw = naive(connectors)
                gated = naive(usable)
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
                    and usable >= missing
                )

                valid_states += 1
                raw_naive += raw
                cost_aware += gated
                exact += true

    return (
        raw_naive / valid_states,
        cost_aware / valid_states,
        exact / valid_states,
    )


def validate() -> None:
    zero_cost = discard_gated_multichannel_access(
        60,
        6,
        starter_cards=12,
        target_copies=(2, 2, 2),
        connector_copies=2,
        disposable_nonstarters=0,
        discard_cost=0,
        opening_hand_size=7,
        extra_random_draws=0,
    )
    previous = multichannel_shared_connector_contention(
        60,
        6,
        starter_cards=12,
        target_copies=(2, 2, 2),
        shared_connector_copies=2,
        opening_hand_size=7,
        extra_random_draws=0,
    )
    for left, right in (
        (
            zero_cost.raw_naive_joint_probability,
            previous.naive_joint_access_probability,
        ),
        (
            zero_cost.exact_joint_probability,
            previous.true_joint_access_probability,
        ),
    ):
        if not isclose(
            left,
            right,
            rel_tol=0.0,
            abs_tol=ABS_TOLERANCE,
        ):
            raise AssertionError((left, right))

    one_channel = discard_gated_multichannel_access(
        60,
        6,
        starter_cards=12,
        target_copies=(2,),
        connector_copies=1,
        disposable_nonstarters=20,
        discard_cost=2,
        opening_hand_size=7,
        extra_random_draws=0,
    )
    previous_gate = discard_gated_supporter_access(
        60,
        6,
        starter_cards=12,
        target_supporters=2,
        connector_copies=1,
        disposable_nonstarters=20,
        discard_cost=2,
        opening_hand_size=7,
        extra_random_draws=0,
    )
    for left, right in (
        (
            one_channel.raw_naive_joint_probability,
            previous_gate.naive_access_probability,
        ),
        (
            one_channel.exact_joint_probability,
            previous_gate.gated_access_probability,
        ),
    ):
        if not isclose(
            left,
            right,
            rel_tol=0.0,
            abs_tol=ABS_TOLERANCE,
        ):
            raise AssertionError((left, right))

    small = dict(
        deck_size=10,
        prize_count=2,
        starter_cards=2,
        target_copies=(1, 1, 1),
        connector_copies=1,
        disposable_nonstarters=2,
        discard_cost=2,
        opening_hand_size=2,
        extra_random_draws=1,
    )
    exact_small = discard_gated_multichannel_access(**small)
    brute = exhaustive_small(**small)
    for left, right in zip(
        (
            exact_small.raw_naive_joint_probability,
            exact_small.cost_aware_naive_joint_probability,
            exact_small.exact_joint_probability,
        ),
        brute,
    ):
        if not isclose(
            left,
            right,
            rel_tol=0.0,
            abs_tol=ABS_TOLERANCE,
        ):
            raise AssertionError((left, right))


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        starter_cards=12,
        target_copies=(2, 2, 2),
        connector_copies=1,
        opening_hand_size=7,
        extra_random_draws=0,
    )

    for discard_cost in (2, 3):
        print(f"\nDiscard cost {discard_cost}")
        print(
            "disposable | raw naive | cost-aware naive | exact joint "
            "| cost loss | capacity loss | total loss"
        )
        for disposable in (10, 15, 20, 25, 30, 35):
            result = discard_gated_multichannel_access(
                **base,
                disposable_nonstarters=disposable,
                discard_cost=discard_cost,
            )
            print(
                f"{disposable:10d} | "
                f"{pct(result.raw_naive_joint_probability):>9} | "
                f"{pct(result.cost_aware_naive_joint_probability):>16} | "
                f"{pct(result.exact_joint_probability):>11} | "
                f"{pct(result.cost_gate_overstatement_probability):>9} | "
                f"{pct(result.capacity_overstatement_probability):>13} | "
                f"{pct(result.total_overstatement_probability):>10}"
            )


if __name__ == "__main__":
    main()
