"""First-turn Quick Ball + Battle VIP Pass in a four-core Gothitelle line.

Quick Ball pays Sky Field and searches one Basic. Battle VIP Pass may
put up to two additional unprized Basic Pokemon from the physical deck
directly onto the Bench, but only on turn one. A natural second-turn
draw may finish Gothitelle + Rare Candy. The compatible opponent's
Stadium/lock state remains exogenous.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from gothitelle_dual_use_joint_access import DualUseSetup, choose
from gothitelle_two_quick_joint_board import prize_conditioned_basic_search


@dataclass(frozen=True)
class QuickVIPSetup:
    total: int = 60
    opening: int = 7
    prizes: int = 6
    gothita: int = 3
    gothitelle: int = 2
    rare_candy: int = 4
    other_basics: int = 8
    quick_ball: int = 4
    sky_field: int = 2
    battle_vip_pass: int = 4

    @property
    def categories(self) -> tuple[int, ...]:
        first = (
            self.gothita, self.gothitelle, self.rare_candy,
            self.other_basics, self.quick_ball, self.sky_field,
            self.battle_vip_pass,
        )
        return first + (self.total - sum(first),)

    def __post_init__(self) -> None:
        if (
            min(self.categories) < 0 or self.opening < 1
            or self.prizes < 0
            or self.total - self.opening - self.prizes - 4 <= 0
            or self.other_basics == 0
        ):
            raise ValueError("invalid Quick/VIP category partition")

    def one_quick_projection(self) -> DualUseSetup:
        return DualUseSetup(
            total=self.total, opening=self.opening,
            prizes=self.prizes, gothita=self.gothita,
            gothitelle=self.gothitelle, rare_candy=self.rare_candy,
            other_basics=self.other_basics,
            quick_ball=self.quick_ball, sky_field=self.sky_field,
        )


@dataclass(frozen=True)
class QuickVIPOdds:
    naturally_complete: Fraction
    one_basic_search: Fraction
    two_basic_searches: Fraction
    three_basic_searches: Fraction
    legal_opener: Fraction

    @property
    def per_attempt(self) -> Fraction:
        return sum((
            self.naturally_complete, self.one_basic_search,
            self.two_basic_searches, self.three_basic_searches,
        ), Fraction(0))

    @property
    def vip_increment(self) -> Fraction:
        return self.two_basic_searches + self.three_basic_searches

    @property
    def conditional_legal_opener(self) -> Fraction:
        return self.per_attempt / self.legal_opener


def exact_quick_vip_board(case: QuickVIPSetup) -> QuickVIPOdds:
    """Exact joint physical searchability for up to three Basics.

    The first-turn observed eight-card hand must contain Quick and Sky.
    If two or three Basic targets remain missing, Battle VIP Pass must
    also appear before the first turn ends, with its first-turn-only
    playing window still open. One Quick + VIP can search up to three
    unprized Basics, constrained to the actual remaining Bench slots.
    """
    sizes = case.categories
    n, h = case.total, case.opening
    denominator = choose(n, h) * (n - h)
    masses = [Fraction(0) for _ in range(4)]
    for counts in product(
        *(range(min(size, h)+1) for size in sizes[:7])
    ):
        filler = h - sum(counts)
        if filler < 0 or filler > sizes[-1] or not counts[3]:
            continue  # An ordinary Basic must be the initial Active.
        opener = counts + (filler,)
        ways = 1
        for original, count in zip(sizes, opener):
            ways *= choose(original, count)
        after_opener = tuple(a-b for a, b in zip(sizes, opener))
        for first_type, first_ways in enumerate(after_opener):
            if not first_ways:
                continue
            seen = tuple(
                count + int(index == first_type)
                for index, count in enumerate(opener)
            )
            if not seen[4] or not seen[5]:
                continue  # Quick Ball and its Sky payment are required.
            missing_g = int(seen[0] == 0)
            missing_o = max(0, 4 - seen[3])
            searches = missing_g + missing_o
            if searches > 3 or (searches >= 2 and not seen[6]):
                continue
            stage_seen = bool(seen[1])
            candy_seen = bool(seen[2])
            if not stage_seen and not candy_seen:
                continue  # A lone second-turn draw cannot find both.
            remainder = list(after_opener)
            remainder[first_type] -= 1
            if searches == 0:
                if stage_seen and candy_seen:
                    continuation = Fraction(1)
                else:
                    missing_index = 2 if stage_seen else 1
                    continuation = Fraction(
                        remainder[missing_index], n-h-1
                    )
            else:
                continuation = prize_conditioned_basic_search(
                    case.prizes, tuple(remainder),
                    need_gothita=missing_g, need_core=missing_o,
                    gothitelle_seen=stage_seen,
                    candy_seen=candy_seen,
                )
            masses[searches] += (
                Fraction(ways * first_ways, denominator)
                * continuation
            )
    legal = Fraction(
        choose(n,h)-choose(n-case.gothita-case.other_basics,h),
        choose(n,h),
    )
    return QuickVIPOdds(*masses, legal)
