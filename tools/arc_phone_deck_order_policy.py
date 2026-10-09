"""Finite deck-order/Prize belief planner for Arc Phone and Trekking Shoes."""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations


def normalize(masses):
    total = sum(masses.values(), Fraction())
    return tuple(sorted(((state, p / total) for state, p in masses.items() if p),
                        key=lambda row: row[0]))


def exact_unknown_orders(prizes, deck):
    worlds = {(p, d) for p in set(permutations(prizes))
                       for d in set(permutations(deck))}
    return normalize({w: Fraction(1, len(worlds)) for w in worlds})


def observe(belief, deck_position):
    split = defaultdict(lambda: defaultdict(Fraction))
    for state, weight in belief:
        split[state[1][deck_position]][state] += weight
    return {card: (sum(worlds.values(), Fraction()), normalize(worlds))
            for card, worlds in split.items()}


def arc_swap(belief, slot):
    outcomes = defaultdict(Fraction)
    for (prizes, deck), weight in belief:
        p, d = list(prizes), list(deck)
        p[slot], d[0] = d[0], p[slot]
        outcomes[(tuple(p), tuple(d))] += weight
    return normalize(outcomes)


def draw(belief, count):
    outcomes = defaultdict(Fraction)
    for (prizes, deck), weight in belief:
        outcomes[(prizes, deck[count:])] += weight
    return normalize(outcomes)


@lru_cache(None)
def optimize(belief, arc, shoes, allow_discard=True):
    """Exact maximal P(put target T in hand), conditioned on current belief."""
    if not belief[0][0][1] or not (arc or shoes):
        return Fraction()
    top_groups = observe(belief, 0)
    actions = [Fraction()]
    if arc:
        value = Fraction()
        for _, (weight, seen) in top_groups.items():
            candidates = [optimize(seen, arc - 1, shoes, allow_discard)]
            candidates.extend(optimize(arc_swap(seen, i), arc - 1, shoes,
                                       allow_discard)
                              for i in range(len(seen[0][0][0])))
            value += weight * max(candidates)
        actions.append(value)
    if shoes:
        value = Fraction()
        for card, (weight, seen) in top_groups.items():
            keep = Fraction(1) if card == "T" else optimize(
                draw(seen, 1), arc + (card == "A"),
                shoes - 1 + (card == "S"), allow_discard)
            if allow_discard and len(seen[0][0][1]) >= 2:
                discard = sum(
                    (p * (Fraction(1) if next_card == "T" else optimize(
                        draw(conditioned, 2), arc + (next_card == "A"),
                        shoes - 1 + (next_card == "S"), allow_discard))
                     for next_card, (p, conditioned) in observe(seen, 1).items()),
                    Fraction())
                keep = max(keep, discard)
            value += weight * keep
        actions.append(value)
    return max(actions)
