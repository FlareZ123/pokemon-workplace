"""Exact fixed-non-Basic-card Prize odds conditioned on a valid starter.

When m specified, physically distinct, non-Basic cards must all fall in the
Prize cards, the opening hand is drawn uniformly from the remaining N-m
cards conditional on that event. Unspecified Prize identities remain random.
"""

from fractions import Fraction
from math import comb


def fixed_nonbasic_prized_given_valid_opener(
    *,
    cards: int,
    basics: int,
    opening: int,
    prizes: int,
    forced_nonbasic: int,
) -> Fraction:
    """P(all specified non-Basics are Prized | opening has >=1 Basic)."""
    if not (
        1 <= opening <= cards - prizes
        and 1 <= basics <= cards - forced_nonbasic
        and 0 <= forced_nonbasic <= prizes
    ):
        raise ValueError("invalid deck, Basic, starter, or Prize parameters")

    all_forced_prized = Fraction(
        comb(cards - forced_nonbasic, prizes - forced_nonbasic),
        comb(cards, prizes),
    )
    valid_unconditional = 1 - Fraction(
        comb(cards - basics, opening),
        comb(cards, opening),
    )
    valid_given_forced = 1 - Fraction(
        comb(cards - forced_nonbasic - basics, opening),
        comb(cards - forced_nonbasic, opening),
    )
    return all_forced_prized * valid_given_forced / valid_unconditional
