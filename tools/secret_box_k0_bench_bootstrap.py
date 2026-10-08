"""Exact Box-first two-Tool holder-capacity bridge over accepted openings.

Unlike the original P-only abstraction, preserve the number of Basic starters
visible after the opening plus ordinary start-of-turn draw. Requiring two
eligible free Pokémon holders is a necessary execution condition for attaching
two distinct Tools. All 12 Basic cards are modeled as mutually Tool-eligible,
with no earlier Tool attached. Box/G&H endpoint is still in-hand acquisition.\n\nThe visible-hand category vector retains already-deployed Basic starters as\ninaccessible protected P tokens to keep the original dealt-card census. They\nare not physically still in hand; because these tokens can never be used\nfor costs or searches, the representation is equivalent for this narrowly\nrestricted action model. Draw-to-hand-size effects would need a real\nseparate board/hand zone representation.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from secret_box_gnh_tool_pipeline import KINDS, State, counts
from secret_box_k0_opening_mix import _openings
from secret_box_k0_payment import evaluate_hidden_prize_payment


@dataclass(frozen=True)
class BasicHolderResult:
    k0_joint_success: Fraction
    k1_joint_success: Fraction
    sufficient_holders_mass: Fraction
    state_count: int
    supporting_state_count: int

    @property
    def joint_information_gap(self) -> Fraction:
        return self.k1_joint_success - self.k0_joint_success


def counted_visible_hands(
    deck_without_box: State, *,
    basics: int = 12, opening_hand_size: int = 7,
) -> tuple[dict[tuple[State, int], int], int]:
    """Count each accepted starter opener and subsequent draw, keeping Basic count."""
    if len(deck_without_box) != len(KINDS) or min(deck_without_box) < 0:
        raise ValueError("bad deck vector")
    if not 0 < basics <= deck_without_box[-1]:
        raise ValueError("Basic count must fit protected P")
    n = sum(deck_without_box)
    h = opening_hand_size - 1
    if h < 1 or h + 1 > n:
        raise ValueError("opening hand or draw too large")
    parts = deck_without_box[:-1] + (basics, deck_without_box[-1] - basics)
    denom = (comb(n, h) - comb(n - basics, h)) * (n - h)
    out: dict[tuple[State, int], int] = defaultdict(int)

    for opener in _openings(parts, h):
        weight = 1
        for n_i, h_i in zip(parts, opener):
            weight *= comb(n_i, h_i)
        for j, n_i in enumerate(parts):
            ways = n_i - opener[j]
            if not ways:
                continue
            visible = list(opener)
            visible[j] += 1
            basic_in_hand = visible[-2]
            visible_counts = tuple(visible[:-2]) + (visible[-2] + visible[-1],)
            out[(visible_counts, basic_in_hand)] += weight * ways

    assert sum(out.values()) == denom
    return out, denom


def holder_qualified_k0(
    deck_without_box: State, *,
    basics: int = 12, min_holders: int = 2, prize_count: int = 6,
) -> BasicHolderResult:
    """P(A+B+S+E acquisition AND >=min_holders visible usable Basics).

    Probabilities condition on Box in original 7-card hand and at least one
    eligible Basic among the other 6, not on holder sufficiency.
    """
    if min_holders < 1:
        raise ValueError("must require at least one holder")
    weighted, denominator = counted_visible_hands(deck_without_box, basics=basics)
    k0 = k1 = Fraction(0)
    qual = 0
    support = 0
    seen: set[State] = set()
    for (hand, basic_count), weight in weighted.items():
        if basic_count < min_holders:
            continue
        qual += weight
        support += 1
        unknown = tuple(total - held for total, held in zip(deck_without_box, hand))
        outcome = evaluate_hidden_prize_payment(hand, unknown, prize_count=prize_count)
        k0 += weight * outcome.k0_success
        k1 += weight * outcome.clairvoyant_success
    return BasicHolderResult(
        k0_joint_success=k0 / denominator,
        k1_joint_success=k1 / denominator,
        sufficient_holders_mass=Fraction(qual, denominator),
        state_count=len(weighted),
        supporting_state_count=support,
    )


def baseline_holder_bridge() -> BasicHolderResult:
    return holder_qualified_k0(
        counts(D=20,I=1,A=2,B=1,G=2,S=2,E=1,P=30),
        basics=12,min_holders=2,prize_count=6,
    )
