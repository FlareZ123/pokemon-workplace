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


def _apply_actions(
    cards: list[str],
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    hand_cards = list(hand)
    deck_cards = list(deck)

    rescuer = next(
        (index for index in hand_cards if cards[index] == "R"),
        None,
    )
    if rescuer is not None:
        hand_cards.remove(rescuer)
        critical_remaining -= 1
        return (
            critical_remaining,
            tuple(sorted(hand_cards)),
            tuple(sorted(deck_cards)),
        )

    preserving = next(
        (
            index
            for index in hand_cards
            if cards[index] in {"PS", "PN"}
        ),
        None,
    )
    if preserving is not None:
        rescuer = next(
            (index for index in deck_cards if cards[index] == "R"),
            None,
        )
        if rescuer is not None:
            hand_cards.remove(preserving)
            deck_cards.remove(rescuer)
            critical_remaining -= 1
            return (
                critical_remaining,
                tuple(sorted(hand_cards)),
                tuple(sorted(deck_cards)),
            )

    consuming = next(
        (index for index in hand_cards if cards[index] == "C"),
        None,
    )
    if consuming is not None:
        rescuer = next(
            (index for index in deck_cards if cards[index] == "R"),
            None,
        )
        if rescuer is not None:
            hand_cards.remove(consuming)
            deck_cards.remove(rescuer)
            hand_cards.append(rescuer)

    return (
        critical_remaining,
        tuple(sorted(hand_cards)),
        tuple(sorted(deck_cards)),
    )
