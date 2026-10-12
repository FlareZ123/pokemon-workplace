"""Exact first-turn Quick Ball-only target accessibility with physical Prize sampling.

Given a valid opening seven and one ordinary draw, track the actual card-class
hand, six Prize identities, remaining deck, Basic placement, and distinct
Quick Ball discard payments. Starting Active and action lines are optimistically
chosen after seeing each physical state: this is an oracle upper envelope.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from functools import lru_cache
from itertools import product

from reproduce import MANIFEST, choose, source_card, two_evolution_bases, validate_sources

# Voltorb, Pikachu, Ditto Prism, Quick Ball, other Basic, all other cards.
POP = (2, 1, 1, 4, 9, 43)
QUICK_BALL = 3
OTHER_BASIC = 4
TARGET_TYPES = (0, 1, 2)
BASIC_TYPES = (*TARGET_TYPES, OTHER_BASIC)
POLICIES = ("all_cards", "filler_only")


@lru_cache(maxsize=None)
def search(
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    board: tuple[int, ...],
    policy: str,
) -> bool:
    """All available Basic placements and paid Quick Ball transitions."""
    if two_evolution_bases(*board):
        return True

    for index in TARGET_TYPES:
        if hand[index]:
            next_hand = list(hand)
            next_board = list(board)
            next_hand[index] -= 1
            next_board[index] += 1
            if search(tuple(next_hand), deck, tuple(next_board), policy):
                return True

    if not hand[QUICK_BALL]:
        return False
    paid = list(hand)
    paid[QUICK_BALL] -= 1  # Played Item itself cannot be its discard payment.

    for discard_index, amount in enumerate(paid):
        if not amount:
            continue
        if policy == "filler_only" and discard_index not in (OTHER_BASIC, 5):
            continue
        after_payment = paid.copy()
        after_payment[discard_index] -= 1
        for target in BASIC_TYPES:
            if not deck[target]:
                continue
            next_deck = list(deck)
            next_deck[target] -= 1
            next_hand = after_payment.copy()
            next_hand[target] += 1
            if search(tuple(next_hand), tuple(next_deck), board, policy):
                return True
    return False


def active_choices(seven: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(index for index in BASIC_TYPES if seven[index] > 0)


def actor_state(
    seven: tuple[int, ...], prizes: tuple[int, ...],
    drawn: int, active: int,
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    hand = list(seven)
    hand[active] -= 1
    hand[drawn] += 1
    board = [0, 0, 0]
    if active in TARGET_TYPES:
        board[active] += 1
    remaining = tuple(
        size - held - prized - (index == drawn)
        for index, (size, held, prized) in enumerate(zip(POP, seven, prizes))
    )
    assert sum(hand) == 7 and sum(remaining) == 46
    return tuple(hand), remaining, tuple(board)


def sample_space():
    """Enumerate seven-hand, six-Prize, one-draw class configurations."""
    for prefix in product(*(range(min(7, size) + 1) for size in POP[:-1])):
        last = 7 - sum(prefix)
        if not 0 <= last <= POP[-1]:
            continue
        seven = (*prefix, last)
        if not any(seven[index] for index in BASIC_TYPES):
            continue
        hand_weight = math.prod(choose(size, held) for size, held in zip(POP, seven))
        remaining_after_hand = tuple(size - held for size, held in zip(POP, seven))
        for prize_prefix in product(
            *(range(min(6, size) + 1) for size in remaining_after_hand[:-1])
        ):
            prize_last = 6 - sum(prize_prefix)
            if not 0 <= prize_last <= remaining_after_hand[-1]:
                continue
            prizes = (*prize_prefix, prize_last)
            prize_weight = math.prod(
                choose(size, prized)
                for size, prized in zip(remaining_after_hand, prizes)
            )
            for drawn in range(len(POP)):
                available = POP[drawn] - seven[drawn] - prizes[drawn]
                if available:
                    yield seven, prizes, drawn, hand_weight * prize_weight * available


def main() -> None:
    validate_sources()
    card_quantities = {
        row["name"]: row["quantity"]
        for row in json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    }
    assert card_quantities["Quick Ball"] == 4
    assert POP == (
        card_quantities["Voltorb"], card_quantities["Pikachu"],
        card_quantities["Ditto ◇"], card_quantities["Quick Ball"], 9, 43,
    )
    quick_ball_rules = source_card("swsh1-179")["rules"]
    assert "discard another card from your hand" in quick_ball_rules[0]
    assert "Basic Pokémon" in quick_ball_rules[1]

    # Isolate distinct-card payment and prove alternative policy results
    # cannot be equated for every individual hand.
    assert not search((0, 0, 0, 1, 0, 0), (1, 1, 0, 0, 0, 0),
                      (0, 0, 0), "all_cards")
    assert search((1, 0, 0, 2, 0, 0), (0, 1, 0, 0, 0, 0),
                  (0, 0, 0), "all_cards")
    assert not search((1, 0, 0, 2, 0, 0), (0, 1, 0, 0, 0, 0),
                      (0, 0, 0), "filler_only")

    denominator = 0
    natural = 0
    success = {policy: 0 for policy in POLICIES}
    states = 0
    for seven, prizes, drawn, weight in sample_space():
        states += 1
        denominator += weight
        observed = list(seven)
        observed[drawn] += 1
        if two_evolution_bases(*observed[:3]):
            natural += weight
        for policy in POLICIES:
            if any(
                search(*actor_state(seven, prizes, drawn, active), policy)
                for active in active_choices(seven)
            ):
                success[policy] += weight

    assert denominator == (choose(60, 7) - choose(47, 7)) * choose(53, 6) * 47
    assert Fraction(natural, denominator) == Fraction(814128, 9797437)
    assert success["all_cards"] >= success["filler_only"] >= natural
    assert Fraction(success["all_cards"], denominator) == Fraction(
        80313436404203, 265089546832110
    )
    print(json.dumps({
        "weighted_zone_configurations": states,
        "denominator": denominator,
        "natural_only": float(Fraction(natural, denominator)),
        "quick_ball_all_cards": float(Fraction(success["all_cards"], denominator)),
        "quick_ball_filler_only": float(Fraction(success["filler_only"], denominator)),
        "exact_quick_ball_fraction": str(Fraction(success["all_cards"], denominator)),
        "cache_states": search.cache_info().currsize,
        "scope": "physical Quick Ball-only oracle upper envelope, not win rate",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
