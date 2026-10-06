"""Reproduce turn-by-turn typed Prize-rescue results and validations."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_rescue_connector_turns import rescue_success_by_turns  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _action_states(
    cards: list[str],
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
) -> list[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    states = [(critical_remaining, hand, deck)]

    rescuer = next(
        (index for index in hand if cards[index] == "R"),
        None,
    )
    if rescuer is not None:
        next_hand = list(hand)
        next_hand.remove(rescuer)
        states.append(
            (
                critical_remaining - 1,
                tuple(sorted(next_hand)),
                deck,
            )
        )

    preserving = next(
        (
            index
            for index in hand
            if cards[index] in {"PS", "PN"}
        ),
        None,
    )
    deck_rescuer = next(
        (index for index in deck if cards[index] == "R"),
        None,
    )
    if preserving is not None and deck_rescuer is not None:
        next_hand = list(hand)
        next_deck = list(deck)
        next_hand.remove(preserving)
        next_deck.remove(deck_rescuer)
        states.append(
            (
                critical_remaining - 1,
                tuple(sorted(next_hand)),
                tuple(sorted(next_deck)),
            )
        )

    consuming = next(
        (index for index in hand if cards[index] == "C"),
        None,
    )
    if consuming is not None and deck_rescuer is not None:
        next_hand = list(hand)
        next_deck = list(deck)
        next_hand.remove(consuming)
        next_deck.remove(deck_rescuer)
        next_hand.append(deck_rescuer)
        states.append(
            (
                critical_remaining,
                tuple(sorted(next_hand)),
                tuple(sorted(next_deck)),
            )
        )

    return states


def _labeled_future_success(
    cards: list[str],
    turns_remaining: int,
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
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
        ):
            best = max(
                best,
                _labeled_future_success(
                    cards,
                    turns_remaining - 1,
                    action_critical,
                    action_hand,
                    action_deck,
                ),
            )
        probability += best

    return probability / len(deck)


