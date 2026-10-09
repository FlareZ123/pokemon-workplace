"""Exact joint turn-one Quick Ball/Sky Field and turn-two Gothitelle access.

The modeled dual-use line spends Quick Ball on turn one, discards Sky Field,
and establishes Gothita naturally or by searching the remaining physical
deck. One natural draw on turn two may finish Rare Candy + Gothitelle.
This measures card access conditional on a separately supplied board/lock
state, not full-board establishment or matchup win rate.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class DualUseSetup:
    total: int = 60
    opening: int = 7
    prizes: int = 6
    gothita: int = 3
    gothitelle: int = 2
    rare_candy: int = 4
    other_basics: int = 8
    quick_ball: int = 4
    sky_field: int = 2

    @property
    def categories(self) -> tuple[int, ...]:
        head = (
            self.gothita, self.gothitelle, self.rare_candy,
            self.other_basics, self.quick_ball, self.sky_field,
        )
        return head + (self.total - sum(head),)

    def __post_init__(self) -> None:
        if (
            min(self.categories) < 0
            or self.opening < 1
            or self.prizes < 0
            or self.total - self.opening - self.prizes - 2 <= 0
            or self.gothita + self.other_basics == 0
        ):
            raise ValueError("invalid joint-access partition or setup window")


@dataclass(frozen=True)
class DualUseOdds:
    natural_gothita: Fraction
    searched_gothita: Fraction
    legal_opener: Fraction

    @property
    def per_attempt(self) -> Fraction:
        return self.natural_gothita + self.searched_gothita

    @property
    def conditional_legal_opener(self) -> Fraction:
        return self.per_attempt / self.legal_opener


def searched_continuation(
    case: DualUseSetup,
    remaining: tuple[int, ...],
    *,
    gothitelle_seen: bool,
    candy_seen: bool,
) -> Fraction:
    """Marginalize joint Prize composition before a paid Basic search.

    The total of `remaining` is the unknown pool after opening plus first
    natural draw. Six Prizes occupy a random subset of this pool. Searching
    removes one unprized Gothita from the physical deck, shrinking the
    turn-two draw denominator by one. A single draw cannot obtain two
    simultaneously missing cards.
    """
    unknown = sum(remaining)
    g = remaining[0]
    if not g or (not gothitelle_seen and not candy_seen):
        return Fraction(0)
    deck_after_search = unknown - case.prizes - 1
    if deck_after_search <= 0:
        return Fraction(0)
    total_prize_subsets = choose(unknown, case.prizes)
    result = Fraction(0)
    for g_prized in range(min(g, case.prizes) + 1):
        if g_prized == g:
            continue
        other_prized = case.prizes - g_prized
        ways = choose(g, g_prized) * choose(unknown - g, other_prized)
        if not ways:
            continue
        if gothitelle_seen and candy_seen:
            turn_two = Fraction(1)
        else:
            missing = 2 if gothitelle_seen else 1
            # Other Prize cards are exchangeable conditional on g_prized.
            expected_outs = Fraction(
                remaining[missing] * (unknown - g - other_prized),
                unknown - g,
            )
            turn_two = expected_outs / deck_after_search
        result += Fraction(ways, total_prize_subsets) * turn_two
    return result


def exact_dual_use_access(case: DualUseSetup) -> DualUseOdds:
    """Exact 7-card opener, 6 random Prizes, T1 draw and T2 draw.

    The first natural draw can be integrated before Prize placement by
    exchangeability; the conditional physical search and final draw cannot.
    The two branches distinguish natural Gothita from a deck-searched one.
    """
    sizes = case.categories
    n = case.total
    h = case.opening
    first_draw_denominator = choose(n, h) * (n - h)
    natural = Fraction(0)
    searched = Fraction(0)
    for six_counts in product(
        *(range(min(size, h) + 1) for size in sizes[:6])
    ):
        filler = h - sum(six_counts)
        if filler < 0 or filler > sizes[6]:
            continue
        opener = six_counts + (filler,)
        if not opener[0] and not opener[3]:
            continue
        ways = 1
        for capacity, observed in zip(sizes, opener):
            ways *= choose(capacity, observed)
        remainder = tuple(a - b for a, b in zip(sizes, opener))
        for first_type, available in enumerate(remainder):
            if not available:
                continue
            seen = tuple(
                count + int(index == first_type)
                for index, count in enumerate(opener)
            )
            if not seen[4] or not seen[5]:
                continue
            after_first = list(remainder)
            after_first[first_type] -= 1
            weight = Fraction(
                ways * available, first_draw_denominator
            )
            t_seen, c_seen = bool(seen[1]), bool(seen[2])
            if seen[0]:
                if t_seen and c_seen:
                    chance = Fraction(1)
                elif t_seen:
                    chance = Fraction(after_first[2], n - h - 1)
                elif c_seen:
                    chance = Fraction(after_first[1], n - h - 1)
                else:
                    chance = Fraction(0)
                natural += weight * chance
            else:
                searched += weight * searched_continuation(
                    case, tuple(after_first),
                    gothitelle_seen=t_seen, candy_seen=c_seen,
                )

    basic_total = case.gothita + case.other_basics
    legal = Fraction(
        choose(n, h) - choose(n - basic_total, h), choose(n, h)
    )
    return DualUseOdds(natural, searched, legal)
