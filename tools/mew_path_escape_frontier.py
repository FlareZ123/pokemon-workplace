"""Exact early Path-to-the-Peak escape sources in Mew/Genesect.

The outcome is the availability of a printed Path-removal Item or replacement
Stadium through natural exposure or held Trainers' Mail. We assume the opposing
Path is currently in play and no other Item lock is active. This measures only
access to source cards, not actual Genesect draw or match wins.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class EscapeFrontier:
    """Probabilities conditioned on a Basic-valid seven-card opening."""

    genesect_visible: Fraction
    direct: Fraction
    combined: Fraction
    genesect_direct: Fraction
    genesect_combined: Fraction

    @property
    def conditional_on_genesect(self) -> Fraction:
        if not self.genesect_visible:
            raise ValueError("Genesect visibility has zero probability")
        return self.genesect_combined / self.genesect_visible


def exact_escape_frontier(
    *,
    genesect: int,
    other_basics: int,
    outs: int,
    mails: int,
    filler: int,
    opening_hand: int = 7,
    prizes: int = 6,
    mail_reach: int = 4,
) -> EscapeFrontier:
    """Exact physical-multiset probability with Prize-aware Mail inspection.

    There is exactly one natural draw after six Prizes. A held Mail reveals the
    top mail_reach cards, selects a source when it appears, and shuffles the
    others into the deck. Conditional on a miss, the shuffled residual deck has
    unchanged class counts. Multiple held Mail attempts therefore have the
    stated independent miss probability conditional on the Prize partition.

    'outs' can include Lost Vacuum only under an explicitly assumed payable
    hand-card policy. Every count is a physical card count in the 60-card deck.
    """

    total = genesect + other_basics + outs + mails + filler
    exposed = opening_hand + 1
    if any(value < 0 for value in (
        genesect, other_basics, outs, mails, filler, prizes, mail_reach
    )):
        raise ValueError("card counts must be non-negative")
    if exposed > total or prizes > total-exposed or mail_reach > total-exposed-prizes:
        raise ValueError("opening/Prize/Mail geometry exceeds the deck")
    basics = genesect + other_basics
    if basics == 0:
        raise ValueError("the deck must have a Basic Pokémon")

    denominator = comb(total, exposed)
    opening_valid = Fraction(
        comb(total, opening_hand) -
        comb(total-basics, opening_hand),
        comb(total, opening_hand),
    )
    gene_mass = Fraction(0)
    direct_mass = Fraction(0)
    total_mass = Fraction(0)
    gene_direct_mass = Fraction(0)
    gene_total_mass = Fraction(0)
    valid_mass = Fraction(0)

    for g in range(min(genesect, exposed)+1):
        for b in range(min(other_basics, exposed-g)+1):
            for o in range(min(outs, exposed-g-b)+1):
                for m in range(min(mails, exposed-g-b-o)+1):
                    r = exposed-g-b-o-m
                    if r > filler:
                        continue
                    if g+b == 0:
                        continue

                    weight = Fraction(
                        comb(genesect, g)*comb(other_basics, b)*
                        comb(outs, o)*comb(mails, m)*comb(filler, r),
                        denominator,
                    )
                    # Last visible card is the post-Prize natural draw.
                    # It cannot be the only Basic in an accepted opener.
                    invalid = (
                        Fraction(comb(exposed-g-b, opening_hand), exposed)
                        if exposed-g-b >= opening_hand else Fraction(0)
                    )
                    weight *= (1-invalid)
                    valid_mass += weight
                    if g:
                        gene_mass += weight

                    if o:
                        direct_mass += weight
                        total_mass += weight
                        if g:
                            gene_direct_mass += weight
                            gene_total_mass += weight
                        continue

                    if not m:
                        continue

                    unseen = total-exposed
                    deck_size = unseen-prizes
                    success = Fraction(0)
                    for p in range(min(prizes, outs)+1):
                        if prizes-p > unseen-outs:
                            continue
                        prize_prob = Fraction(
                            comb(outs, p)*comb(unseen-outs, prizes-p),
                            comb(unseen, prizes),
                        )
                        surviving = outs-p
                        miss = Fraction(
                            comb(deck_size-surviving, mail_reach),
                            comb(deck_size, mail_reach),
                        )
                        success += prize_prob*(1-miss**m)

                    total_mass += weight*success
                    if g:
                        gene_total_mass += weight*success

    if valid_mass != opening_valid:
        raise AssertionError(
            f"opening normalization mismatch: {valid_mass} != {opening_valid}"
        )

    return EscapeFrontier(
        gene_mass/opening_valid,
        direct_mass/opening_valid,
        total_mass/opening_valid,
        gene_direct_mass/opening_valid,
        gene_total_mass/opening_valid,
    )
