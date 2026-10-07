"""Reproduce and validate literal Gladion projection equivalence."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from literal_gladion_rescue import (  # noqa: E402
    consumed_projection_success,
    literal_gladion_rescue_success,
    literal_state_success,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _remove_one(values: tuple[int, ...], value: int) -> tuple[int, ...]:
    out = list(values)
    out.remove(value)
    return tuple(sorted(out))


@lru_cache(maxsize=None)
def _labeled_future(
    cards: tuple[str, ...],
    turns: int,
    critical_prizes: tuple[int, ...],
    hand: tuple[int, ...],
    prizes: tuple[int, ...],
    deck: tuple[int, ...],
) -> float:
    if not critical_prizes:
        return 1.0
    if turns == 0 or not deck:
        return 0.0

    total = 0.0
    for drawn in deck:
        next_deck = _remove_one(deck, drawn)
        next_hand = tuple(sorted(hand + (drawn,)))

        best = _labeled_future(
            cards,
            turns - 1,
            critical_prizes,
            next_hand,
            prizes,
            next_deck,
        )

        gladion = next((i for i in next_hand if cards[i] == "G"), None)
        if gladion is not None:
            critical = critical_prizes[0]
            new_hand = list(next_hand)
            new_hand.remove(gladion)
            new_hand.append(critical)
            new_prizes = list(prizes)
            new_prizes.remove(critical)
            new_prizes.append(gladion)
            best = max(
                best,
                _labeled_future(
                    cards,
                    turns - 1,
                    critical_prizes[1:],
                    tuple(sorted(new_hand)),
                    tuple(sorted(new_prizes)),
                    next_deck,
                ),
            )

            prize_gladion = next((i for i in prizes if cards[i] == "G"), None)
            if prize_gladion is not None:
                exchange_hand = list(next_hand)
                exchange_hand.remove(gladion)
                exchange_hand.append(prize_gladion)
                exchange_prizes = list(prizes)
                exchange_prizes.remove(prize_gladion)
                exchange_prizes.append(gladion)
                best = max(
                    best,
                    _labeled_future(
                        cards,
                        turns - 1,
                        critical_prizes,
                        tuple(sorted(exchange_hand)),
                        tuple(sorted(exchange_prizes)),
                        next_deck,
                    ),
                )

        total += best
    return total / len(deck)


def labeled_small_case(gladion_copies: int, turns: int) -> tuple[float, float]:
    cards = tuple(
        ["S"] * 3
        + ["C"] * 2
        + ["G"] * gladion_copies
        + ["O"] * (5 - gladion_copies)
    )
    indices = tuple(range(10))
    opening_size = 3
    prize_count = 2

    accepted_hands = 0
    prize_states = 0
    critical_states = 0
    success_sum = 0.0
    for hand in combinations(indices, opening_size):
        if not any(cards[i] == "S" for i in hand):
            continue
        accepted_hands += 1
        remaining = tuple(i for i in indices if i not in hand)
        for prizes in combinations(remaining, prize_count):
            prize_states += 1
            critical = tuple(sorted(i for i in prizes if cards[i] == "C"))
            if not critical:
                continue
            critical_states += 1
            deck = tuple(i for i in remaining if i not in prizes)
            _labeled_future.cache_clear()
            success_sum += _labeled_future(
                cards,
                turns,
                critical,
                tuple(sorted(hand)),
                tuple(sorted(prizes)),
                tuple(sorted(deck)),
            )

    assert prize_states == accepted_hands * 21
    return critical_states / prize_states, success_sum / critical_states


def main() -> None:
    for turns in range(1, 5):
        for critical in range(1, 4):
            for hand in range(0, 4):
                for prize_gladion in range(0, 4):
                    for deck_gladion in range(0, 4):
                        for other in range(1, 5):
                            literal_state_success.cache_clear()
                            consumed_projection_success.cache_clear()
                            literal = literal_state_success(
                                turns,
                                critical,
                                hand,
                                prize_gladion,
                                deck_gladion,
                                other,
                            )
                            projected = consumed_projection_success(
                                turns,
                                critical,
                                hand,
                                deck_gladion,
                                other,
                            )
                            assert isclose(
                                literal,
                                projected,
                                rel_tol=0.0,
                                abs_tol=1e-12,
                            )

    baseline = []
    for turns in range(1, 5):
        result = literal_gladion_rescue_success(
            60,
            6,
            starter_cards=12,
            critical_starter=0,
            critical_nonstarter=4,
            gladion_copies=2,
            rescue_turns=turns,
        )
        assert isclose(result.state_mass, 1.0, rel_tol=0.0, abs_tol=1e-12)
        baseline.append(result.conditional_success_probability)

    published = [0.20988290, 0.23799232, 0.26377561, 0.28912644]
    for actual, expected in zip(baseline, published):
        assert isclose(actual, expected, rel_tol=0.0, abs_tol=5e-9)

    for copies in (1, 2, 3):
        for turns in (1, 2, 3):
            category = literal_gladion_rescue_success(
                10,
                2,
                starter_cards=3,
                critical_starter=0,
                critical_nonstarter=2,
                gladion_copies=copies,
                opening_hand_size=3,
                rescue_turns=turns,
            )
            labeled_any, labeled_success = labeled_small_case(copies, turns)
            assert isclose(
                category.any_critical_prized,
                labeled_any,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
            assert isclose(
                category.conditional_success_probability,
                labeled_success,
                rel_tol=0.0,
                abs_tol=1e-12,
            )

    print("literal_gladion_projection: all assertions passed")
    print("60-card two-Gladion baseline:", *(pct(x) for x in baseline))
    any_critical, small = labeled_small_case(2, 2)
    print("small P(any critical prized):", pct(any_critical))
    print("small literal success:", pct(small))


if __name__ == "__main__":
    main()
