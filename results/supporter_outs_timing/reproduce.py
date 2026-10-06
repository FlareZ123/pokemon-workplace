"""Reproduce typed same-turn Supporter access results and validations."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from supporter_outs_timing import same_turn_supporter_access  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_probabilities(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_supporters: int,
    preserving_starter_connectors: int,
    preserving_nonstarter_connectors: int,
    consuming_connectors: int,
    opening_hand_size: int,
    extra_random_draws: int,
    supporter_plays_remaining: int,
) -> tuple[float, float, float]:
    cards: list[tuple[str, bool]] = []
    cards += [("target", False)] * target_supporters
    cards += [("preserving", True)] * preserving_starter_connectors
    cards += [("preserving", False)] * preserving_nonstarter_connectors
    cards += [("consuming", False)] * consuming_connectors
    cards += [("filler", True)] * (
        starter_cards - preserving_starter_connectors
    )

    used_nonstarters = (
        target_supporters
        + preserving_nonstarter_connectors
        + consuming_connectors
    )
    cards += [("filler", False)] * (
        deck_size - starter_cards - used_nonstarters
    )

    all_cards = set(range(deck_size))
    accepted_states = 0
    typed_states = 0
    naive_states = 0
    naive_only_states = 0

    for hand_tuple in combinations(range(deck_size), opening_hand_size):
        hand = set(hand_tuple)
        if not any(cards[index][1] for index in hand):
            continue

        after_hand = all_cards - hand
        for prize_tuple in combinations(sorted(after_hand), prize_count):
            prizes = set(prize_tuple)
            after_prizes = after_hand - prizes

            for draw_tuple in combinations(
                sorted(after_prizes), extra_random_draws
            ):
                draws = set(draw_tuple)
                accepted_states += 1

                if supporter_plays_remaining == 0:
                    continue

                visible = hand | draws
                searchable_deck = after_prizes - draws

                target_in_hand = any(
                    cards[index][0] == "target" for index in visible
                )
                target_in_deck = any(
                    cards[index][0] == "target"
                    for index in searchable_deck
                )
                preserving_available = any(
                    cards[index][0] == "preserving"
                    for index in visible
                )
                consuming_available = any(
                    cards[index][0] == "consuming"
                    for index in visible
                )

                typed_success = (
                    target_in_hand
                    or (preserving_available and target_in_deck)
                    or (
                        supporter_plays_remaining >= 2
                        and consuming_available
                        and target_in_deck
                    )
                )
                naive_success = (
                    target_in_hand
                    or (
                        (preserving_available or consuming_available)
                        and target_in_deck
                    )
                )

                typed_states += int(typed_success)
                naive_states += int(naive_success)
                naive_only_states += int(
                    naive_success and not typed_success
                )

    return (
        typed_states / accepted_states,
        naive_states / accepted_states,
        naive_only_states / accepted_states,
    )


def validate() -> None:
    kwargs = {
        "starter_cards": 4,
        "target_supporters": 1,
        "preserving_starter_connectors": 1,
        "preserving_nonstarter_connectors": 1,
        "consuming_connectors": 1,
        "opening_hand_size": 3,
        "extra_random_draws": 1,
        "supporter_plays_remaining": 1,
    }
    exact = same_turn_supporter_access(10, 2, **kwargs)
    brute = exhaustive_probabilities(10, 2, **kwargs)

    if abs(exact.typed_access_probability - brute[0]) > 1e-15:
        raise AssertionError((exact.typed_access_probability, brute[0]))
    if abs(exact.naive_access_probability - brute[1]) > 1e-15:
        raise AssertionError((exact.naive_access_probability, brute[1]))
    if abs(exact.naive_only_probability - brute[2]) > 1e-15:
        raise AssertionError((exact.naive_only_probability, brute[2]))
    if abs(exact.state_mass - 1.0) > 1e-14:
        raise AssertionError(exact.state_mass)

    ordinary = same_turn_supporter_access(
        60,
        6,
        starter_cards=12,
        target_supporters=2,
        preserving_nonstarter_connectors=2,
        consuming_connectors=4,
        supporter_plays_remaining=1,
    )
    expanded_capacity = same_turn_supporter_access(
        60,
        6,
        starter_cards=12,
        target_supporters=2,
        preserving_nonstarter_connectors=2,
        consuming_connectors=4,
        supporter_plays_remaining=2,
    )
    if abs(
        expanded_capacity.typed_access_probability
        - ordinary.naive_access_probability
    ) > 1e-15:
        raise AssertionError(
            (
                expanded_capacity.typed_access_probability,
                ordinary.naive_access_probability,
            )
        )


def main() -> None:
    validate()

    print(
        "60 cards, 6 Prizes, 7-card accepted opener, 12 starters, "
        "2 target Supporters, 2 preserving connectors, 4 consuming connectors"
    )
    print(
        "random draws | typed access | naive access | naive-only overstatement"
    )
    for draws in [0, 1, 2, 5, 10]:
        result = same_turn_supporter_access(
            60,
            6,
            starter_cards=12,
            target_supporters=2,
            preserving_nonstarter_connectors=2,
            consuming_connectors=4,
            extra_random_draws=draws,
            supporter_plays_remaining=1,
        )
        print(
            f"{draws:12d} | {pct(result.typed_access_probability):>12} | "
            f"{pct(result.naive_access_probability):>12} | "
            f"{pct(result.naive_only_probability):>24}"
        )

    print("\nSupporter plays remaining, no later random draws")
    print("plays | typed access | naive access | naive-only overstatement")
    for plays in [0, 1, 2]:
        result = same_turn_supporter_access(
            60,
            6,
            starter_cards=12,
            target_supporters=2,
            preserving_nonstarter_connectors=2,
            consuming_connectors=4,
            supporter_plays_remaining=plays,
        )
        print(
            f"{plays:5d} | {pct(result.typed_access_probability):>12} | "
            f"{pct(result.naive_access_probability):>12} | "
            f"{pct(result.naive_only_probability):>24}"
        )


if __name__ == "__main__":
    main()
