from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations


@dataclass(frozen=True)
class Outcome:
    """Exact physical outcome conditional on one legal two-card choice."""

    returned_cards: tuple[str, str]
    drawn_card: str
    hand_after_draw: tuple[str, ...]
    deck_after_draw: tuple[str, ...]
    conditional_probability: Fraction


def historical_actions(
    other_hand: tuple[str, ...], deck: tuple[str, ...],
) -> set[Outcome]:
    """Base Set: shuffle two *other* cards from hand in order to draw one."""
    result: set[Outcome] = set()
    if len(other_hand) < 2:
        return result
    for selected in combinations(other_hand, 2):
        kept = tuple(card for card in other_hand if card not in selected)
        possible = deck + selected
        p = Fraction(1, len(possible) * (len(possible) - 1))
        # Uniform shuffle: 1/(n!) for each complete shuffle order.
        p = Fraction(1, 1)
        for i in range(2, len(possible) + 1):
            p /= i
        for order in permutations(possible):
            result.add(Outcome(selected, order[0], kept + (order[0],), order[1:], p))
    return result


def current_actions(
    remaining_hand: tuple[str, ...], deck: tuple[str, ...],
) -> set[Outcome]:
    """XY: shuffle two hand cards, then draw; illegal with fewer than two."""
    if len(remaining_hand) < 2:
        return set()
    outcomes: set[Outcome] = set()
    for i in range(len(remaining_hand)):
        for j in range(i + 1, len(remaining_hand)):
            selected = (remaining_hand[i], remaining_hand[j])
            preserved = (
                remaining_hand[:i]
                + remaining_hand[i + 1 :j]
                + remaining_hand[j + 1 :]
            )
            count = len(deck) + 2
            denominator = 1
            for k in range(1, count + 1):
                denominator *= k
            probability = Fraction(1, denominator)
            for shuffled in permutations([*deck, *selected]):
                outcomes.add(
                    Outcome(
                        selected,
                        shuffled[0],
                        preserved + (shuffled[0],),
                        tuple(shuffled[1:]),
                        probability,
                    )
                )
    return outcomes


def exhaustively_compare() -> dict[str, int]:
    """Enumerate distinct physical cards and all small ordered-deck states."""
    worlds = outcomes = playable_worlds = 0
    for hand_size in range(6):
        hand = tuple(f"H{i}" for i in range(hand_size))
        for deck_size in range(4):
            starting_deck = tuple(f"D{i}" for i in range(deck_size))
            old = historical_actions(hand, starting_deck)
            new = current_actions(hand, starting_deck)
            assert old == new, (hand, starting_deck, old ^ new)
            assert bool(old) == (hand_size >= 2)
            assert all(x.conditional_probability > 0 for x in old)
            assert all(len(x.hand_after_draw) == hand_size - 1 for x in old)
            assert all(len(x.deck_after_draw) == deck_size + 1 for x in old)
            worlds += 1
            playable_worlds += bool(old)
            outcomes += len(old)
    return {
        "worlds": worlds,
        "playable_worlds": playable_worlds,
        "conditional_outcomes": outcomes,
    }
