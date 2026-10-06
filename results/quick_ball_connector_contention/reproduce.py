"""Reproduce and validate Quick Ball connector contention."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from quick_ball_connector_contention import (  # noqa: E402
    joint_attacker_and_gladion_probability,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_joint_probability(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    attacker_starter_copies: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    opening_hand_size: int,
    reusable_connector_counterfactual: bool,
) -> float:
    categories = (
        ["C"] * critical_nonstarter
        + ["G"] * rescue_nonstarter
        + ["L"]
        + ["A"] * attacker_starter_copies
        + ["Q"] * quick_ball_copies
        + ["D"] * disposable_nonstarter
        + ["S"] * other_starters
        + ["F"] * (
            deck_size
            - 1
            - other_starters
            - attacker_starter_copies
            - critical_nonstarter
            - rescue_nonstarter
            - quick_ball_copies
            - disposable_nonstarter
        )
    )
    all_cards = set(range(deck_size))
    critical_states = success_states = 0

    for opening_tuple in combinations(
        range(deck_size), opening_hand_size
    ):
        opening = set(opening_tuple)
        if not any(
            categories[index] in {"L", "A", "S"}
            for index in opening
        ):
            continue

        remaining = all_cards - opening
        for prize_tuple in combinations(
            sorted(remaining), prize_count
        ):
            prizes = set(prize_tuple)
            if not any(
                categories[index] == "C"
                for index in prizes
            ):
                continue
            critical_states += 1

            attacker_in_hand = any(
                categories[index] == "A"
                for index in opening
            )
            attacker_in_deck = any(
                categories[index] == "A"
                for index in remaining - prizes
            )
            if not attacker_in_hand and not attacker_in_deck:
                continue

            rescue_in_hand = any(
                categories[index] == "G"
                for index in opening
            )
            rescue_in_deck = any(
                categories[index] == "G"
                for index in remaining - prizes
            )
            support_in_hand = any(
                categories[index] == "L"
                for index in opening
            )
            support_in_deck = any(
                categories[index] == "L"
                for index in remaining - prizes
            )
            other_setup_starter = any(
                categories[index] in {"A", "S"}
                for index in opening
            )
            support_preserved = (
                support_in_hand and other_setup_starter
            )

            attacker_search = 0 if attacker_in_hand else 1

            if rescue_in_hand:
                support_search = 0
            elif support_preserved and rescue_in_deck:
                support_search = 0
            elif support_in_deck and rescue_in_deck:
                support_search = 1
            else:
                continue

            searches = attacker_search + support_search
            if searches == 0:
                success_states += 1
                continue

            if reusable_connector_counterfactual:
                quick_balls_required = discards_required = 1
            else:
                quick_balls_required = discards_required = searches

            quick_balls = sum(
                categories[index] == "Q"
                for index in opening
            )
            disposable = sum(
                categories[index] == "D"
                for index in opening
            )
            if (
                quick_balls >= quick_balls_required
                and disposable >= discards_required
            ):
                success_states += 1

    return success_states / critical_states


def validate() -> None:
    small = dict(
        deck_size=11,
        prize_count=2,
        other_starters=1,
        attacker_starter_copies=1,
        critical_nonstarter=2,
        rescue_nonstarter=1,
        quick_ball_copies=2,
        disposable_nonstarter=2,
        opening_hand_size=4,
    )
    for reusable in [False, True]:
        exact = joint_attacker_and_gladion_probability(
            **small,
            reusable_connector_counterfactual=reusable,
        )
        brute = exhaustive_joint_probability(
            **small,
            reusable_connector_counterfactual=reusable,
        )
        if abs(exact - brute) > 1e-14:
            raise AssertionError((reusable, exact, brute))


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        other_starters=10,
        attacker_starter_copies=1,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        quick_ball_copies=4,
        opening_hand_size=7,
    )

    print(
        "Required singleton Basic attacker + Tapu Lele-GX/Gladion package, "
        "12 total starters"
    )
    print(
        "disposable | actual one-use Quick Ball | reusable-edge graph | overstatement"
    )
    for disposable in [4, 8, 12, 16, 20, 24]:
        actual = joint_attacker_and_gladion_probability(
            **base,
            disposable_nonstarter=disposable,
        )
        reusable = joint_attacker_and_gladion_probability(
            **base,
            disposable_nonstarter=disposable,
            reusable_connector_counterfactual=True,
        )
        print(
            f"{disposable:10d} | {pct(actual):>25} | "
            f"{pct(reusable):>19} | "
            f"{100 * (reusable - actual):.6f} pp"
        )


if __name__ == "__main__":
    main()
