"""Reproduce discard-gated target-Supporter access results and validations."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_gated_supporter_access import (  # noqa: E402
    discard_gated_supporter_access,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_probabilities(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_supporters: int,
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int,
    extra_random_draws: int,
    spare_connectors_disposable: bool,
) -> tuple[float, float, float, float, float, float]:
    protected_nonstarters = (
        deck_size
        - starter_cards
        - target_supporters
        - connector_copies
        - disposable_nonstarters
    )
    cards: list[str] = []
    cards += ["target"] * target_supporters
    cards += ["connector"] * connector_copies
    cards += ["disposable"] * disposable_nonstarters
    cards += ["starter"] * starter_cards
    cards += ["protected"] * protected_nonstarters

    all_cards = set(range(deck_size))
    states = 0
    direct = 0
    naive = 0
    gated = 0
    overstatement = 0
    connector_needed = 0
    connector_payable = 0

    for hand_tuple in combinations(range(deck_size), opening_hand_size):
        hand = set(hand_tuple)
        if not any(cards[index] == "starter" for index in hand):
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

                target_in_hand = any(
                    cards[index] == "target" for index in visible
                )
                connectors_in_hand = sum(
                    cards[index] == "connector" for index in visible
                )
                target_in_deck = any(
                    cards[index] == "target" for index in searchable
                )
                route_needed = (
                    not target_in_hand
                    and connectors_in_hand > 0
                    and target_in_deck
                )

                disposable = sum(
                    cards[index] == "disposable" for index in visible
                )
                if (
                    spare_connectors_disposable
                    and connectors_in_hand > 1
                ):
                    disposable += connectors_in_hand - 1
                route_payable = (
                    route_needed and disposable >= discard_cost
                )

                direct += int(target_in_hand)
                naive_success = target_in_hand or route_needed
                gated_success = target_in_hand or route_payable
                naive += int(naive_success)
                gated += int(gated_success)
                overstatement += int(
                    naive_success and not gated_success
                )
                connector_needed += int(route_needed)
                connector_payable += int(route_payable)

    conditional = (
        connector_payable / connector_needed
        if connector_needed
        else 1.0
    )
    return (
        direct / states,
        naive / states,
        gated / states,
        overstatement / states,
        connector_needed / states,
        conditional,
    )


def validate() -> None:
    kwargs = {
        "starter_cards": 3,
        "target_supporters": 1,
        "connector_copies": 1,
        "disposable_nonstarters": 3,
        "discard_cost": 2,
        "opening_hand_size": 3,
        "extra_random_draws": 1,
        "spare_connectors_disposable": False,
    }
    exact = discard_gated_supporter_access(10, 2, **kwargs)
    brute = exhaustive_probabilities(10, 2, **kwargs)

    exact_values = (
        exact.direct_target_probability,
        exact.naive_access_probability,
        exact.gated_access_probability,
        exact.gate_overstatement_probability,
        exact.connector_needed_probability,
        exact.connector_payability_given_needed,
    )
    for exact_value, brute_value in zip(exact_values, brute):
        if abs(exact_value - brute_value) > 1e-15:
            raise AssertionError((exact_value, brute_value))

    if abs(exact.state_mass - 1.0) > 1e-14:
        raise AssertionError(exact.state_mass)


def main() -> None:
    validate()

    print(
        "60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, "
        "2 target Supporters, 1 discard-gated connector"
    )
    print(
        "disposable | cost | naive access | gated access | overstatement | "
        "P(payable | connector route needed)"
    )
    for disposable in [10, 15, 20, 25, 30, 35]:
        for cost in [2, 3]:
            result = discard_gated_supporter_access(
                60,
                6,
                starter_cards=12,
                target_supporters=2,
                connector_copies=1,
                disposable_nonstarters=disposable,
                discard_cost=cost,
            )
            print(
                f"{disposable:10d} | {cost:4d} | "
                f"{pct(result.naive_access_probability):>12} | "
                f"{pct(result.gated_access_probability):>12} | "
                f"{pct(result.gate_overstatement_probability):>13} | "
                f"{pct(result.connector_payability_given_needed):>35}"
            )


if __name__ == "__main__":
    main()
