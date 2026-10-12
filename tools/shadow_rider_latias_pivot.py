"""Exact natural Latias ex Skyliner retreat access after Radiant launch.

One Latias ex among 13 non-Radiant Basic cards can be the starting Active or
can be played from hand onto a spare Bench position by attack time. Skyliner
then gives the starting Active Basic no Retreat Cost. Float Stone is alternate.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb, prod

from tools.shadow_rider_paid_ball_attack import COUNTS, ROUTES
from tools.shadow_rider_direct_launch_attack import allocations, choose


@dataclass(frozen=True)
class LatiasLaunch:
    launch: Fraction
    normal_energy_pivot: Fraction
    reduced_valley_pivot: Fraction
    either_pivot: Fraction
    overlap: Fraction
    states: int


@lru_cache(None)
def five_category_draw_window(
    he: int, de: int, n: int, hf: int, df: int,
    hl: int, dl: int, hv: int, dv: int,
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Exact Underworld Door outcome with Energy, Float, Latias and Valley."""
    if min(he, de, n, hf, df, hl, dl, hv, dv) < 0 or de+df+dl+dv > n:
        raise ValueError("invalid category inventory")
    states: dict[tuple[int, ...], Fraction] = {
        (he, hf, hl, hv, de, df, dl, dv, n, 0): Fraction(1),
    }
    for _ in range(2):
        next_states: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
        for (eh, fh, lh, vh, ed, fd, ld, vd, size, attached), mass in states.items():
            if not eh:
                next_states[(eh, fh, lh, vh, ed, fd, ld, vd, size, attached)] += mass
                continue
            drawn = min(2, size)
            for a in range(drawn+1):
                for b in range(drawn-a+1):
                    for c in range(drawn-a-b+1):
                        for d in range(drawn-a-b-c+1):
                            other = drawn-a-b-c-d
                            if (a > ed or b > fd or c > ld or d > vd
                                or other > size-ed-fd-ld-vd):
                                continue
                            chance = Fraction(
                                comb(ed, a)*comb(fd, b)*comb(ld, c)*comb(vd, d)
                                * comb(size-ed-fd-ld-vd, other),
                                comb(size, drawn),
                            )
                            key = (
                                eh-1+a, fh+b, lh+c, vh+d,
                                ed-a, fd-b, ld-c, vd-d, size-drawn, attached+1,
                            )
                            next_states[key] += mass*chance
        states = next_states
    assert sum(states.values(), Fraction()) == 1
    normal = valley = either = overlap = Fraction()
    for (eh, fh, lh, vh, *remaining), mass in states.items():
        attached = remaining[-1]
        total_energy = attached+int(eh > 0)
        pivot = fh > 0 or lh > 0
        normal_legal = pivot and total_energy >= 3
        valley_legal = pivot and total_energy >= 2 and vh > 0
        if normal_legal:
            normal += mass
        if valley_legal:
            valley += mass
        if normal_legal or valley_legal:
            either += mass
        if normal_legal and valley_legal:
            overlap += mass
    return normal, valley, either, overlap


def exact_latias(
    *,
    counts: tuple[int, int, int, int, int, int, int] = COUNTS,
    opening: int = 7,
    prizes: int = 6,
) -> dict[str, LatiasLaunch]:
    """Exact two-turn card zones with an exchangeable singleton Latias."""
    n = sum(counts)
    if min(counts) < 0 or counts[0] != 1 or counts[4] != 1 or counts[1] < 1 or counts[6] < 1:
        raise ValueError("requires Radiant, Latias, Float, Valley and Basic")
    if n-opening-prizes < 6:
        raise ValueError("insufficient residual deck")
    accepted = choose(n, opening)-choose(n-counts[0]-counts[1], opening)
    base = accepted*choose(n-opening, prizes)*(n-opening-prizes)
    masses: dict[tuple[str, int, int, int, int, int, int], Fraction] = defaultdict(Fraction)
    weighted_basic_hand: dict[tuple[str, int, int, int, int, int, int], Fraction] = defaultdict(Fraction)
    weighted_basic_deck: dict[tuple[str, int, int, int, int, int, int], Fraction] = defaultdict(Fraction)
    for hand in allocations(opening, counts):
        if not hand[1]:
            continue
        hand_ways = prod(choose(c, x) for c, x in zip(counts, hand))
        unseen = tuple(c-x for c, x in zip(counts, hand))
        for prize in allocations(prizes, unseen):
            prize_ways = prod(choose(c, x) for c, x in zip(unseen, prize))
            deck = tuple(c-x for c, x in zip(unseen, prize))
            for first, copies in enumerate(deck):
                if not copies:
                    continue
                after_first = list(deck)
                after_first[first] -= 1
                energy_hand = hand[3]+int(first == 3)
                ball_hand = hand[5]+int(first == 5)
                if hand[0]+int(first == 0):
                    route = "direct"
                    searched = 0
                    energy_paid = 0
                else:
                    route = "psychic_paid_ball"
                    if not (after_first[0] and ball_hand and energy_hand):
                        continue
                    searched = 1
                    energy_paid = 1
                if after_first[2] < 2:
                    continue
                after_first[0] -= searched
                after_first[2] -= 2
                remaining_draw = n-opening-prizes-3-searched
                weight = hand_ways*prize_ways*copies
                for second, count2 in enumerate(after_first):
                    if not count2:
                        continue
                    after_second = list(after_first)
                    after_second[second] -= 1
                    key = (
                        route,
                        energy_hand-energy_paid+int(second == 3), after_second[3],
                        hand[4]+int(first == 4)+int(second == 4), after_second[4],
                        hand[6]+int(first == 6)+int(second == 6), after_second[6],
                    )
                    mass = Fraction(weight*count2, base*remaining_draw)
                    masses[key] += mass
                    weighted_basic_hand[key] += mass*(
                        hand[1]+int(first == 1)+int(second == 1)
                    )
                    weighted_basic_deck[key] += mass*after_second[1]
    subtotals = {
        route:dict(launch=Fraction(), normal=Fraction(), valley=Fraction(),
                   either=Fraction(), overlap=Fraction(), states=0)
        for route in ROUTES
    }
    for key, mass in masses.items():
        route, he, de, hf, df, neutral_hand, neutral_deck = key
        remaining = n-opening-prizes-4-int(route == "psychic_paid_ball")
        p_lh = weighted_basic_hand[key]/mass/counts[1]
        p_ld = weighted_basic_deck[key]/mass/counts[1]
        p_lp = 1-p_lh-p_ld
        p_vh = Fraction(neutral_hand, counts[6])
        p_vd = Fraction(neutral_deck, counts[6])
        p_vp = 1-p_vh-p_vd
        row = subtotals[route]
        row["launch"] += mass
        row["states"] += 1
        for lh, ld, p_latias in (
            (1, 0, p_lh), (0, 1, p_ld), (0, 0, p_lp),
        ):
            if not p_latias:
                continue
            for vh, vd, p_valley in (
                (1, 0, p_vh), (0, 1, p_vd), (0, 0, p_vp),
            ):
                if not p_valley:
                    continue
                outcome = five_category_draw_window(
                    he, de, remaining, hf, df, lh, ld, vh, vd,
                )
                for name, value in zip(("normal", "valley", "either", "overlap"), outcome):
                    row[name] += mass*p_latias*p_valley*value
    return {
        route:LatiasLaunch(
            d["launch"], d["normal"], d["valley"], d["either"], d["overlap"],
            d["states"],
        )
        for route, d in subtotals.items()
    }
