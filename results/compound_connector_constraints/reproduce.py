"""Reproduce compound shared-connector capacity and discard constraints."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from compound_connector_constraints import (  # noqa: E402
    compound_connector_constraints,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_probabilities(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int,
    extra_random_draws: int,
) -> tuple[float, ...]:
    filler = (
        deck_size
        - starter_cards
        - target_a_copies
        - target_b_copies
        - connector_copies
        - disposable_nonstarters
    )
    cards: list[str] = []
    cards += ["A"] * target_a_copies
    cards += ["B"] * target_b_copies
    cards += ["C"] * connector_copies
    cards += ["D"] * disposable_nonstarters
    cards += ["S"] * starter_cards
    cards += ["X"] * filler

    all_cards = set(range(deck_size))
    states = 0
    totals = [0] * 8

    for hand_tuple in combinations(range(deck_size), opening_hand_size):
        hand = set(hand_tuple)
        if not any(cards[index] == "S" for index in hand):
            continue

        after_hand = all_cards - hand
        for prize_tuple in combinations(sorted(after_hand), prize_count):
            prizes = set(prize_tuple)
            after_prizes = after_hand - prizes

            for draw_tuple in combinations(
                sorted(after_prizes), extra_random_draws
            ):
                draws = set(draw_tuple)
                visible = hand | draws
                searchable = after_prizes - draws
                states += 1

                a_direct = any(
                    cards[index] == "A" for index in visible
                )
                b_direct = any(
                    cards[index] == "B" for index in visible
                )
                connectors = sum(
                    cards[index] == "C" for index in visible
                )
                disposable = sum(
                    cards[index] == "D" for index in visible
                )
                a_in_deck = any(
                    cards[index] == "A" for index in searchable
                )
                b_in_deck = any(
                    cards[index] == "B" for index in searchable
                )

                naive = (
                    a_direct or (connectors > 0 and a_in_deck)
                ) and (
                    b_direct or (connectors > 0 and b_in_deck)
                )
                missing = int(not a_direct) + int(not b_direct)
                targets_exist = (
                    (a_direct or a_in_deck)
                    and (b_direct or b_in_deck)
                )
                capacity = (
                    targets_exist and connectors >= missing
                    if missing
                    else True
                )

                payable = (
                    connectors
                    if discard_cost == 0
                    else min(
                        connectors, disposable // discard_cost
                    )
                )
                gated_naive = (
                    a_direct or (payable > 0 and a_in_deck)
                ) and (
                    b_direct or (payable > 0 and b_in_deck)
                )
                full = (
                    targets_exist and payable >= missing
                    if missing
                    else True
                )

                capacity_failure = naive and not capacity
                discard_failure = naive and not gated_naive
                combined_failure = naive and not full

                values = (
                    naive,
                    capacity,
                    gated_naive,
                    full,
                    capacity_failure,
                    discard_failure,
                    combined_failure,
                    capacity_failure and discard_failure,
                )
                for index, value in enumerate(values):
                    totals[index] += int(value)

    return tuple(total / states for total in totals)


def validate() -> None:
    kwargs = {
        "starter_cards": 3,
        "target_a_copies": 1,
        "target_b_copies": 1,
        "connector_copies": 1,
        "disposable_nonstarters": 2,
        "discard_cost": 1,
        "opening_hand_size": 3,
        "extra_random_draws": 1,
    }
    exact = compound_connector_constraints(10, 2, **kwargs)
    brute = exhaustive_probabilities(10, 2, **kwargs)
    exact_values = (
        exact.naive_joint_probability,
        exact.capacity_only_probability,
        exact.discard_only_naive_probability,
        exact.full_joint_probability,
        exact.capacity_error_probability,
        exact.discard_error_probability,
        exact.combined_error_probability,
        exact.constraint_overlap_probability,
    )
    for exact_value, brute_value in zip(exact_values, brute):
        if abs(exact_value - brute_value) > 1e-15:
            raise AssertionError((exact_value, brute_value))
    if abs(exact.state_mass - 1.0) > 1e-14:
        raise AssertionError(exact.state_mass)


def main() -> None:
    validate()

    print(
        "60 cards, 6 Prizes, valid 7-card opener, 12 starters, "
        "2 copies each of targets A/B, 1 shared connector"
    )
    print(
        "disposable | cost | naive joint | capacity only | "
        "discard-only naive | full joint | combined error"
    )
    for disposable in [10, 15, 20, 25, 30, 35]:
        result = compound_connector_constraints(
            60,
            6,
            starter_cards=12,
            target_a_copies=2,
            target_b_copies=2,
            connector_copies=1,
            disposable_nonstarters=disposable,
            discard_cost=2,
        )
        print(
            f"{disposable:10d} | {2:4d} | "
            f"{pct(result.naive_joint_probability):>11} | "
            f"{pct(result.capacity_only_probability):>13} | "
            f"{pct(result.discard_only_naive_probability):>18} | "
            f"{pct(result.full_joint_probability):>10} | "
            f"{pct(result.combined_error_probability):>14}"
        )

    print("\n20 disposable non-starters, varying discard cost")
    print(
        "cost | naive joint | capacity only | discard-only naive | "
        "full joint | constraint overlap"
    )
    for cost in [0, 2, 3]:
        result = compound_connector_constraints(
            60,
            6,
            starter_cards=12,
            target_a_copies=2,
            target_b_copies=2,
            connector_copies=1,
            disposable_nonstarters=20,
            discard_cost=cost,
        )
        print(
            f"{cost:4d} | {pct(result.naive_joint_probability):>11} | "
            f"{pct(result.capacity_only_probability):>13} | "
            f"{pct(result.discard_only_naive_probability):>18} | "
            f"{pct(result.full_joint_probability):>10} | "
            f"{pct(result.constraint_overlap_probability):>18}"
        )


if __name__ == "__main__":
    main()
