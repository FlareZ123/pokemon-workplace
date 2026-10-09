"""Exact two-action information advantage from reward-disagreement moments."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


@dataclass(frozen=True)
class BinaryChoiceGap:
    expected_advantage: Fraction
    expected_absolute_advantage: Fraction
    information_gain: Fraction


def binary_choice_information_gap(
    states: Iterable[tuple[Fraction, Fraction, Fraction]],
) -> BinaryChoiceGap:
    """Each state = (prior mass, payoff action A, payoff action B).

    For any state-dependent rational payoffs, the value of observing the
    state before choosing is exactly:
       (E[abs(A-B)] - abs(E[A-B])) / 2.
    No assumption about card effects or hidden-zone distributions is needed.
    """
    rows=tuple((Fraction(w),Fraction(a),Fraction(b)) for w,a,b in states)
    if not rows or any(w<0 for w,a,b in rows):
        raise ValueError("nonempty distribution with nonnegative masses required")
    if sum((w for w,a,b in rows),Fraction(0))!=1:
        raise ValueError("prior masses must sum to exactly one")
    mean=sum((w*(a-b) for w,a,b in rows),Fraction(0))
    abs_mean=sum((w*abs(a-b) for w,a,b in rows),Fraction(0))
    gap=(abs_mean-abs(mean))/2
    assert gap>=0
    return BinaryChoiceGap(mean,abs_mean,gap)
