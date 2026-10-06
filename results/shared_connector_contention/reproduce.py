"""Reproduce and independently validate shared connector contention."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from shared_connector_contention import shared_connector_contention  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    shared_connector_copies: int,
    opening_hand_size: int,
    extra_random_draws: int,
) -> dict[str, float]:
    categories = (
        ["A"] * target_a_copies
        + ["B"] * target_b_copies
        + ["C"] * shared_connector_copies
        + ["S"] * starter_cards
        + ["F"] * (
            deck_size
            - starter_cards
            - target_a_copies
            - target_b_copies
            - shared_connector_copies
        )
    )

    totals = {
        "state_mass": 0,
        "target_a": 0,
        "target_b": 0,
        "true_joint": 0,
        "naive_joint": 0,
        "contention": 0,
    }

    cards = tuple(range(deck_size))
    for hand in combinations(cards, opening_hand_size):
        if not any(categories[index] == "S" for index in hand):
            continue

        after_hand = tuple(index for index in cards if index not in hand)
        for prizes in combinations(after_hand, prize_count):
            after_prizes = tuple(
                index for index in after_hand
                if index not in prizes
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

                a_in_hand = sum(
                    categories[index] == "A"
                    for index in exposed
                )
                b_in_hand = sum(
                    categories[index] == "B"
                    for index in exposed
                )
                connectors_in_hand = sum(
                    categories[index] == "C"
                    for index in exposed
                )
                a_in_deck = sum(
                    categories[index] == "A"
                    for index in searchable
                )
                b_in_deck = sum(
                    categories[index] == "B"
                    for index in searchable
                )

                a_accessible = (
                    a_in_hand > 0
                    or (
                        connectors_in_hand > 0
                        and a_in_deck > 0
                    )
                )
                b_accessible = (
                    b_in_hand > 0
                    or (
                        connectors_in_hand > 0
                        and b_in_deck > 0
                    )
                )
                naive_joint = a_accessible and b_accessible

                missing_targets = (
                    int(a_in_hand == 0)
                    + int(b_in_hand == 0)
                )
                true_joint = (
                    (a_in_hand > 0 or a_in_deck > 0)
                    and (b_in_hand > 0 or b_in_deck > 0)
                    and connectors_in_hand >= missing_targets
                )

                totals["state_mass"] += 1
                totals["target_a"] += a_accessible
                totals["target_b"] += b_accessible
                totals["true_joint"] += true_joint
                totals["naive_joint"] += naive_joint
                totals["contention"] += (
                    naive_joint and not true_joint
                )

    denominator = totals["state_mass"]
    return {
        key: value / denominator
        for key, value in totals.items()
    }


def validate() -> None:
    case = dict(
        deck_size=9,
        prize_count=2,
        starter_cards=2,
        target_a_copies=2,
        target_b_copies=2,
        shared_connector_copies=2,
        opening_hand_size=2,
        extra_random_draws=1,
    )
    exact = shared_connector_contention(**case)
    brute = exhaustive(**case)

    comparisons = {
        "state_mass": exact.state_mass,
        "target_a": exact.target_a_access_probability,
        "target_b": exact.target_b_access_probability,
        "true_joint": exact.true_joint_access_probability,
        "naive_joint": exact.naive_joint_access_probability,
        "contention": exact.connector_contention_probability,
    }
    for key, exact_value in comparisons.items():
        if not isclose(exact_value, brute[key], rel_tol=0.0, abs_tol=ABS_TOLERANCE):
            raise AssertionError(
                (key, exact_value, brute[key])
            )

    if not isclose(exact.state_mass, 1.0, rel_tol=0.0, abs_tol=ABS_TOLERANCE):
        raise AssertionError(exact.state_mass)
    if abs(
        exact.naive_joint_access_probability
        - exact.true_joint_access_probability
        - exact.connector_contention_probability
    ) > 1e-15:
        raise AssertionError(exact)


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        starter_cards=12,
        target_a_copies=2,
        target_b_copies=2,
        opening_hand_size=7,
        extra_random_draws=0,
    )

    print("Two target channels with two copies each")
    print(
        "connectors | true joint | naive joint | overstatement "
        "| overstatement given naive"
    )
    for connectors in range(5):
        result = shared_connector_contention(
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
        result = shared_connector_contention(
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

    print("\nTarget-copy sensitivity with one shared connector")
    print("A copies | B copies | true joint | naive joint | overstatement")
    for a_copies, b_copies in [
        (1, 1),
        (1, 2),
        (2, 2),
        (2, 4),
        (4, 4),
    ]:
        result = shared_connector_contention(
            **{
                **base,
                "target_a_copies": a_copies,
                "target_b_copies": b_copies,
            },
            shared_connector_copies=1,
        )
        print(
            f"{a_copies:8d} | {b_copies:8d} | "
            f"{pct(result.true_joint_access_probability):>10} | "
            f"{pct(result.naive_joint_access_probability):>11} | "
            f"{pct(result.connector_contention_probability):>13}"
        )


if __name__ == "__main__":
    main()
