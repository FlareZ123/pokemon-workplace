"""Exact same-pool Quick Ball / Ultra Ball policy for Teleport Room feed.

Two search Items coexist. The player can use Quick Ball as a one-card
Sky Field discard and Basic search, or Ultra Ball as Sky Field+other payment
and a broader Pokémon search. Quick Ball itself may pay Ultra Ball when the
target is an Evolution Pokémon Quick Ball cannot retrieve.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

from teleport_discard_access_bound import at_least_one_of_each


@dataclass(frozen=True)
class SharedPool:
    n: int
    prizes: int
    seen: int
    quick: int
    ultra: int
    sky: int
    other_payment: int

    def __post_init__(self) -> None:
        counts = (
            self.quick, self.ultra, self.sky, self.other_payment, 1
        )
        if (
            self.n <= 0 or not 0 <= self.prizes < self.n
            or not 0 <= self.seen <= self.n-self.prizes
            or min(counts) < 0 or sum(counts) > self.n
        ):
            raise ValueError("invalid physical category partition")


@dataclass(frozen=True)
class PolicyOutcome:
    target_searched: Fraction
    target_held: Fraction

    @property
    def goal(self) -> Fraction:
        return self.target_searched + self.target_held


def _all(pop: int, sample: int, *groups: int) -> Fraction:
    return at_least_one_of_each(pop, sample, groups)


def _basic_any_feeder(pop: int, sample: int, spec: SharedPool) -> Fraction:
    """S & (Q OR (U & D)), with Quick preferred when present."""
    s, q, u, d = spec.sky, spec.quick, spec.ultra, spec.other_payment
    return (
        _all(pop, sample, s, q)
        + _all(pop, sample, s, u, d)
        - _all(pop, sample, s, q, u, d)
    )


def _evolution_search_feeder(pop: int, sample: int, spec: SharedPool) -> Fraction:
    """S & U & (D OR Q); Quick Ball can pay Ultra Ball."""
    s, q, u, d = spec.sky, spec.quick, spec.ultra, spec.other_payment
    return (
        _all(pop, sample, s, u, d)
        + _all(pop, sample, s, u, q)
        - _all(pop, sample, s, u, q, d)
    )


def k0_policy(spec: SharedPool, *, evolution_target: bool) -> PolicyOutcome:
    n, p, h = spec.n, spec.prizes, spec.seen
    target_in_deck = Fraction(n-p-h, n)
    target_in_hand = Fraction(h, n)
    search_branch = (
        _evolution_search_feeder(n-1, h, spec) if evolution_target
        else _basic_any_feeder(n-1, h, spec)
    )
    hand_branch = (
        _basic_any_feeder(n-1, h-1, spec) if h else Fraction(0)
    )
    return PolicyOutcome(
        target_searched=target_in_deck * search_branch,
        target_held=target_in_hand * hand_branch,
    )


def k0_quick_only(spec: SharedPool, *, evolution_target: bool) -> PolicyOutcome:
    n, p, h = spec.n, spec.prizes, spec.seen
    return PolicyOutcome(
        target_searched=(
            Fraction(0) if evolution_target
            else Fraction(n-p-h,n) * _all(n-1,h,spec.sky,spec.quick)
        ),
        target_held=(
            Fraction(h,n) * _all(n-1,h-1,spec.sky,spec.quick)
            if h else Fraction(0)
        ),
    )


def k0_ultra_only(spec: SharedPool) -> PolicyOutcome:
    n,p,h = spec.n,spec.prizes,spec.seen
    return PolicyOutcome(
        target_searched=Fraction(n-p-h,n)*_all(
            n-1,h,spec.sky,spec.ultra,spec.other_payment
        ),
        target_held=Fraction(h,n)*_all(
            n-1,h-1,spec.sky,spec.ultra,spec.other_payment
        ) if h else Fraction(0),
    )


def exhaustive(spec: SharedPool, *, evolution_target: bool) -> PolicyOutcome:
    """Independent enumeration of all labeled Prize and hand combinations."""
    labels = (
        "Q"*spec.quick + "U"*spec.ultra
        + "S"*spec.sky + "D"*spec.other_payment + "T"
    )
    labels += "F"*(spec.n-len(labels))
    universe = tuple(range(spec.n))
    searched=held=total=0
    for prize in combinations(universe,spec.prizes):
        prizes=set(prize)
        for hand in combinations(
            (i for i in universe if i not in prizes), spec.seen
        ):
            total+=1
            hand_classes={labels[i] for i in hand}
            if "T" in {labels[i] for i in prize}:
                continue
            if "S" not in hand_classes:
                continue
            has_q="Q" in hand_classes
            has_u="U" in hand_classes
            has_d="D" in hand_classes
            if "T" in hand_classes:
                # Any live Sky feeder works: Q alone or U + another D.
                if has_q or (has_u and has_d):
                    held+=1
            else:
                can_feed = (
                    (has_u and (has_q or has_d))
                    if evolution_target
                    else (has_q or (has_u and has_d))
                )
                if can_feed:
                    searched+=1
    assert total == comb(spec.n,spec.prizes)*comb(
        spec.n-spec.prizes,spec.seen
    )
    return PolicyOutcome(Fraction(searched,total),Fraction(held,total))


def example() -> dict[str, PolicyOutcome]:
    spec=SharedPool(
        n=46, prizes=6, seen=5,
        quick=4, ultra=4, sky=2, other_payment=16,
    )
    return {
        "quick_basic_only":k0_quick_only(spec,evolution_target=False),
        "ultra_only":k0_ultra_only(spec),
        "joint_basic_policy":k0_policy(spec,evolution_target=False),
        "quick_evolution_only":k0_quick_only(spec,evolution_target=True),
        "joint_evolution_policy":k0_policy(spec,evolution_target=True),
    }
