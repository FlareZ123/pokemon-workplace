"""Finite exact sensitivity surface for the K0 Box-payment information premium.

The deck composition always totals 60, including one initially held Box.
Use the exact pre-search Prize policy and accepted opening / draw mixture.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from secret_box_gnh_tool_pipeline import counts
from secret_box_k0_opening_mix import average_box_payment_policy


@dataclass(frozen=True)
class SensitivityRow:
    axis: str
    value: tuple[int, ...]
    nonanticipating: Fraction
    clairvoyant: Fraction
    gap_hand_mass: Fraction
    gap_hand_count: int

    @property
    def gap(self) -> Fraction:
        return self.clairvoyant - self.nonanticipating


def disposable_sensitivity(
    counts_to_check: tuple[int, ...] = (5, 10, 15, 20, 25, 30, 35),
) -> tuple[SensitivityRow, ...]:
    """Replace protected filler with immediately disposable copies."""
    out = []
    for d in counts_to_check:
        if not 0 <= d <= 38:
            raise ValueError("disposable count leaves fewer than 12 protected starters")
        deck = counts(D=d, I=1, A=2, B=1, G=2, S=2, E=1, P=50-d)
        assert sum(deck) + 1 == 60
        r = average_box_payment_policy(deck, basic_starters=12)
        out.append(SensitivityRow(
            "D", (d,), r.k0_success, r.clairvoyant_success,
            r.gap_visible_hand_mass, r.gap_state_count,
        ))
    return tuple(out)


def item_stadium_sensitivity(
    stadium_counts: tuple[int, ...] = (1, 2, 3, 4),
    item_counts: tuple[int, ...] = (0, 1, 2, 3, 4),
) -> tuple[SensitivityRow, ...]:
    """Replace protected filler with searchable Item and Stadium backups."""
    out = []
    for s in stadium_counts:
        for i in item_counts:
            protected = 33 - s - i
            if protected < 12 or min(s, i) < 0:
                raise ValueError("invalid item/stadium composition")
            deck = counts(D=20, I=i, A=2, B=1, G=2, S=s, E=1, P=protected)
            assert sum(deck) + 1 == 60
            r = average_box_payment_policy(deck, basic_starters=12)
            out.append(SensitivityRow(
                "S,I", (s, i), r.k0_success, r.clairvoyant_success,
                r.gap_visible_hand_mass, r.gap_state_count,
            ))
    return tuple(out)
