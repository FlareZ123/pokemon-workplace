"""Reproduce discard-gated rescue-turn results and validations."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_rescue_discard_connector import (  # noqa: E402
    rescue_success_with_discard_connector,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _action_states(
    cards: list[str],
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    discard_cost: int,
) -> list[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    states = [(critical_remaining, hand, deck)]

    connectors = [
        index for index in hand if cards[index] == "G"
    ]
    disposable = [
        index for index in hand if cards[index] == "D"
    ]
    rescuers_in_deck = [
        index for index in deck if cards[index] == "R"
    ]
    rescuers_in_hand = [
        index for index in hand if cards[index] == "R"
    ]

    if discard_cost == 0:
        payable = len(connectors)
    else:
        payable = min(
            len(connectors), len(disposable) // discard_cost
        )
    max_searches = min(
        payable,
        len(rescuers_in_deck),
        critical_remaining,
    )

    for searches in range(max_searches + 1):
        if len(rescuers_in_hand) + searches == 0:
            continue

        next_hand = list(hand)
        next_deck = list(deck)

        for connector in connectors[:searches]:
            next_hand.remove(connector)
        for card in disposable[: searches * discard_cost]:
            next_hand.remove(card)
        for rescuer in rescuers_in_deck[:searches]:
            next_deck.remove(rescuer)
            next_hand.append(rescuer)

        played = next(
            index for index in next_hand if cards[index] == "R"
        )
        next_hand.remove(played)

        states.append(
            (
                critical_remaining - 1,
                tuple(sorted(next_hand)),
                tuple(sorted(next_deck)),
            )
        )

    return states


def _future_success(
    cards: list[str],
    turns_remaining: int,
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    discard_cost: int,
) -> float:
    if critical_remaining == 0:
        return 1.0
    if turns_remaining == 0 or not deck:
        return 0.0

    probability = 0.0
    for drawn in deck:
        next_deck = list(deck)
        next_deck.remove(drawn)
        next_hand = tuple(sorted(hand + (drawn,)))

        best = 0.0
        for (
            action_critical,
            action_hand,
            action_deck,
        ) in _action_states(
            cards,
            critical_remaining,
            next_hand,
            tuple(sorted(next_deck)),
            discard_cost,
        ):
            best = max(
                best,
                _future_success(
                    cards,
                    turns_remaining - 1,
                    action_critical,
                    action_hand,
                    action_deck,
                    discard_cost,
                ),
            )
        probability += best

    return probability / len(deck)


def exhaustive_conditional_success(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    rescue_supporters: int,
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int,
    rescue_turns: int,
) -> tuple[float, float]:
    protected_nonstarter = (
        deck_size
        - starter_cards
        - critical_nonstarter
        - rescue_supporters
        - connector_copies
        - disposable_nonstarters
    )

    cards: list[str] = []
    cards += ["CN"] * critical_nonstarter
    cards += ["R"] * rescue_supporters
    cards += ["G"] * connector_copies
    cards += ["D"] * disposable_nonstarters
    cards += ["S"] * starter_cards
    cards += ["X"] * protected_nonstarter

    all_cards = set(range(deck_size))
    accepted = 0
    critical_states = 0
    success_mass = 0.0

    for hand_tuple in combinations(range(deck_size), opening_hand_size):
        hand = set(hand_tuple)
        if not any(cards[index] == "S" for index in hand):
            continue

        after_hand = all_cards - hand
        for prize_tuple in combinations(sorted(after_hand), prize_count):
            prizes = set(prize_tuple)
            accepted += 1
            critical_prized = sum(
                cards[index] == "CN" for index in prizes
            )
            if critical_prized == 0:
                continue

            critical_states += 1
            success_mass += _future_success(
                cards,
                rescue_turns,
                critical_prized,
                tuple(sorted(hand)),
                tuple(sorted(after_hand - prizes)),
                discard_cost,
            )

    return (
        success_mass / critical_states,
        critical_states / accepted,
    )


def validate() -> None:
    exact = rescue_success_with_discard_connector(
        10,
        2,
        starter_cards=3,
        critical_starter=0,
        critical_nonstarter=2,
        rescue_supporters=2,
        connector_copies=1,
        disposable_nonstarters=2,
        discard_cost=1,
        opening_hand_size=3,
        rescue_turns=3,
    )
    brute_success, brute_any = exhaustive_conditional_success(
        10,
        2,
        starter_cards=3,
        critical_nonstarter=2,
        rescue_supporters=2,
        connector_copies=1,
        disposable_nonstarters=2,
        discard_cost=1,
        opening_hand_size=3,
        rescue_turns=3,
    )

    if abs(exact.conditional_success_probability - brute_success) > 1e-15:
        raise AssertionError(
            (exact.conditional_success_probability, brute_success)
        )
    if abs(exact.any_critical_prized - brute_any) > 1e-15:
        raise AssertionError((exact.any_critical_prized, brute_any))
    if abs(exact.state_mass - 1.0) > 1e-14:
        raise AssertionError(exact.state_mass)


def main() -> None:
    validate()

    print(
        "Conditional probability of rescuing every initially Prized critical"
    )
    print(
        "60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, "
        "4 non-starter criticals, 2 rescue Supporters, 1 preserving connector"
    )
    print(
        "disposable | cost | turn 1     | turn 2     | turn 3     | turn 4"
    )
    for disposable in [10, 20, 30]:
        for cost in [0, 2, 3]:
            values = []
            for turns in [1, 2, 3, 4]:
                result = rescue_success_with_discard_connector(
                    60,
                    6,
                    starter_cards=12,
                    critical_starter=0,
                    critical_nonstarter=4,
                    rescue_supporters=2,
                    connector_copies=1,
                    disposable_nonstarters=disposable,
                    discard_cost=cost,
                    rescue_turns=turns,
                )
                values.append(
                    pct(result.conditional_success_probability)
                )

            print(
                f"{disposable:10d} | {cost:4d} | "
                f"{values[0]:>10} | {values[1]:>10} | "
                f"{values[2]:>10} | {values[3]:>10}"
            )


if __name__ == "__main__":
    main()
