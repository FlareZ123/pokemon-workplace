"""Exact decomposition of physical Tag Call thinning and K1 at a G&H payment.

One G&H and one Tag Call are already held. Three additional G&H copies
are unseen among 52 physical cards with six uniformly placed Prizes.
A successful Tag Call searches for up to two of them *before* G&H is played.
The normalized experiment conditions on at least one of the three copies
being searchable. This avoids assuming a legal empty-target Item play.

Four other distinguished unseen cards: Artazon, spare TM: Evolution,
spare Jet Energy and a Ticket-role Item. An otherwise-unused Jirachi
will view uniformly sampled shuffled cards after G&H searches.
Cost is a hypothetical continuation penalty for paying two cards.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

NAMED = ("Artazon", "TM", "Jet", "Ticket")
EXTRA_GNH = 3
TAGCALL_TAKE = 2


@dataclass(frozen=True)
class World:
    prized_named: frozenset[str]
    prized_gnh: int
    mass: Fraction
    keep: Fraction
    pay: Fraction
    preview_keep: Fraction
    preview_pay: Fraction


@dataclass(frozen=True)
class Decomposition:
    successful_preview_probability: Fraction
    baseline_k0: Fraction
    baseline_free_k1: Fraction
    material_only_k0: Fraction
    material_plus_information: Fraction
    material_gain: Fraction
    preview_information_gain: Fraction
    gross_preview_gain: Fraction


def worlds(unseen: int, prizes: int, inspect: int) -> tuple[World, ...]:
    """Return exact grouped Prize worlds conditioned on a G&H search hit."""
    if (unseen < 7 or prizes < 0 or prizes > unseen
            or inspect < 1 or inspect > unseen-prizes-5):
        raise ValueError("Invalid unseen pool, Prizes or Wish horizon")

    fillers = unseen-len(NAMED)-EXTRA_GNH
    denominator = comb(unseen, prizes)
    rows = []

    for k in range(len(NAMED)+1):
        for prized in combinations(NAMED, k):
            named = frozenset(prized)
            for gnh_prized in range(EXTRA_GNH):
                filler_prized = prizes-k-gnh_prized
                if not 0 <= filler_prized <= fillers:
                    continue
                mass = Fraction(
                    comb(EXTRA_GNH, gnh_prized) * comb(fillers, filler_prized),
                    denominator,
                )
                copies_available = EXTRA_GNH-gnh_prized
                take = min(TAGCALL_TAKE, copies_available)
                original_size = unseen-prizes-int("Artazon" not in named)
                paid_size = original_size-int("TM" not in named)-int("Jet" not in named)
                ticket = "Ticket" not in named
                rows.append(World(
                    named, gnh_prized, mass,
                    Fraction(inspect, original_size) if ticket else Fraction(),
                    Fraction(inspect, paid_size) if ticket else Fraction(),
                    Fraction(inspect, original_size-take) if ticket else Fraction(),
                    Fraction(inspect, paid_size-take) if ticket else Fraction(),
                ))
    return tuple(rows)


def calculate(
    unseen: int, prizes: int, inspect: int, penalty: Fraction,
) -> Decomposition:
    if penalty < 0:
        raise ValueError("Discard continuation penalty must be nonnegative")
    rows = worlds(unseen, prizes, inspect)
    mass = sum((row.mass for row in rows), Fraction())
    if mass <= 0:
        raise ValueError("No successful Tag Call preview state")

    def mean(values: tuple[Fraction, ...]) -> Fraction:
        return sum((r.mass*v for r, v in zip(rows, values)), Fraction())/mass

    original_keep = mean(tuple(r.keep for r in rows))
    original_pay = mean(tuple(r.pay-penalty for r in rows))
    original_k0 = max(original_keep, original_pay)
    original_k1 = mean(tuple(max(r.keep,r.pay-penalty) for r in rows))
    thinned_keep = mean(tuple(r.preview_keep for r in rows))
    thinned_pay = mean(tuple(r.preview_pay-penalty for r in rows))
    thinned_k0 = max(thinned_keep, thinned_pay)
    observed_k1 = mean(tuple(max(r.preview_keep,r.preview_pay-penalty) for r in rows))
    assert original_k0 <= original_k1
    assert thinned_k0 <= observed_k1
    assert thinned_k0 >= original_k0
    return Decomposition(
        mass, original_k0, original_k1, thinned_k0, observed_k1,
        thinned_k0-original_k0, observed_k1-thinned_k0,
        observed_k1-original_k0,
    )
