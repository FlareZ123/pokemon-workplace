"""Scalable exact K0/K1 G&H spare-search frontier for realistic hidden pools.

Only four named categories matter: Artazon, spare TM: Evolution,
spare Jet Energy, one desired Ticket; the other unseen cards are
exchangeable fillers. A free K1 Prize map is a counterfactual reference.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.prized_filler_search_invariance import exact as thinning_hit


NAMED = ("Artazon", "TM", "Jet", "Ticket")


@dataclass(frozen=True)
class Frontier:
    unseen: int
    prizes: int
    inspect: int
    penalty: Fraction
    keep: Fraction
    paid_after_cost: Fraction
    k0: Fraction
    k1: Fraction
    information_value: Fraction
    switch_penalty: Fraction


def calculate(
    unseen: int, prizes: int, inspect: int, penalty: Fraction,
) -> Frontier:
    if (unseen < 4 or prizes < 0 or inspect < 1
            or inspect > unseen-3-prizes or penalty < 0):
        raise ValueError("Invalid physical pool, observation horizon, or cost")

    other = unseen-len(NAMED)
    total = comb(unseen,prizes)
    mean_keep = mean_paid = mean_k1 = Fraction(0)
    weight_total = Fraction(0)

    for count_named in range(min(prizes,len(NAMED))+1):
        remainder = prizes-count_named
        if not 0 <= remainder <= other:
            continue
        weight = Fraction(comb(other,remainder),total)
        for selected in combinations(NAMED,count_named):
            prized = set(selected)
            n = unseen-prizes-int("Artazon" not in prized)
            paid_n = n-int("TM" not in prized)-int("Jet" not in prized)
            keep = Fraction(inspect,n) if "Ticket" not in prized else Fraction(0)
            pay = Fraction(inspect,paid_n) if "Ticket" not in prized else Fraction(0)
            mean_keep += weight*keep
            mean_paid += weight*(pay-penalty)
            mean_k1 += weight*max(keep,pay-penalty)
            weight_total += weight
    assert weight_total == 1
    switch = thinning_hit(unseen,prizes,3,inspect) - thinning_hit(
        unseen,prizes,1,inspect)
    assert mean_keep == thinning_hit(unseen,prizes,1,inspect)
    assert mean_paid+penalty == thinning_hit(unseen,prizes,3,inspect)
    k0 = max(mean_keep,mean_paid)
    assert mean_k1 >= k0
    return Frontier(unseen,prizes,inspect,penalty,mean_keep,
                    mean_paid,k0,mean_k1,mean_k1-k0,switch)
