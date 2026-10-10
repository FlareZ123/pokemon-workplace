"""Optimal physical target hand/discard placement via Crobat and Dedenne.

The target is uniform among earlier draws, Prize cards and live deck.
Both hand-to-Bench support Basics are available, with two Bench slots.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product


@dataclass(frozen=True)
class Policy:
    initial_found: str
    initial_missing: str
    crobat_found: str
    crobat_missing: str


@dataclass(frozen=True)
class Outcome:
    policy: Policy
    hand: Fraction
    discarded: Fraction
    bench: Fraction
    utility: Fraction


def all_policies():
    for first,root,hit,miss in product(
            ("stop","dede"),("stop","dede","crobat"),
            ("stop","dede"),("stop","dede")):
        yield Policy(first,root,hit,miss)


def evaluate(policy: Policy, *, hand_value: Fraction = Fraction(1),
             discard_value: Fraction = Fraction(0),
             bench_cost: Fraction = Fraction(0), earlier: int = 1,
             prizes: int = 6, deck: int = 46, crobat_draw: int = 2) -> Outcome:
    if min(earlier, prizes, deck, crobat_draw) < 0 or deck < crobat_draw + 6:
        raise ValueError("invalid draw model")
    n = earlier + prizes + deck
    counts = [0,0,0]
    for idx in range(n):
        in_hand = idx < earlier
        live_index = idx - earlier - prizes
        discard = False
        bench = 0
        if in_hand:
            if policy.initial_found == "dede":
                in_hand, discard, bench = False, True, 1
        elif policy.initial_missing == "dede":
            in_hand = 0 <= live_index < 6
            bench = 1
        elif policy.initial_missing == "crobat":
            bench = 1
            if 0 <= live_index < crobat_draw:
                in_hand = True
                if policy.crobat_found == "dede":
                    in_hand,discard,bench = False,True,2
            elif policy.crobat_missing == "dede":
                in_hand = crobat_draw <= live_index < crobat_draw+6
                bench = 2
        counts[0] += int(in_hand)
        counts[1] += int(discard)
        counts[2] += bench
    H,G,B = (Fraction(x,n) for x in counts)
    return Outcome(policy,H,G,B,
                   H*hand_value+G*discard_value-B*bench_cost)


def optimize(*, hand_value: Fraction = Fraction(1),
             discard_value: Fraction = Fraction(0),
             bench_cost: Fraction = Fraction(0), earlier: int = 1,
             prizes: int = 6, deck: int = 46, crobat_draw: int = 2) -> Outcome:
    if min(hand_value, discard_value, bench_cost) < 0:
        raise ValueError("negative utility")
    outcomes = (evaluate(p,hand_value=hand_value,discard_value=discard_value,
                         bench_cost=bench_cost,earlier=earlier,prizes=prizes,
                         deck=deck,crobat_draw=crobat_draw)
                for p in all_policies())
    return max(outcomes,key=lambda x:(x.utility,-x.bench))


def closed_optimal_value(*, hand_value: Fraction = Fraction(1),
                         discard_value: Fraction = Fraction(0),
                         bench_cost: Fraction = Fraction(0), earlier: int = 1,
                         prizes: int = 6, deck: int = 46,
                         crobat_draw: int = 2) -> Fraction:
    """Exact nonanticipative decision-tree envelope with no peek at Prizes."""
    if min(earlier,prizes,deck,crobat_draw) < 0 or deck < crobat_draw + 6:
        raise ValueError("invalid draw model")
    total = earlier + prizes + deck
    unseen = total - earlier
    H,G,C = hand_value,discard_value,bench_cost
    a = crobat_draw
    held = max(H,G-C)
    dede = Fraction(6,unseen)*H-C
    after_crobat_miss = max(Fraction(0),Fraction(6,unseen-a)*H-C)
    crobat = (-C + Fraction(a,unseen)*held
              + Fraction(unseen-a,unseen)*after_crobat_miss)
    return (Fraction(earlier,total)*held
            +Fraction(unseen,total)*max(Fraction(0),dede,crobat))
