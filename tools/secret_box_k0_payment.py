"""Exact hidden-Prize payment commitment for Secret Box before the first deck search.

Box held. Player commits a three-card payment before knowing the six Prizes.
After that commitment, the Box search reveals remaining deck contents and
all subsequent Box -> G&H search choices can respond to them.

K0 chooses a common payment across hidden states; K1 is a clairvoyant
upper bound that can pick a different payment for each hidden Prize world.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb

from secret_box_gnh_tool_pipeline import (
    D, I, A, B, G, S, E, P, KINDS, State,
    _box_choices, _fetch, _gnh_choices, _goal, _pay,
)

SEARCHABLE = (I, A, B, G, S, E)


@dataclass(frozen=True)
class PaymentInformationResult:
    clairvoyant_success: Fraction
    k0_success: Fraction
    best_paid_hands: tuple[State, ...]
    prize_worlds: int

    @property
    def information_gap(self) -> Fraction:
        return self.clairvoyant_success - self.k0_success


@lru_cache(maxsize=None)
def continuation_after_box_payment(
    after_payment: State, searchable_deck: State, *,
    retain_item: bool = False, supporter_available: bool = True,
) -> bool:
    """Optimize legal Box searches and optional later G&H after Box is paid."""
    for picks in _box_choices(searchable_deck):
        held, remaining = _fetch(after_payment, searchable_deck, picks)
        if _goal(held, retain_item):
            return True
        if not supporter_available or not held[G]:
            continue
        after_supporter = list(held)
        after_supporter[G] -= 1
        after_supporter = tuple(after_supporter)
        for picks in _gnh_choices(remaining, False):
            gained, _ = _fetch(after_supporter, remaining, picks)
            if _goal(gained, retain_item):
                return True
        for paid in _pay(after_supporter, 2):
            for picks in _gnh_choices(remaining, True):
                gained, _ = _fetch(paid, remaining, picks)
                if _goal(gained, retain_item):
                    return True
    return False


def evaluate_hidden_prize_payment(
    visible_hand: State, unknown_cards: State, *, prize_count: int = 6,
    retain_item: bool = False, supporter_available: bool = True,
) -> PaymentInformationResult:
    """Exact multivariate-hypergeometric K0 vs clairvoyant Box payment.

    The held Box is omitted from both inputs. Unknown cards comprise the
    hidden Prizes plus physically remaining draw deck. The solver marginalizes
    Prize counts among unsearchable D/P fillers and enumerates all assignments
    for six strategically searchable categories.
    """
    if len(visible_hand) != len(KINDS) or len(unknown_cards) != len(KINDS):
        raise ValueError("invalid category vector length")
    if min(visible_hand + unknown_cards) < 0:
        raise ValueError("negative card count")
    if not 0 <= prize_count <= sum(unknown_cards):
        raise ValueError("invalid Prize count")
    payments = tuple(sorted(set(_pay(visible_hand, 3))))
    if not payments:
        return PaymentInformationResult(Fraction(0), Fraction(0), (), 0)

    denominator = comb(sum(unknown_cards), prize_count)
    other = unknown_cards[D] + unknown_cards[P]
    fixed_payment_wins = [0] * len(payments)
    k1_wins = 0
    total_mass = 0
    worlds = 0

    for prizes in product(*(range(min(unknown_cards[t], prize_count) + 1)
                            for t in SEARCHABLE)):
        spare = prize_count - sum(prizes)
        if not 0 <= spare <= other:
            continue
        weight = comb(other, spare)
        for category, count in zip(SEARCHABLE, prizes):
            weight *= comb(unknown_cards[category], count)
        if not weight:
            continue
        # Only searchable types are materialized. D/P Prize placements were
        # integrated into the integer multiplicity above.
        after_prizes = [0] * len(KINDS)
        for category, count in zip(SEARCHABLE, prizes):
            after_prizes[category] = unknown_cards[category] - count
        remaining = tuple(after_prizes)
        outcomes = [
            continuation_after_box_payment(p, remaining,
                                           retain_item=retain_item,
                                           supporter_available=supporter_available)
            for p in payments
        ]
        k1_wins += weight * any(outcomes)
        for i, success in enumerate(outcomes):
            fixed_payment_wins[i] += weight * success
        total_mass += weight
        worlds += 1

    assert total_mass == denominator, (total_mass, denominator)
    best = max(fixed_payment_wins)
    return PaymentInformationResult(
        clairvoyant_success=Fraction(k1_wins, denominator),
        k0_success=Fraction(best, denominator),
        best_paid_hands=tuple(payment for payment, wins in
                              zip(payments, fixed_payment_wins) if wins == best),
        prize_worlds=worlds,
    )
