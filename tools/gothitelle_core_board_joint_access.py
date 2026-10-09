"""Exact joint turn-one four-core-Basic board and dual-use Gothitelle setup.

At first-turn end the controlled side must contain four ordinary Basics:
one Active and three Bench occupants, plus Gothita on the fourth Bench
slot, under the exogenously supplied Collapsed Stadium geometry.
Only one Quick Ball is allowed, always discarding Sky Field. It can
search Gothita, search the fourth ordinary Basic, or choose no target.
The turn-two Candy/Gothitelle draw and Prize conditioning are exact.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from gothitelle_dual_use_joint_access import (
    DualUseSetup,
    choose,
)


@dataclass(frozen=True)
class CoreBoardOdds:
    already_complete: Fraction
    search_core_basic: Fraction
    search_gothita: Fraction
    legal_opener: Fraction

    @property
    def per_attempt(self) -> Fraction:
        return (
            self.already_complete
            + self.search_core_basic
            + self.search_gothita
        )

    @property
    def conditional_legal_opener(self) -> Fraction:
        return self.per_attempt / self.legal_opener


def _search_and_draw(
    case: DualUseSetup,
    remaining: tuple[int, ...],
    *,
    target_index: int,
    has_gothitelle: bool,
    has_candy: bool,
) -> Fraction:
    """Search one required unprized Basic then draw the missing Stage2/Candy.

    Conditional on the number of target Basics that were Prized, the
    remaining prizes are uniformly distributed among non-target cards.
    """
    unknown = sum(remaining)
    target_count = remaining[target_index]
    if not target_count or (not has_gothitelle and not has_candy):
        return Fraction(0)
    physical_deck = unknown - case.prizes - 1
    if physical_deck <= 0:
        return Fraction(0)
    denominator = choose(unknown, case.prizes)
    result = Fraction(0)
    for lost in range(min(target_count, case.prizes) + 1):
        if lost == target_count:
            continue
        other_lost = case.prizes - lost
        subsets = (
            choose(target_count, lost)
            * choose(unknown - target_count, other_lost)
        )
        if not subsets:
            continue
        if has_gothitelle and has_candy:
            continuation = Fraction(1)
        else:
            missing_index = 2 if has_gothitelle else 1
            continuation = Fraction(
                remaining[missing_index]
                * (unknown - target_count - other_lost),
                (unknown - target_count) * physical_deck,
            )
        result += Fraction(subsets, denominator) * continuation
    return result


def exact_core_board_access(case: DualUseSetup) -> CoreBoardOdds:
    sizes = case.categories
    n = case.total
    opening = case.opening
    denominator = choose(n, opening) * (n - opening)
    complete = core_search = gothita_search = Fraction(0)

    for first_six in product(
        *(range(min(count, opening) + 1) for count in sizes[:6])
    ):
        filler = opening - sum(first_six)
        if filler < 0 or filler > sizes[6]:
            continue
        opener = first_six + (filler,)
        if not opener[3]:
            continue  # An ordinary Basic must occupy the initial Active.
        opener_weight = 1
        for copies, count in zip(sizes, opener):
            opener_weight *= choose(copies, count)
        remaining = tuple(a - b for a, b in zip(sizes, opener))
        for first_type, first_ways in enumerate(remaining):
            if not first_ways:
                continue
            seen = tuple(
                count + int(i == first_type)
                for i, count in enumerate(opener)
            )
            if not seen[4] or not seen[5]:
                continue  # Q and Sky must arrive by turn one's end.
            after_first = list(remaining)
            after_first[first_type] -= 1
            weight = Fraction(
                opener_weight * first_ways, denominator
            )
            t_seen, c_seen = bool(seen[1]), bool(seen[2])

            if seen[0] and seen[3] >= 4:
                # Four ordinary Basics and a Gothita are already observed.
                # The paid restricted Quick search can select zero cards.
                if t_seen and c_seen:
                    chance = Fraction(1)
                elif t_seen:
                    chance = Fraction(after_first[2], n - opening - 1)
                elif c_seen:
                    chance = Fraction(after_first[1], n - opening - 1)
                else:
                    chance = Fraction(0)
                complete += weight * chance
            elif seen[0] and seen[3] == 3:
                # Gothita is natural; Quick searches the fourth core Basic.
                core_search += weight * _search_and_draw(
                    case, tuple(after_first), target_index=3,
                    has_gothitelle=t_seen, has_candy=c_seen,
                )
            elif not seen[0] and seen[3] >= 4:
                # Four cores are natural; Quick searches the Gothita.
                gothita_search += weight * _search_and_draw(
                    case, tuple(after_first), target_index=0,
                    has_gothitelle=t_seen, has_candy=c_seen,
                )

    legal = Fraction(
        choose(n, opening)
        - choose(n - case.gothita - case.other_basics, opening),
        choose(n, opening),
    )
    return CoreBoardOdds(complete, core_search, gothita_search, legal)
