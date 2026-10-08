"""Exact access comparison for Quick Ball and Ultra Ball as Sky Field feeders."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

from teleport_discard_access_bound import at_least_one_of_each


@dataclass(frozen=True)
class Case:
    n: int
    prizes: int
    seen: int
    connectors: int
    sky: int
    discard: int
    needs_second_discard: bool
    target_searchable: bool


@dataclass(frozen=True)
class Result:
    found_in_deck: Fraction
    naturally_held: Fraction

    @property
    def goal(self) -> Fraction:
        return self.found_in_deck + self.naturally_held


def calculate(case: Case) -> Result:
    n, p, h = case.n, case.prizes, case.seen
    groups = (case.connectors, case.sky)
    if case.needs_second_discard:
        groups += (case.discard,)
    if not (n > 0 and 0 <= p < n and 0 <= h <= n-p
            and min(groups) >= 0 and sum(groups) + 1 <= n):
        raise ValueError("invalid partition")
    in_deck = (
        Fraction(n-p-h, n) * at_least_one_of_each(n-1, h, groups)
        if case.target_searchable else Fraction(0)
    )
    in_hand = (
        Fraction(h, n) * at_least_one_of_each(n-1, h-1, groups)
        if h else Fraction(0)
    )
    return Result(in_deck, in_hand)


def exhaustive(case: Case) -> Result:
    """Independent labeled Prize and hand enumeration for small cases."""
    n, p, h = case.n, case.prizes, case.seen
    labels = (
        "C" * case.connectors + "S" * case.sky
        + "D" * case.discard + "T"
    )
    labels += "F" * (n-len(labels))
    total = in_deck = in_hand = 0
    universe = tuple(range(n))
    for prize in combinations(universe, p):
        prize_positions = set(prize)
        for hand in combinations(
            (i for i in universe if i not in prize_positions), h
        ):
            total += 1
            seen = {labels[i] for i in hand}
            if not {"C", "S"} <= seen:
                continue
            if case.needs_second_discard and "D" not in seen:
                continue
            if "T" in seen:
                in_hand += 1
            elif case.target_searchable and all(labels[i] != "T" for i in prize):
                in_deck += 1
    assert total == comb(n, p) * comb(n-p, h)
    return Result(Fraction(in_deck, total), Fraction(in_hand, total))


def compare() -> dict[str, Result]:
    same = dict(n=46, prizes=6, seen=5, connectors=4, sky=2, discard=16)
    return {
        "quick_basic": calculate(Case(**same, needs_second_discard=False, target_searchable=True)),
        "ultra_basic": calculate(Case(**same, needs_second_discard=True, target_searchable=True)),
        "quick_evolution_access": calculate(Case(**same, needs_second_discard=False, target_searchable=False)),
        "ultra_evolution_access": calculate(Case(**same, needs_second_discard=True, target_searchable=True)),
    }
