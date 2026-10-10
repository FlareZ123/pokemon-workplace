"""Exact count of legal and inclusion-minimal Retreat payments for 1/2-unit Energy.

The model uses the existing repository rule: positive-cost Retreat payments
contain at least one selected physical Energy card and at most cost cards.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import comb


@dataclass(frozen=True)
class RetreatPaymentCounts:
    full: int
    inclusion_minimal: int

    @property
    def nonminimal(self) -> int:
        return self.full - self.inclusion_minimal


def count_retreat_payments(
    one_unit_cards: int, two_unit_cards: int, retreat_cost: int,
) -> RetreatPaymentCounts:
    """Count physically distinct payments, treating card copies as labeled.

    For a selected a two-unit and b one-unit cards:
    - payment is legal when 1 <= a+b <= cost and 2a+b >= cost;
    - payment is inclusion-minimal when deleting any chosen card fails to pay.
      This is equivalent to 2a+b - min_selected_unit < cost.
    """
    if min(one_unit_cards, two_unit_cards, retreat_cost) < 0:
        raise ValueError("Card counts and Retreat Cost must be nonnegative")
    if retreat_cost == 0:
        return RetreatPaymentCounts(1, 1)

    full = minimal = 0
    for a in range(two_unit_cards + 1):
        for b in range(one_unit_cards + 1):
            if not (1 <= a + b <= retreat_cost and 2 * a + b >= retreat_cost):
                continue
            physical_choices = comb(two_unit_cards, a) * comb(one_unit_cards, b)
            full += physical_choices
            minimum_selected_unit = 1 if b else 2
            if 2 * a + b - minimum_selected_unit < retreat_cost:
                minimal += physical_choices
    return RetreatPaymentCounts(full, minimal)
