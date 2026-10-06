"""Reproduce exact deck-state access through connector capacity profiles."""

from __future__ import annotations

from itertools import combinations, product
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_capacity import ConnectorType  # noqa: E402
from connector_profile_access import connector_profile_access  # noqa: E402
from shared_connector_multichannel import (  # noqa: E402
    multichannel_shared_connector_contention,
)


ABS_TOLERANCE = 1e-12


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _state_true_feasible(
    demand: tuple[int, ...],
    exposed_connectors: tuple[
        tuple[int, tuple[tuple[int, ...], ...]],
        ...,
    ],
) -> bool:
    """Independently enumerate profile choices for exposed physical copies."""

    physical_profiles: list[tuple[tuple[int, ...], ...]] = []
    for copies, profiles in exposed_connectors:
        physical_profiles.extend(
            [profiles] * copies
        )

    option_ranges = [
        (None,) + profiles
        for profiles in physical_profiles
    ]
    for choices in product(*option_ranges):
        remaining = list(demand)
        for profile in choices:
            if profile is None:
                continue
            for index, supplied in enumerate(profile):
                remaining[index] = max(
                    0,
                    remaining[index] - supplied,
                )
        if sum(remaining) == 0:
            return True
    return False


def exhaustive_small(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_copies: tuple[int, ...],
    connector_types: tuple[ConnectorType, ...],
    opening_hand_size: int,
    extra_random_draws: int,
) -> tuple[float, float, float]:
    """Return labeled-state true joint, naive joint, and contention."""

    categories: list[str] = []
    for target_index, copies in enumerate(target_copies):
        categories.extend([f"T{target_index}"] * copies)
    for connector_index, connector in enumerate(connector_types):
        categories.extend(
            [f"C{connector_index}"] * connector.copies
        )
    categories.extend(["S"] * starter_cards)
    categories.extend(
        ["F"]
        * (
            deck_size
            - sum(target_copies)
            - sum(
                connector.copies
                for connector in connector_types
            )
            - starter_cards
        )
    )

    cards = tuple(range(deck_size))
    target_names = tuple(
        f"T{index}"
        for index in range(len(target_copies))
    )
    connector_names = tuple(
        f"C{index}"
        for index in range(len(connector_types))
    )

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
                connector_counts = tuple(
                    sum(
                        categories[index] == connector_name
                        for index in exposed
                    )
                    for connector_name in connector_names
                )

                reachable = []
                for target_index in range(len(target_copies)):
                    if in_hand[target_index] > 0:
                        reachable.append(True)
                        continue
                    if in_deck[target_index] == 0:
                        reachable.append(False)
                        continue

                    reachable.append(
                        any(
                            copies > 0
                            and any(
                                profile[target_index] > 0
                                for profile in connector.profiles
                            )
                            for copies, connector in zip(
                                connector_counts,
                                connector_types,
                            )
                        )
                    )

                naive = all(reachable)
                all_targets_exist = all(
                    hand_count > 0 or deck_count > 0
                    for hand_count, deck_count in zip(
                        in_hand,
                        in_deck,
                    )
                )

                if all_targets_exist:
                    demand = tuple(
                        int(hand_count == 0)
                        for hand_count in in_hand
                    )
                    exposed_connectors = tuple(
                        (
                            copies,
                            connector.profiles,
                        )
                        for copies, connector in zip(
                            connector_counts,
                            connector_types,
                        )
                    )
                    true = _state_true_feasible(
                        demand,
                        exposed_connectors,
                    )
                else:
                    true = False

                valid_states += 1
                true_joint += true
                naive_joint += naive
                contention += naive and not true

    return (
        true_joint / valid_states,
        naive_joint / valid_states,
        contention / valid_states,
    )


def validate() -> None:
    unit_profiles = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    )

    reduction = connector_profile_access(
        60,
        6,
        starter_cards=12,
        target_copies=(2, 2, 2),
        connector_types=(
            ConnectorType(
                "shared any-card",
                2,
                unit_profiles,
            ),
        ),
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
            reduction.true_joint_access_probability,
            previous.true_joint_access_probability,
        ),
        (
            reduction.naive_joint_access_probability,
            previous.naive_joint_access_probability,
        ),
        (
            reduction.connector_contention_probability,
            previous.connector_contention_probability,
        ),
    ):
        if not isclose(
            left,
            right,
            rel_tol=0.0,
            abs_tol=ABS_TOLERANCE,
        ):
            raise AssertionError((left, right))

    small_connectors = (
        ConnectorType(
            "any-card",
            1,
            unit_profiles,
        ),
        ConnectorType(
            "three-axis",
            1,
            ((1, 1, 1),),
        ),
    )
    small = dict(
        deck_size=10,
        prize_count=2,
        starter_cards=2,
        target_copies=(1, 1, 1),
        connector_types=small_connectors,
        opening_hand_size=2,
        extra_random_draws=1,
    )
    exact = connector_profile_access(**small)
    brute_true, brute_naive, brute_contention = exhaustive_small(
        **small
    )

    for left, right in (
        (
            exact.true_joint_access_probability,
            brute_true,
        ),
        (
            exact.naive_joint_access_probability,
            brute_naive,
        ),
        (
            exact.connector_contention_probability,
            brute_contention,
        ),
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

    unit_profiles = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    )
    three_axis_profile = ((1, 1, 1),)
    base = dict(
        deck_size=60,
        prize_count=6,
        starter_cards=12,
        target_copies=(2, 2, 2),
        opening_hand_size=7,
        extra_random_draws=0,
    )

    packages = (
        (
            "one capacity-one any-card",
            (
                ConnectorType(
                    "any-card",
                    1,
                    unit_profiles,
                ),
            ),
        ),
        (
            "one true three-axis",
            (
                ConnectorType(
                    "three-axis",
                    1,
                    three_axis_profile,
                ),
            ),
        ),
        (
            "two capacity-one any-card",
            (
                ConnectorType(
                    "any-card",
                    2,
                    unit_profiles,
                ),
            ),
        ),
        (
            "one any-card plus one three-axis",
            (
                ConnectorType(
                    "any-card",
                    1,
                    unit_profiles,
                ),
                ConnectorType(
                    "three-axis",
                    1,
                    three_axis_profile,
                ),
            ),
        ),
    )

    print("Three target channels, two copies of each")
    print("package | true joint | naive joint | overstatement")
    for label, connector_types in packages:
        result = connector_profile_access(
            **base,
            connector_types=connector_types,
        )
        print(
            f"{label:32s} | "
            f"{pct(result.true_joint_access_probability):>10} | "
            f"{pct(result.naive_joint_access_probability):>11} | "
            f"{pct(result.connector_contention_probability):>13}"
        )


if __name__ == "__main__":
    main()
