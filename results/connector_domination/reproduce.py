"""Reproduce and validate the connector-domination result."""

from __future__ import annotations

from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_domination import two_channel_connector_access


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def _small_labeled_validation() -> None:
    """Independently exhaust a small labeled deck."""

    cards = (
        "A1",
        "A2",
        "B1",
        "C1",
        "D1",
        "D2",
        "S1",
        "S2",
        "P1",
        "P2",
    )
    opening_size = 3
    prize_count = 2
    discard_cost = 1

    accepted_hands = [
        hand
        for hand in combinations(cards, opening_size)
        if any(card.startswith("S") for card in hand)
    ]

    totals = {
        "state_mass": 0.0,
        "direct": 0.0,
        "capacity_no_cost": 0.0,
        "capacity_gated": 0.0,
        "naive_gated": 0.0,
        "naive_no_cost": 0.0,
        "one_missing": 0.0,
        "one_missing_paid": 0.0,
        "both_missing": 0.0,
        "both_missing_paid": 0.0,
    }

    for hand in accepted_hands:
        remaining_after_hand = tuple(card for card in cards if card not in hand)
        prize_sets = tuple(combinations(remaining_after_hand, prize_count))

        for prizes in prize_sets:
            state_mass = 1.0 / len(accepted_hands) / len(prize_sets)
            totals["state_mass"] += state_mass

            searchable_deck = tuple(
                card for card in remaining_after_hand if card not in prizes
            )
            a_in_hand = any(card.startswith("A") for card in hand)
            b_in_hand = any(card.startswith("B") for card in hand)
            connector_in_hand = "C1" in hand
            disposable_in_hand = sum(
                card.startswith("D") for card in hand
            )
            a_searchable = any(
                card.startswith("A") for card in searchable_deck
            )
            b_searchable = any(
                card.startswith("B") for card in searchable_deck
            )

            direct = a_in_hand and b_in_hand
            missing_count = int(not a_in_hand) + int(not b_in_hand)
            one_missing = (
                connector_in_hand
                and missing_count == 1
                and (
                    (not a_in_hand and a_searchable)
                    or (not b_in_hand and b_searchable)
                )
            )
            payable = (
                connector_in_hand
                and disposable_in_hand >= discard_cost
            )
            one_missing_paid = one_missing and payable
            both_missing = (
                connector_in_hand
                and not a_in_hand
                and not b_in_hand
                and a_searchable
                and b_searchable
            )
            both_missing_paid = both_missing and payable
            all_individually_reachable = (
                (a_in_hand or a_searchable)
                and (b_in_hand or b_searchable)
            )

            capacity_no_cost = direct or one_missing
            capacity_gated = direct or one_missing_paid
            naive_gated = direct or (
                payable and all_individually_reachable
            )
            naive_no_cost = direct or (
                connector_in_hand and all_individually_reachable
            )

            totals["direct"] += state_mass * direct
            totals["capacity_no_cost"] += state_mass * capacity_no_cost
            totals["capacity_gated"] += state_mass * capacity_gated
            totals["naive_gated"] += state_mass * naive_gated
            totals["naive_no_cost"] += state_mass * naive_no_cost
            totals["one_missing"] += state_mass * one_missing
            totals["one_missing_paid"] += state_mass * one_missing_paid
            totals["both_missing"] += state_mass * both_missing
            totals["both_missing_paid"] += state_mass * both_missing_paid

    exact = two_channel_connector_access(
        10,
        2,
        starter_cards=2,
        target_a_copies=2,
        target_b_copies=1,
        disposable_nonstarters=2,
        discard_cost=1,
        opening_hand_size=3,
    )

    _assert_close(totals["state_mass"], 1.0)
    _assert_close(exact.state_mass, 1.0)
    _assert_close(exact.direct_joint_access, totals["direct"])
    _assert_close(
        exact.capacity_aware_no_cost_access,
        totals["capacity_no_cost"],
    )
    _assert_close(
        exact.capacity_aware_gated_access,
        totals["capacity_gated"],
    )
    _assert_close(
        exact.naive_shared_connector_gated_access,
        totals["naive_gated"],
    )
    _assert_close(
        exact.naive_shared_connector_no_cost_access,
        totals["naive_no_cost"],
    )
    _assert_close(
        exact.one_missing_connector_route,
        totals["one_missing"],
    )
    _assert_close(
        exact.one_missing_payable_route,
        totals["one_missing_paid"],
    )
    _assert_close(
        exact.both_missing_connector_route,
        totals["both_missing"],
    )
    _assert_close(
        exact.both_missing_payable_route,
        totals["both_missing_paid"],
    )


def _baseline() -> None:
    result = two_channel_connector_access(
        60,
        6,
        starter_cards=12,
        target_a_copies=4,
        target_b_copies=2,
        disposable_nonstarters=20,
        discard_cost=2,
    )

    expected = {
        "direct_joint_access": 0.07023479155822993,
        "capacity_aware_no_cost_access": 0.1150511759962711,
        "capacity_aware_gated_access": 0.09486194929667843,
        "naive_shared_connector_gated_access": 0.1362120612120315,
        "naive_shared_connector_no_cost_access": 0.17346603797716,
        "connector_capacity_overstatement": 0.041350111915353066,
        "discard_gate_loss": 0.020189226699592666,
        "combined_naive_overstatement": 0.07860408868048158,
        "one_missing_payability": 0.5495123724783111,
    }
    _assert_close(result.state_mass, 1.0)
    for field, value in expected.items():
        _assert_close(getattr(result, field), value)

    _assert_close(
        result.connector_capacity_overstatement,
        result.both_missing_payable_route,
    )
    _assert_close(
        result.discard_gate_loss,
        result.one_missing_connector_route
        - result.one_missing_payable_route,
    )

    print("Baseline: 4-copy target A, 2-copy target B, 1 connector")
    print(f"Direct joint access: {result.direct_joint_access:.6%}")
    print(
        "Capacity-aware, no discard cost: "
        f"{result.capacity_aware_no_cost_access:.6%}"
    )
    print(
        "Capacity-aware, discard-gated: "
        f"{result.capacity_aware_gated_access:.6%}"
    )
    print(
        "Naive shared connector, discard-gated: "
        f"{result.naive_shared_connector_gated_access:.6%}"
    )
    print(
        "Naive shared connector, no discard cost: "
        f"{result.naive_shared_connector_no_cost_access:.6%}"
    )
    print(
        "Connector-capacity overstatement: "
        f"{result.connector_capacity_overstatement:.6%}"
    )
    print(f"Discard-gate loss: {result.discard_gate_loss:.6%}")
    print(
        "Combined naive overstatement: "
        f"{result.combined_naive_overstatement:.6%}"
    )
    print(
        "Connector payability when exactly one target is missing: "
        f"{result.one_missing_payability:.6%}"
    )


def _disposable_sensitivity() -> None:
    print()
    print("Disposable-pool sensitivity")
    print(
        "D | realistic | capacity overstatement | "
        "discard-gate loss | fully naive"
    )
    for disposable in (10, 15, 20, 25, 30, 35):
        result = two_channel_connector_access(
            60,
            6,
            starter_cards=12,
            target_a_copies=4,
            target_b_copies=2,
            disposable_nonstarters=disposable,
            discard_cost=2,
        )
        print(
            f"{disposable:2d} | "
            f"{result.capacity_aware_gated_access:.6%} | "
            f"{result.connector_capacity_overstatement:.6%} | "
            f"{result.discard_gate_loss:.6%} | "
            f"{result.naive_shared_connector_no_cost_access:.6%}"
        )


if __name__ == "__main__":
    _small_labeled_validation()
    _baseline()
    _disposable_sensitivity()
    print()
    print("All connector-domination validations passed.")
