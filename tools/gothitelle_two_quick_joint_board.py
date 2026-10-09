"""Joint four-core turn-one Gothitelle probability with up to two Quick Balls.

One mandatory first-turn Quick Ball discards Sky Field. If a second
search is required, another accessible Quick Ball pays one separately
approved disposable card. Quick Ball targets only Basic Pokémon.
Prize uncertainty and the delayed Stage2/Rare Candy draw remain joint.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from gothitelle_dual_use_joint_access import DualUseSetup, choose


@dataclass(frozen=True)
class TwoQuickSetup:
    total: int = 60
    opening: int = 7
    prizes: int = 6
    gothita: int = 3
    gothitelle: int = 2
    rare_candy: int = 4
    other_basics: int = 8
    quick_ball: int = 4
    sky_field: int = 2
    approved_discard: int = 12

    @property
    def categories(self) -> tuple[int, ...]:
        head = (
            self.gothita, self.gothitelle, self.rare_candy,
            self.other_basics, self.quick_ball, self.sky_field,
            self.approved_discard,
        )
        return head + (self.total - sum(head),)

    def __post_init__(self) -> None:
        if (
            min(self.categories) < 0 or self.opening < 1
            or self.prizes < 0
            or self.total - self.opening - self.prizes - 3 <= 0
            or self.other_basics == 0
        ):
            raise ValueError("invalid two-Quick partition or turn window")

    def one_quick_projection(self) -> DualUseSetup:
        """Forget discard-fodder class without changing any card counts."""
        return DualUseSetup(
            total=self.total, opening=self.opening, prizes=self.prizes,
            gothita=self.gothita, gothitelle=self.gothitelle,
            rare_candy=self.rare_candy, other_basics=self.other_basics,
            quick_ball=self.quick_ball, sky_field=self.sky_field,
        )


@dataclass(frozen=True)
class TwoQuickOdds:
    complete_without_search: Fraction
    single_search_core: Fraction
    single_search_gothita: Fraction
    double_search_two_cores: Fraction
    double_search_mixed: Fraction
    legal_opener: Fraction

    @property
    def per_attempt(self) -> Fraction:
        return sum((
            self.complete_without_search,
            self.single_search_core,
            self.single_search_gothita,
            self.double_search_two_cores,
            self.double_search_mixed,
        ), Fraction(0))

    @property
    def increment_from_second_search(self) -> Fraction:
        return self.double_search_two_cores + self.double_search_mixed

    @property
    def conditional_legal_opener(self) -> Fraction:
        return self.per_attempt / self.legal_opener


def prize_conditioned_basic_search(
    prizes: int,
    remaining: tuple[int, ...],
    *,
    need_gothita: int,
    need_core: int,
    gothitelle_seen: bool,
    candy_seen: bool,
) -> Fraction:
    """Joint hypergeometric Prize distribution for two Basic categories."""
    total_unknown = sum(remaining)
    g, o = remaining[0], remaining[3]
    other = total_unknown - g - o
    searches = need_gothita + need_core
    if g < need_gothita or o < need_core:
        return Fraction(0)
    if not gothitelle_seen and not candy_seen:
        return Fraction(0)
    post_search_deck = total_unknown - prizes - searches
    if post_search_deck <= 0:
        return Fraction(0)
    probability = Fraction(0)
    denominator = choose(total_unknown, prizes)
    for g_prized in range(min(g, prizes) + 1):
        for o_prized in range(min(o, prizes - g_prized) + 1):
            if g - g_prized < need_gothita or o - o_prized < need_core:
                continue
            other_prized = prizes - g_prized - o_prized
            ways = (
                choose(g, g_prized)
                * choose(o, o_prized)
                * choose(other, other_prized)
            )
            if not ways:
                continue
            if gothitelle_seen and candy_seen:
                continuation = Fraction(1)
            elif other == 0:
                continuation = Fraction(0)
            else:
                missing = 2 if gothitelle_seen else 1
                continuation = Fraction(
                    remaining[missing] * (other - other_prized),
                    other * post_search_deck,
                )
            probability += Fraction(ways, denominator) * continuation
    return probability


def exact_two_quick_board(case: TwoQuickSetup) -> TwoQuickOdds:
    """Exact first seven, six Prizes, T1 observed eighth, T2 top draw."""
    sizes = case.categories
    n, opening = case.total, case.opening
    denominator = choose(n, opening) * (n - opening)
    masses = [Fraction(0) for _ in range(5)]
    for seven_categories in product(
        *(range(min(count, opening) + 1) for count in sizes[:7])
    ):
        filler = opening - sum(seven_categories)
        if filler < 0 or filler > sizes[-1] or not seven_categories[3]:
            continue  # Non-Gothitelle Active must start as an ordinary Basic.
        observed_opening = seven_categories + (filler,)
        weight_opening = 1
        for size, count in zip(sizes, observed_opening):
            weight_opening *= choose(size, count)
        remaining_opening = tuple(
            count - seen for count, seen in zip(sizes, observed_opening)
        )
        for first_type, count_first in enumerate(remaining_opening):
            if not count_first:
                continue
            seen = tuple(
                count + int(index == first_type)
                for index, count in enumerate(observed_opening)
            )
            if not seen[4] or not seen[5]:
                continue  # Must have one Quick and the Sky payment at T1.
            remaining = list(remaining_opening)
            remaining[first_type] -= 1
            need_g = int(seen[0] == 0)
            need_o = max(0, 4 - seen[3])
            searches = need_g + need_o
            if searches > 2:
                continue
            if searches == 2 and (seen[4] < 2 or not seen[6]):
                continue  # Second paid Quick requires another copy + fodder.
            t_seen, c_seen = bool(seen[1]), bool(seen[2])
            if not t_seen and not c_seen:
                continue  # One T2 draw cannot acquire both evolution cards.
            weight = Fraction(
                weight_opening * count_first, denominator
            )
            if searches == 0:
                if t_seen and c_seen:
                    chance = Fraction(1)
                else:
                    missing = 2 if t_seen else 1
                    chance = Fraction(
                        remaining[missing], n - opening - 1
                    )
                branch = 0
            else:
                chance = prize_conditioned_basic_search(
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
            masses[branch] += weight * chance

    legal = Fraction(
        choose(n, opening)
        - choose(n - case.gothita - case.other_basics, opening),
        choose(n, opening),
    )
    return TwoQuickOdds(*masses, legal)
