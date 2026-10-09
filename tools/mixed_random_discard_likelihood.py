"""Exact posterior law for mixed-class random hand discards."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MixedDiscardInference:
    likelihood_tag_a: Fraction
    likelihood_tag_b: Fraction
    posterior_tag_a: Fraction
    posterior_tag_survives: Fraction


def mixed_class_two_discard_inference(a: int, b: int, *, prior_tag_a: Fraction) -> MixedDiscardInference:
    """Known a copies of A, b copies of B, and one hidden tagged A/B card."""
    if a < 0 or b < 0 or not 0 <= prior_tag_a <= 1:
        raise ValueError("invalid nonnegative card counts or probability")
    total = a + b + 1
    if total < 2:
        raise ValueError("need two cards")
    denominator = total * (total - 1)
    l_a = Fraction((a + 1) * b, denominator)
    l_b = Fraction(a * (b + 1), denominator)
    evidence = prior_tag_a * l_a + (1 - prior_tag_a) * l_b
    if evidence == 0:
        raise ValueError("mixed-class two-discard observation is impossible")
    p = prior_tag_a * l_a / evidence
    survival = p * Fraction(a, a + 1) + (1 - p) * Fraction(b, b + 1)
    return MixedDiscardInference(l_a, l_b, p, survival)
