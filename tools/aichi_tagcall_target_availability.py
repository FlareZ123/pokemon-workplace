"""Exact TAG TEAM Supporter targets under a natural Jirachi/G&H/Tag Call triplet.

Classifies the physical searchable deck after a valid seven-card opener,
a single turn-start random draw, and six hidden Prize cards.
This is an information/action availability measure, not setup success.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class TagCallTargets:
    probabilities: tuple[tuple[bool, bool, Fraction], ...]
    natural_triplet_probability: Fraction
    accepted_opener_probability: Fraction

    def probability(self, *, gnh_searchable: bool, bellelba_searchable: bool) -> Fraction:
        return next(p for g, b, p in self.probabilities
                    if (g, b) == (gnh_searchable, bellelba_searchable))


def exact_tagcall_target_partition(
    *, deck_size: int = 60, opener: int = 7, natural_draws: int = 1,
    prizes: int = 6, basics: int = 14, gnh: int = 4,
    tagcall: int = 4, bellelba: int = 1,
) -> TagCallTargets:
    """Classify held-Jirachi/G&H/Tag Call cases by unprized search targets.

    Jirachi is one unique Basic known to have been dealt in the opener.
    Other Basic cards belong to the untyped residual pool because their
    exact location does not affect target existence in this partition.
    TAG TEAM Bellelba is one unique non-Basic Supporter.
    """
    if not (0 < opener < deck_size and natural_draws >= 0 and prizes >= 0
            and 1 <= basics <= deck_size and gnh > 0 and tagcall > 0
            and bellelba == 1):
        raise ValueError("invalid parameters")
    observed = opener-1+natural_draws
    unknown = deck_size-1-observed
    other = deck_size-1-gnh-tagcall-bellelba
    if (other < basics-1 or unknown < prizes
            or observed > deck_size-1):
        raise ValueError("deck or Prize size inconsistent")
    accept = Fraction(
        choose(deck_size, opener) -
        choose(deck_size-basics, opener),
        choose(deck_size, opener),
    )
    if not accept:
        raise ValueError("accepted opening impossible")

    hits = {(g, b): Fraction(0) for g in (False, True)
            for b in (False, True)}
    # First choose non-Jirachi observed cards, conditioning on the
    # single Jirachi being present in the opening seven.
    base = Fraction(opener, deck_size) / choose(deck_size-1, observed)
    for held_gnh in range(1, min(gnh, observed)+1):
        for held_tag in range(1, min(tagcall, observed-held_gnh)+1):
            for held_bellelba in (0, 1):
                ways = (
                    choose(gnh, held_gnh) *
                    choose(tagcall, held_tag) *
                    choose(bellelba, held_bellelba) *
                    choose(other, observed-held_gnh-held_tag-held_bellelba)
                )
                if not ways:
                    continue
                g_unknown = gnh-held_gnh
                b_unknown = bellelba-held_bellelba
                other_unknown = unknown-g_unknown-b_unknown
                for g_prized in range(g_unknown+1):
                    for b_prized in range(b_unknown+1):
                        prize_ways = (
                            choose(g_unknown, g_prized) *
                            choose(b_unknown, b_prized) *
                            choose(other_unknown, prizes-g_prized-b_prized)
                        )
                        if prize_ways:
                            target = (g_unknown>g_prized, b_unknown>b_prized)
                            hits[target] += (
                                base*ways*Fraction(prize_ways,choose(unknown,prizes))
                                / accept
                            )
    partition = tuple((g,b,hits[(g,b)]) for g in (False, True)
                      for b in (False, True))
    return TagCallTargets(
        probabilities=partition,
        natural_triplet_probability=sum(hits.values(), Fraction(0)),
        accepted_opener_probability=accept,
    )
