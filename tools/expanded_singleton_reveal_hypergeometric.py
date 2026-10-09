"""Exact finite-population search-target and Prize-status signal probabilities.

Three distinct singleton cards A, X, Y remain in an unknown deck-plus-Prize
pool of U physically exchangeable positions. P Prize cards are drawn uniformly.
Search chooses X when A is Prized and X is in deck, otherwise Y if available,
otherwise X; the no-target branch occurs when X and Y are both Prized.

This is a single-card availability/selection model, not a complete TCG turn.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class SingletonRevealProbabilities:
    pool_size: int
    prizes: int
    search_success: Fraction
    probability_x_given_success: Fraction
    probability_y_given_success: Fraction
    a_prized_given_success: Fraction
    a_prized_given_x: Fraction
    a_prized_given_y: Fraction
    name_only_correct_prediction: Fraction
    print_aware_correct_prediction: Fraction

    @property
    def print_information_decision_gain(self) -> Fraction:
        return (
            self.print_aware_correct_prediction
            - self.name_only_correct_prediction
        )


def _legal_combinations(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def exact_membership_enumeration(
    pool_size: int,
    prizes: int,
) -> SingletonRevealProbabilities:
    """Evaluate all eight Prize-membership states by hypergeometric counts."""
    if pool_size < 4 or not 1 <= prizes <= pool_size - 2:
        raise ValueError("need three distinguished copies and an active deck")
    total = comb(pool_size, prizes)
    rows: list[tuple[bool, str | None, Fraction]] = []
    for a_prized in (False, True):
        for x_prized in (False, True):
            for y_prized in (False, True):
                n_prized = sum((a_prized, x_prized, y_prized))
                probability = Fraction(
                    _legal_combinations(pool_size - 3, prizes - n_prized),
                    total,
                )
                if probability == 0:
                    continue
                choice = (
                    "X" if a_prized and not x_prized
                    else "Y" if not y_prized
                    else "X" if not x_prized
                    else None
                )
                rows.append((a_prized, choice, probability))

    success = sum((p for _, choice, p in rows if choice), Fraction())
    x = sum((p for _, choice, p in rows if choice == "X"), Fraction())
    y = sum((p for _, choice, p in rows if choice == "Y"), Fraction())
    if min(success, x, y) == 0:
        raise ValueError("this Prize configuration makes an outcome impossible")

    a_and_success = sum((
        p for a_prized, choice, p in rows if a_prized and choice
    ), Fraction())
    a_and_x = sum((
        p for a_prized, choice, p in rows if a_prized and choice == "X"
    ), Fraction())
    a_and_y = sum((
        p for a_prized, choice, p in rows if a_prized and choice == "Y"
    ), Fraction())

    return SingletonRevealProbabilities(
        pool_size,
        prizes,
        success,
        x / success,
        y / success,
        a_and_success / success,
        a_and_x / x,
        a_and_y / y,
        max(a_and_success, success - a_and_success) / success,
        (max(a_and_x, x - a_and_x) + max(a_and_y, y - a_and_y))
        / success,
    )


def closed_form_reveal_probabilities(
    pool_size: int,
    prizes: int,
) -> SingletonRevealProbabilities:
    """Independent symbolic probability identities in the nondegenerate range."""
    u, p = pool_size, prizes
    if u < 4 or not 2 <= p <= u - 2:
        raise ValueError("closed-form witness requires two possible Prizes")
    success = 1 - Fraction(p * (p - 1), u * (u - 1))
    x_joint = Fraction(
        p * (u - p) * (2 * u - p - 3),
        u * (u - 1) * (u - 2),
    )
    y_joint = success - x_joint

    a_and_x = Fraction(p * (u - p), u * (u - 1))
    a_and_y = Fraction(
        p * (p - 1) * (u - p),
        u * (u - 1) * (u - 2),
    )
    a_success = a_and_x + a_and_y

    return SingletonRevealProbabilities(
        u,
        p,
        success,
        x_joint / success,
        y_joint / success,
        a_success / success,
        a_and_x / x_joint,
        a_and_y / y_joint,
        max(a_success, success - a_success) / success,
        (
            max(a_and_x, x_joint - a_and_x)
            + max(a_and_y, y_joint - a_and_y)
        ) / success,
    )
