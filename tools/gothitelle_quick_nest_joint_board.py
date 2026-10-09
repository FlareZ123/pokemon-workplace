"""One Sky-paying Quick Ball plus an optional no-discard Nest Ball.

Exact first-seven, six-Prize, first-turn draw, typed one/two Basic searches
and turn-two evolution access for a four-core Basic Bench. The opponent
Stadium/lock state is supplied outside this card-access model.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from gothitelle_dual_use_joint_access import DualUseSetup, choose
from gothitelle_two_quick_joint_board import prize_conditioned_basic_search


@dataclass(frozen=True)
class QuickNestSetup:
    total: int = 60
    opening: int = 7
    prizes: int = 6
    gothita: int = 3
    gothitelle: int = 2
    rare_candy: int = 4
    other_basics: int = 8
    quick_ball: int = 4
    sky_field: int = 2
    nest_ball: int = 4

    @property
    def categories(self) -> tuple[int, ...]:
        head = (
            self.gothita, self.gothitelle, self.rare_candy,
            self.other_basics, self.quick_ball, self.sky_field,
            self.nest_ball,
        )
        return head + (self.total - sum(head),)

    def __post_init__(self) -> None:
        if (
            min(self.categories) < 0 or self.opening < 1
            or self.prizes < 0
            or self.total - self.opening - self.prizes - 3 <= 0
            or self.other_basics == 0
        ):
            raise ValueError("invalid Quick/Nest category partition")

    def one_quick_projection(self) -> DualUseSetup:
        return DualUseSetup(
            total=self.total, opening=self.opening, prizes=self.prizes,
            gothita=self.gothita, gothitelle=self.gothitelle,
            rare_candy=self.rare_candy, other_basics=self.other_basics,
            quick_ball=self.quick_ball, sky_field=self.sky_field,
        )


@dataclass(frozen=True)
class QuickNestOdds:
    complete_without_search: Fraction
    quick_search_core: Fraction
    quick_search_gothita: Fraction
    quick_nest_two_cores: Fraction
    quick_nest_mixed: Fraction
    legal_opener: Fraction

    @property
    def per_attempt(self) -> Fraction:
        return sum((
            self.complete_without_search, self.quick_search_core,
            self.quick_search_gothita, self.quick_nest_two_cores,
            self.quick_nest_mixed,
        ), Fraction(0))

    @property
    def nest_increment(self) -> Fraction:
        return self.quick_nest_two_cores + self.quick_nest_mixed

    @property
    def conditional_legal_opener(self) -> Fraction:
        return self.per_attempt / self.legal_opener


def exact_quick_nest_board(case: QuickNestSetup) -> QuickNestOdds:
    sizes = case.categories
    n, h = case.total, case.opening
    denominator = choose(n, h) * (n - h)
    masses = [Fraction(0) for _ in range(5)]
    for first_seven in product(
        *(range(min(value, h) + 1) for value in sizes[:7])
    ):
        filler = h - sum(first_seven)
        if filler < 0 or filler > sizes[-1] or not first_seven[3]:
            continue  # Initial Active must be an ordinary Basic.
        opener = first_seven + (filler,)
        ways = 1
        for size, taken in zip(sizes, opener):
            ways *= choose(size, taken)
        remaining_opening = tuple(
            size - taken for size, taken in zip(sizes, opener)
        )
        for first_type, first_ways in enumerate(remaining_opening):
            if not first_ways:
                continue
            seen = tuple(
                count + int(i == first_type)
                for i, count in enumerate(opener)
            )
            if not seen[4] or not seen[5]:
                continue  # First-turn Quick and Sky Field payment.
            remaining = list(remaining_opening)
            remaining[first_type] -= 1
            need_g = int(seen[0] == 0)
            need_o = max(0, 4 - seen[3])
            searches = need_g + need_o
            if searches > 2 or (searches == 2 and not seen[6]):
                continue  # Second search requires Nest Ball.
            t_seen, c_seen = bool(seen[1]), bool(seen[2])
            if not t_seen and not c_seen:
                continue
            weight = Fraction(ways * first_ways, denominator)
            if searches == 0:
                if t_seen and c_seen:
                    continuation = Fraction(1)
                else:
                    missing = 2 if t_seen else 1
                    continuation = Fraction(
                        remaining[missing], n - h - 1
                    )
                branch = 0
            else:
                continuation = prize_conditioned_basic_search(
                    case.prizes, tuple(remaining),
                    need_gothita=need_g, need_core=need_o,
                    gothitelle_seen=t_seen, candy_seen=c_seen,
                )
                branch = (
                    1 if searches == 1 and need_o
                    else 2 if searches == 1
                    else 3 if need_o == 2
                    else 4
                )
            masses[branch] += weight * continuation

    legal = Fraction(
        choose(n, h) - choose(n - case.gothita - case.other_basics, h),
        choose(n, h),
    )
    return QuickNestOdds(*masses, legal)
