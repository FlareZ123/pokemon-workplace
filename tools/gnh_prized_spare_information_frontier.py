"""Exact prepayment information value for G&H fetching spare Tool/Energy.

Twelve unseen cards include Artazon, spare TM, spare Jet, one Ticket,
and eight other physical filler cards. The player already holds one TM,
one Jet, G&H, and two otherwise expendable cards to finance payment.
Place P uniform Prizes; the payer chooses PAY or KEEP before first G&H
deck inspection. If PAY, the two cards are discarded and G&H searches
any unprized Artazon, TM and Jet, before a five-card Stellar Wish.
A nonnegative utility penalty lambda models lost discard resources.

K0 must choose one action across all hidden Prize worlds; free K1 may
choose separately after seeing Prizes. The latter is an information
upper bound, not a simulation of physically paying for a prior search.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from collections import Counter

NAMED = ("Artazon", "TM", "Jet", "Ticket")
OTHER = tuple(f"Other{i}" for i in range(8))
CARDS = NAMED + OTHER


@dataclass(frozen=True)
class World:
    prizes: tuple[str, ...]
    keep: Fraction
    pay: Fraction

    @property
    def gain(self) -> Fraction:
        return self.pay - self.keep


@dataclass(frozen=True)
class Values:
    keep: Fraction
    paid_after_cost: Fraction
    k0: Fraction
    k1: Fraction
    information_value: Fraction


def worlds(prizes: int, inspect: int = 5) -> tuple[World, ...]:
    if not (0 <= prizes <= len(CARDS)-len(NAMED) and
            1 <= inspect <= len(CARDS)-len(NAMED)-prizes+len(NAMED)-3):
        raise ValueError("Invalid Prize or observation count")
    d = len(CARDS)-prizes
    result = []
    for picked in combinations(CARDS, prizes):
        excluded = set(picked)
        present = {name: name not in excluded for name in NAMED}
        before = d-int(present["Artazon"])
        after = before-int(present["TM"])-int(present["Jet"])
        if before < inspect or after < inspect:
            raise ValueError("Insufficient searchable cards")
        keep = Fraction(inspect, before) if present["Ticket"] else Fraction(0)
        pay = Fraction(inspect, after) if present["Ticket"] else Fraction(0)
        result.append(World(picked, keep, pay))
    return tuple(result)


def values(prizes: int, penalty: Fraction, inspect: int = 5) -> Values:
    if penalty < 0:
        raise ValueError("Negative penalty")
    all_worlds = worlds(prizes, inspect)
    n = len(all_worlds)
    keep = sum((w.keep for w in all_worlds), Fraction(0))/n
    paid = sum((w.pay for w in all_worlds), Fraction(0))/n - penalty
    k0 = max(keep, paid)
    k1 = sum((max(w.keep, w.pay-penalty) for w in all_worlds),
             Fraction(0))/n
    assert k1 >= k0
    return Values(keep, paid, k0, k1, k1-k0)


def gain_distribution(prizes: int) -> dict[Fraction, Fraction]:
    items = worlds(prizes)
    counts = Counter(w.gain for w in items)
    return {gain: Fraction(count,len(items)) for gain,count in counts.items()}


def switch_penalty(prizes: int) -> Fraction:
    """The K0 break-even cost, equal to expected benefit of paying."""
    ws = worlds(prizes)
    return sum((w.gain for w in ws), Fraction(0))/len(ws)
