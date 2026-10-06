"""Reproduce and validate multi-window rescue with clean direct outs."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from clean_out_rescue_deadline import (  # noqa: E402
    deadline_failure_probability_with_clean_outs,
)
from prize_rescue_deadline import (  # noqa: E402
    conditional_deadline_failure_probability_given_valid_start,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_failure(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    direct_out_nonstarter: int,
    cards_seen_by_window: tuple[int, ...],
    opening_hand_size: int,
) -> tuple[float, float]:
    """Independent labeled-subset enumeration for a small regression case."""
    categories = (
        ["C"] * critical_nonstarter
        + ["R"] * rescue_nonstarter
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
    all_cards = set(range(deck_size))
    segments: list[int] = []
    previous = opening_hand_size
    for cards_seen in cards_seen_by_window:
        segments.append(cards_seen - previous)
        previous = cards_seen

    accepted_openings = [
        set(opening)
        for opening in combinations(range(deck_size), opening_hand_size)
        if any(categories[index] == "S" for index in opening)
    ]

    critical_mass = 0.0
    failure_mass = 0.0
    opening_mass = 1.0 / len(accepted_openings)

    for opening in accepted_openings:
        remaining = all_cards - opening
        prize_sets = [
            set(prizes)
            for prizes in combinations(sorted(remaining), prize_count)
        ]
        prize_mass = 1.0 / len(prize_sets)

        for prizes in prize_sets:
            critical_prized = sum(
                categories[index] == "C" for index in prizes
            )
            if critical_prized == 0:
                continue

            state_mass = opening_mass * prize_mass
            critical_mass += state_mass

            deck = remaining - prizes
            rescue_hand = {
                index for index in opening
                if categories[index] == "R"
            }
            outs_hand = {
                index for index in opening
                if categories[index] == "O"
            }

            def recurse(
                window_index: int,
                current_deck: set[int],
                current_rescue_hand: set[int],
                current_outs_hand: set[int],
                played: int,
                branch_mass: float,
            ) -> None:
                nonlocal failure_mass

                if window_index == len(segments):
                    return

                draw_count = segments[window_index]
                draws = list(
                    combinations(sorted(current_deck), draw_count)
                )
                draw_mass = 1.0 / len(draws)
                required_by_now = max(
                    0,
                    critical_prized
                    - (len(segments) - (window_index + 1)),
                )

                for draw_tuple in draws:
                    drawn = set(draw_tuple)
                    next_deck = current_deck - drawn
                    next_rescue_hand = (
                        set(current_rescue_hand)
                        | {
                            index for index in drawn
                            if categories[index] == "R"
                        }
                    )
                    next_outs_hand = (
                        set(current_outs_hand)
                        | {
                            index for index in drawn
                            if categories[index] == "O"
                        }
                    )

                    rescue_in_deck = sorted(
                        index for index in next_deck
                        if categories[index] == "R"
                    )
                    out_count = min(
                        len(next_outs_hand),
                        len(rescue_in_deck),
                    )
                    if out_count:
                        used_outs = set(
                            sorted(next_outs_hand)[:out_count]
                        )
                        searched_rescue = set(
                            rescue_in_deck[:out_count]
                        )
                        next_outs_hand -= used_outs
                        next_deck -= searched_rescue
                        next_rescue_hand |= searched_rescue

                    needed_now = max(
                        0,
                        required_by_now - played,
                    )
                    next_branch_mass = branch_mass * draw_mass
                    if len(next_rescue_hand) < needed_now:
                        failure_mass += (
                            state_mass * next_branch_mass
                        )
                        continue

                    used_rescue = set(
                        sorted(next_rescue_hand)[:needed_now]
                    )
                    next_rescue_hand -= used_rescue
                    recurse(
                        window_index + 1,
                        next_deck,
                        next_rescue_hand,
                        next_outs_hand,
                        played + needed_now,
                        next_branch_mass,
                    )

            recurse(
                0,
                deck,
                rescue_hand,
                outs_hand,
                0,
                1.0,
            )

    return failure_mass / critical_mass, critical_mass


def validate() -> None:
    small = dict(
        deck_size=9,
        prize_count=2,
        starter_cards=3,
        critical_nonstarter=2,
        rescue_nonstarter=2,
        direct_out_nonstarter=1,
        cards_seen_by_window=(3, 4),
        opening_hand_size=2,
    )
    exact = deadline_failure_probability_with_clean_outs(
        **small,
        condition_on_critical_prized=True,
    )
    brute, _ = exhaustive_failure(**small)
    if abs(exact - brute) > 1e-15:
        raise AssertionError((exact, brute))

    # Zero clean outs must reduce exactly to the earlier timed-access model.
    previous = conditional_deadline_failure_probability_given_valid_start(
        60,
        6,
        starter_cards=12,
        critical_starter=0,
        critical_nonstarter=4,
        rescue_starter=0,
        rescue_nonstarter=2,
        cards_seen_by_window=(8, 9, 10),
        opening_hand_size=7,
    )
    combined_zero = deadline_failure_probability_with_clean_outs(
        60,
        6,
        starter_cards=12,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        direct_out_nonstarter=0,
        cards_seen_by_window=(8, 9, 10),
        opening_hand_size=7,
        condition_on_critical_prized=True,
    )
    if abs(previous - combined_zero) > 1e-15:
        raise AssertionError((previous, combined_zero))


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        starter_cards=12,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        opening_hand_size=7,
        condition_on_critical_prized=True,
    )

    print("Four criticals, two real rescuers, windows 8/9/10")
    print("clean outs | conditional deadline failure")
    for outs in [0, 1, 2, 4, 6, 8]:
        failure = deadline_failure_probability_with_clean_outs(
            **base,
            direct_out_nonstarter=outs,
            cards_seen_by_window=(8, 9, 10),
        )
        print(f"{outs:10d} | {pct(failure):>28}")

    print("\nExposure and clean-out interaction")
    print("windows | 0 outs | 2 outs | 4 outs | 6 outs | 8 outs")
    for windows in [
        (8, 9, 10),
        (10, 13, 16),
        (12, 18, 24),
    ]:
        values = [
            deadline_failure_probability_with_clean_outs(
                **base,
                direct_out_nonstarter=outs,
                cards_seen_by_window=windows,
            )
            for outs in [0, 2, 4, 6, 8]
        ]
        print(
            f"{'/'.join(map(str, windows)):>8} | "
            + " | ".join(f"{pct(value):>10}" for value in values)
        )


if __name__ == "__main__":
    main()
