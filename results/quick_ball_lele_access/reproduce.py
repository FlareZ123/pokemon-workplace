"""Reproduce and validate Quick Ball -> Tapu Lele-GX -> Gladion access."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from quick_ball_lele_access import (  # noqa: E402
    opening_gladion_access_probability,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_access(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    opening_hand_size: int,
    allow_spare_quick_ball_discard: bool = False,
    ignore_setup_trigger_loss: bool = False,
) -> float:
    categories = (
        ["C"] * critical_nonstarter
        + ["G"] * rescue_nonstarter
        + ["L"]
        + ["Q"] * quick_ball_copies
        + ["D"] * disposable_nonstarter
        + ["S"] * other_starters
        + ["F"] * (
            deck_size
            - 1
            - other_starters
            - critical_nonstarter
            - rescue_nonstarter
            - quick_ball_copies
            - disposable_nonstarter
        )
    )
    all_cards = set(range(deck_size))
    accepted = access = critical = 0

    for opening_tuple in combinations(
        range(deck_size), opening_hand_size
    ):
        opening = set(opening_tuple)
        if not any(
            categories[index] in {"L", "S"}
            for index in opening
        ):
            continue
        accepted += 1

        remaining = all_cards - opening
        for prizes_tuple in combinations(
            sorted(remaining), prize_count
        ):
            prizes = set(prizes_tuple)
            if not any(
                categories[index] == "C"
                for index in prizes
            ):
                continue
            critical += 1

            rescue_in_hand = sum(
                categories[index] == "G"
                for index in opening
            )
            rescue_in_deck = sum(
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
            other_starter_in_hand = any(
                categories[index] == "S"
                for index in opening
            )
            quick_ball_in_hand = sum(
                categories[index] == "Q"
                for index in opening
            )
            discardable = sum(
                categories[index] == "D"
                for index in opening
            )
            if allow_spare_quick_ball_discard:
                discardable += max(
                    0, quick_ball_in_hand - 1
                )

            support_preserved = support_in_hand and (
                ignore_setup_trigger_loss
                or other_starter_in_hand
            )

            if (
                rescue_in_hand >= 1
                or (
                    support_preserved
                    and rescue_in_deck >= 1
                )
                or (
                    quick_ball_in_hand >= 1
                    and discardable >= 1
                    and support_in_deck
                    and rescue_in_deck >= 1
                )
            ):
                access += 1

    if critical == 0:
        return 0.0
    return access / critical


def validate() -> None:
    case = dict(
        deck_size=9,
        prize_count=2,
        other_starters=2,
        critical_nonstarter=2,
        rescue_nonstarter=1,
        quick_ball_copies=1,
        disposable_nonstarter=1,
        opening_hand_size=2,
    )
    for spare in [False, True]:
        for ignore_setup in [False, True]:
            exact = opening_gladion_access_probability(
                **case,
                allow_spare_quick_ball_discard=spare,
                ignore_setup_trigger_loss=ignore_setup,
            )
            brute = exhaustive_access(
                **case,
                allow_spare_quick_ball_discard=spare,
                ignore_setup_trigger_loss=ignore_setup,
            )
            if abs(exact - brute) > 1e-15:
                raise AssertionError(
                    (spare, ignore_setup, exact, brute)
                )


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        other_starters=11,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        quick_ball_copies=4,
        opening_hand_size=7,
    )

    print(
        "Four criticals, two Gladion, one Tapu Lele-GX, "
        "four Quick Ball, 12 total starters"
    )
    print(
        "disposable | strict access | spare Quick Ball discard | "
        "naive ignore setup-trigger loss"
    )
    for disposable in [4, 8, 12, 16, 20, 24]:
        strict = opening_gladion_access_probability(
            **base,
            disposable_nonstarter=disposable,
        )
        spare = opening_gladion_access_probability(
            **base,
            disposable_nonstarter=disposable,
            allow_spare_quick_ball_discard=True,
        )
        naive = opening_gladion_access_probability(
            **base,
            disposable_nonstarter=disposable,
            ignore_setup_trigger_loss=True,
        )
        print(
            f"{disposable:10d} | {pct(strict):>13} | "
            f"{pct(spare):>24} | {pct(naive):>31}"
        )


if __name__ == "__main__":
    main()
