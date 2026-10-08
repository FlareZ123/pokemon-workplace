"""Exact accepted-opening and turn-draw mixture of K0 Secret Box payment policies.

Condition on one Box in the initial seven and an eligible Basic already among
the six other opening cards. The ordinary turn-start draw occurs after Prizes
are placed; conditionally, this is equivalent to drawing one from all 53
remaining cards, then dealing six Prizes from the other 52.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from secret_box_gnh_tool_pipeline import State, P
from secret_box_k0_payment import evaluate_hidden_prize_payment


@dataclass(frozen=True)
class OpeningMixResult:
    clairvoyant_success: Fraction
    k0_success: Fraction
    gap_visible_hand_mass: Fraction
    visible_state_count: int
    gap_state_count: int

    @property
    def information_gap(self) -> Fraction:
        return self.clairvoyant_success - self.k0_success


def _openings(remaining: tuple[int, ...], places: int, chosen=()):
    if not remaining:
        if places == 0 and chosen[-2] > 0:
            yield chosen
        return
    for k in range(min(remaining[0], places) + 1):
        yield from _openings(remaining[1:], places - k, chosen + (k,))


def opening_hand_distribution(
    deck_without_box: State, *, basic_starters: int, opening_hand_size: int = 7,
) -> tuple[dict[State, int], int]:
    """Integer weighted visible hands after opener+draw, conditional on valid Basic."""
    if len(deck_without_box) != 8 or min(deck_without_box) < 0:
        raise ValueError("invalid category vector")
    if not 0 < basic_starters <= deck_without_box[P]:
        raise ValueError("must have positive protected Basic count")
    n = sum(deck_without_box)
    slots = opening_hand_size - 1
    if slots < 1 or slots + 1 > n:
        raise ValueError("opening and draw must fit in deck")
    split = deck_without_box[:-1] + (basic_starters, deck_without_box[P] - basic_starters)
    valid = comb(n, slots) - comb(n - basic_starters, slots)
    denominator = valid * (n - slots)
    weights: dict[State, int] = defaultdict(int)
    for opener in _openings(split, slots):
        ways = 1
        for total, held in zip(split, opener):
            ways *= comb(total, held)
        for j, total in enumerate(split):
            remaining = total - opener[j]
            if remaining == 0:
                continue
            shown = list(opener)
            shown[j] += 1
            # Both types of protected P are indistinguishable after acceptance.
            visible = tuple(shown[:-2]) + (shown[-2] + shown[-1],)
            weights[visible] += ways * remaining
    assert sum(weights.values()) == denominator
    return weights, denominator


def average_box_payment_policy(
    deck_without_box: State, *, basic_starters: int, opening_hand_size: int = 7,
    prize_count: int = 6, retain_item: bool = False,
    supporter_available: bool = True,
) -> OpeningMixResult:
    weights, denominator = opening_hand_distribution(
        deck_without_box, basic_starters=basic_starters,
        opening_hand_size=opening_hand_size,
    )
    total_clairvoyant = Fraction(0)
    total_k0 = Fraction(0)
    gap_weight = 0
    gap_states = 0
    for visible, weight in weights.items():
        unknown = tuple(total - held for total, held in zip(deck_without_box, visible))
        result = evaluate_hidden_prize_payment(
            visible, unknown, prize_count=prize_count,
            retain_item=retain_item, supporter_available=supporter_available,
        )
        total_clairvoyant += weight * result.clairvoyant_success
        total_k0 += weight * result.k0_success
        if result.information_gap:
            gap_weight += weight
            gap_states += 1
    return OpeningMixResult(
        clairvoyant_success=total_clairvoyant / denominator,
        k0_success=total_k0 / denominator,
        gap_visible_hand_mass=Fraction(gap_weight, denominator),
        visible_state_count=len(weights),
        gap_state_count=gap_states,
    )
