"""Exact partial-observation policies for a G&H discard-before-search decision.

The synthetic physical pool has one Artazon, one spare TM, one spare Jet,
one Ticket target, and indistinguishable-for-payoff filler identities.
G&H is held; the two optional discards are assumed payable.
A named Prize-status signal is free information only, not a legal card action.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

NAMES = ("Artazon", "TM", "Jet", "Ticket")


@dataclass(frozen=True)
class PrizeWorld:
    prized: frozenset[str]
    mass: Fraction
    keep: Fraction
    pay: Fraction


@dataclass(frozen=True)
class ObservationPolicy:
    observed: tuple[str, ...]
    value: Fraction
    actions: dict[tuple[bool, ...], str]


def worlds(unseen: int, prizes: int, inspect: int) -> tuple[PrizeWorld, ...]:
    """Group the uniformly Prized physical pool into at most 16 exact worlds."""
    if unseen < 4 or prizes < 0 or prizes > unseen or not 1 <= inspect <= unseen-prizes-3:
        raise ValueError("Invalid pool size, Prize count or top-card horizon")
    filler = unseen-len(NAMES)
    denominator = comb(unseen, prizes)
    result = []
    for n_prized in range(min(prizes, len(NAMES))+1):
        count_fillers = prizes-n_prized
        if not 0 <= count_fillers <= filler:
            continue
        mass = Fraction(comb(filler, count_fillers), denominator)
        for subset in combinations(NAMES, n_prized):
            prized = frozenset(subset)
            deck = unseen-prizes
            keep_size = deck-int("Artazon" not in prized)
            paid_size = keep_size-int("TM" not in prized)-int("Jet" not in prized)
            keep = Fraction(inspect, keep_size) if "Ticket" not in prized else Fraction()
            pay = Fraction(inspect, paid_size) if "Ticket" not in prized else Fraction()
            result.append(PrizeWorld(prized, mass, keep, pay))
    assert sum((row.mass for row in result), Fraction()) == 1
    return tuple(result)


def optimize(
    unseen: int,
    prizes: int,
    inspect: int,
    penalty: Fraction,
    observed: tuple[str, ...] = (),
) -> ObservationPolicy:
    """Choose one pre-search pay/keep action for each available Prize signal.

    The player learns only whether the selected named identities are Prized.
    Post-payment G&H searches are allowed to adapt to the inspected deck.
    The penalty is an explicit hypothetical value of the discarded cards.
    """
    if penalty < 0:
        raise ValueError("The discard penalty must be nonnegative")
    if len(set(observed)) != len(observed) or any(n not in NAMES for n in observed):
        raise ValueError("Signals must be distinct named pool identities")
    grouped: dict[tuple[bool, ...], list[Fraction]] = {}
    for world in worlds(unseen, prizes, inspect):
        signal = tuple(name in world.prized for name in observed)
        totals = grouped.setdefault(signal, [Fraction(), Fraction()])
        totals[0] += world.mass*world.keep
        totals[1] += world.mass*(world.pay-penalty)
    actions = {signal: "pay" if pay > keep else "keep"
               for signal, (keep, pay) in sorted(grouped.items())}
    value = sum((max(keep, pay) for keep, pay in grouped.values()), Fraction())
    return ObservationPolicy(observed, value, actions)
