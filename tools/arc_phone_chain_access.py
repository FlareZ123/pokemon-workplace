"""Exact hand/Prize availability model for consecutive Arc Phone probes.

The model is deliberately limited to a fixed, already-seen hand window. It
excludes search/draw effects other than the final Trekking Shoes endpoint.
One target singleton is known to begin in the Prize zone.
"""
from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from itertools import product
from math import comb


# Category order: target singleton, Peonia, Arc Phone, Trekking Shoes, filler.
DEFAULT_DECK = (1, 1, 4, 4, 50)


def _choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def _selected_counts(prizes: tuple[int, ...], count: int):
    """Hypergeometric, without observing which physical positions are sampled."""
    target, supporter, arc, shoes, filler = prizes
    denominator = comb(sum(prizes), count)
    for t in range(min(target, count) + 1):
        for p in range(min(supporter, count - t) + 1):
            for a in range(min(arc, count - t - p) + 1):
                for s in range(min(shoes, count - t - p - a) + 1):
                    f = count - t - p - a - s
                    weight = (_choose(target, t) * _choose(supporter, p)
                              * _choose(arc, a) * _choose(shoes, s)
                              * _choose(filler, f))
                    if weight:
                        yield (t, p, a, s, f), Fraction(weight, denominator)


@lru_cache(maxsize=None)
def _best_probes_after_return(arc: int, shoes: int, filler: int,
                              returned: int, remaining_prizes: int,
                              chained: bool) -> int:
    """Maximum same-turn distinct probes after replacing Peonia Prize cards.

    Peonia's replacement choices are visible-hand decisions. A non-essential
    filler is always an acceptable replacement; otherwise Item copies must be
    surrendered. The endpoint needs a retained Trekking Shoes.
    """
    best = 0
    for paid_arc in range(min(arc, returned) + 1):
        for paid_shoes in range(min(shoes, returned - paid_arc) + 1):
            paid_filler = returned - paid_arc - paid_shoes
            if paid_filler > filler:
                continue
            usable_arc = arc - paid_arc
            usable_shoes = shoes - paid_shoes
            if usable_shoes == 0:
                continue
            probes = usable_arc if chained else min(usable_arc, usable_shoes)
            best = max(best, min(probes, remaining_prizes))
    return best


@lru_cache(maxsize=None)
def _peonia_value(prizes: tuple[int, ...], hand: tuple[int, ...],
                  selected: int, chained: bool) -> Fraction:
    """Hit chance for a fixed count of Peonia-selected slots.

    Input hand contains the Peonia being played. TARGET is absent from hand.
    The player's later choices may depend on revealed Peonia cards but not on
    unobserved Prize-slot identities.
    """
    count = sum(prizes)
    value = Fraction()
    for picked, probability in _selected_counts(prizes, selected):
        t, _p, a, s, f = picked
        if t:
            # Peonia must put selected cards back into the Prize zone.
            # With only Peonia originally in hand, no other card can pay
            # the replacement while keeping TARGET.
            if sum(hand) > 1:
                value += probability
            continue
        remaining = count - selected
        probes = _best_probes_after_return(
            hand[2] + a, hand[3] + s, hand[4] + f,
            selected, remaining, chained,
        )
        value += probability * Fraction(probes, remaining)
    return value


@lru_cache(maxsize=None)
def _state_value(prizes: tuple[int, ...], hand: tuple[int, ...],
                 chained: bool, peonia_limit: int, optimize_peonia: bool) -> Fraction:
    count = sum(prizes)
    arc, shoes = hand[2:4]
    basic = Fraction(min(arc, count), count) if shoes and chained else (
        Fraction(min(arc, shoes, count), count) if shoes else Fraction()
    )
    if hand[1] == 0 or peonia_limit == 0:
        return basic
    options = [_peonia_value(prizes, hand, n, chained)
               for n in range(1, min(peonia_limit, count) + 1)]
    return max([basic, *options]) if optimize_peonia else options[-1]


def exact_access(*, seen: int, deck: tuple[int, ...] = DEFAULT_DECK,
                 prize_count: int = 6, peonia_limit: int = 3,
                 chained: bool = True, optimize_peonia: bool = True) -> Fraction:
    """P(target acquired | target starts Prized) in a fixed hand window.

    Exact two-stage multivariate hypergeometric enumeration. The remaining
    non-target Prize cards are sampled first, then \`seen\` cards are available
    in hand from the remainder. A singleton TARGET is pinned into the Prizes.
    """
    if deck[0] != 1 or any(n < 0 for n in deck):
        raise ValueError("deck requires one target and nonnegative categories")
    size = sum(deck)
    if not 1 <= prize_count < size or not 0 <= seen <= size - prize_count:
        raise ValueError("invalid Prize or hand size")
    if not 0 <= peonia_limit <= prize_count:
        raise ValueError("invalid Peonia limit")

    population = list(deck)
    population[0] -= 1
    denom_prize = comb(size - 1, prize_count - 1)
    denom_hand = comb(size - prize_count, seen)
    total = Fraction()
    for pp in product(*[range(min(n, prize_count - 1) + 1) for n in population[1:4]]):
        p, a, s = pp
        f = prize_count - 1 - p - a - s
        prize_weight = _choose(population[1], p) * _choose(population[2], a) * _choose(population[3], s) * _choose(population[4], f)
        if not prize_weight:
            continue
        prizes = (1, p, a, s, f)
        left = tuple(pool - taken for pool, taken in zip(population[1:], prizes[1:]))
        for hp in range(min(left[0], seen) + 1):
            for ha in range(min(left[1], seen - hp) + 1):
                for hs in range(min(left[2], seen - hp - ha) + 1):
                    hf = seen - hp - ha - hs
                    hand_weight = (_choose(left[0], hp) * _choose(left[1], ha)
                                   * _choose(left[2], hs) * _choose(left[3], hf))
                    if not hand_weight:
                        continue
                    hand = (0, hp, ha, hs, hf)
                    probability = Fraction(prize_weight * hand_weight, denom_prize * denom_hand)
                    total += probability * _state_value(
                        prizes, hand, chained, peonia_limit, optimize_peonia
                    )
    return total


def fixed_resource_case(*, prize_count: int = 6, peonia_checked: int = 3,
                        arc: int = 3, shoes: int = 1) -> tuple[Fraction, Fraction]:
    """Access chance with preavailable Trainers and expendable replacements."""
    p = prize_count
    k = min(arc, p - peonia_checked)
    chained = Fraction(peonia_checked + (k if shoes else 0), p)
    repeated = Fraction(peonia_checked + min(k, shoes), p)
    return chained, repeated


if __name__ == "__main__":
    for seen in (7, 10, 13, 16):
        c = exact_access(seen=seen)
        r = exact_access(seen=seen, chained=False)
        print(f"seen={seen}: chain={float(c):.9%}, repeated_shoes={float(r):.9%}, gain_pp={float(100*(c-r)):.7f}")
