"""Exact Tool side-payload access on the Aichi Iron Thorns G&H line."""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import product


@dataclass(frozen=True)
class Counts:
    iron: int = 4
    tag: int = 2
    gh: int = 2
    mountain: int = 1
    dce: int = 1
    tools: int = 3
    deck_size: int = 60
    opening: int = 7
    prizes: int = 6

    @property
    def filler(self) -> int:
        return self.deck_size - sum((self.iron, self.tag, self.gh, self.mountain, self.dce, self.tools))


@dataclass(frozen=True)
class Result:
    accepted_opening: Fraction
    direct: Fraction
    mediated_discard: Fraction
    mediated_discard_with_tool: Fraction
    mediated_no_discard: Fraction
    unavailable: Fraction
    connector_failure: Fraction
    tool_distribution_given_discard: tuple[Fraction, ...]

    @property
    def tool_available_given_discard(self) -> Fraction:
        return self.mediated_discard_with_tool / self.mediated_discard if self.mediated_discard else Fraction()

    @property
    def expected_tools_in_deck_given_discard(self) -> Fraction:
        return sum(Fraction(i) * p for i, p in enumerate(self.tool_distribution_given_discard))


def _alloc(total: int, caps: tuple[int, ...]):
    for values in product(*(range(min(c, total) + 1) for c in caps)):
        if sum(values) == total:
            yield values


def exact(counts: Counts) -> Result:
    if counts.filler < 0:
        raise ValueError("card counts exceed deck size")
    cats = (counts.iron, counts.tag, counts.gh, counts.mountain, counts.dce, counts.tools, counts.filler)
    accepted = math.comb(counts.deck_size, counts.opening) - math.comb(counts.deck_size - counts.iron, counts.opening)
    after_open = counts.deck_size - counts.opening
    after_prizes = after_open - counts.prizes
    denominator = accepted * math.comb(after_open, counts.prizes) * after_prizes
    direct = discard = discard_tool = no_discard = unavailable = connector_fail = 0
    tool_weights = [0] * (counts.tools + 1)

    for opening in _alloc(counts.opening, cats):
        if opening[0] == 0:
            continue
        opening_ways = math.prod(math.comb(n, k) for n, k in zip(cats, opening))
        left = tuple(n - k for n, k in zip(cats, opening))
        for prizes in _alloc(counts.prizes, left):
            prize_ways = math.prod(math.comb(n, k) for n, k in zip(left, prizes))
            deck0 = tuple(n - k for n, k in zip(left, prizes))
            for draw, copies in enumerate(deck0):
                if copies == 0:
                    continue
                hand = [opening[i] + (i == draw) for i in range(len(cats))]
                hand[0] -= 1
                deck = [deck0[i] - (i == draw) for i in range(len(cats))]
                weight = opening_ways * prize_ways * copies
                tag_h, gh_h, m_h, dce_h = hand[1:5]
                gh_d, m_d, dce_d, tools_d = deck[2:6]

                if m_h and dce_h:
                    direct += weight
                elif not ((m_h or m_d) and (dce_h or dce_d)):
                    unavailable += weight
                elif not (gh_h or (tag_h and gh_d)):
                    connector_fail += weight
                elif dce_h:
                    no_discard += weight
                else:
                    discard += weight
                    tool_weights[tools_d] += weight
                    if tools_d:
                        discard_tool += weight

    if direct + discard + no_discard + unavailable + connector_fail != denominator:
        raise AssertionError("state partition mismatch")
    dist = tuple(Fraction(w, discard) for w in tool_weights) if discard else tuple(Fraction() for _ in tool_weights)
    f = lambda x: Fraction(x, denominator)
    return Result(Fraction(accepted, math.comb(counts.deck_size, counts.opening)), f(direct), f(discard), f(discard_tool), f(no_discard), f(unavailable), f(connector_fail), dist)
