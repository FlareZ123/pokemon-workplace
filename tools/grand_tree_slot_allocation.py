"""Balanced evolution copy allocation maximizes joint deck-search access.

The objective here is exact initial-zone availability only: a designated
Basic is in the opening hand; a Stage 1 and Stage 2 must both remain in
the searchable deck at setup. This is not a whole-game deck optimizer.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from tools.grand_tree_initial_zone_probability import probability_full


@dataclass(frozen=True)
class Allocation:
    stage1: int
    stage2: int
    both_deck: Fraction


def missing_probability(
    copies: int,
    *, n: int = 59,
    inaccessible: int = 12,
) -> Fraction:
    """Probability all copies occupy inaccessible hand/Prize positions."""

    if not 0 <= inaccessible <= n or not 0 <= copies <= n:
        raise ValueError("invalid finite population parameters")
    if copies > inaccessible:
        return Fraction(0)
    return Fraction(comb(inaccessible, copies), comb(n, copies))


def verify_diminishing_rescue(
    *, n: int = 59, inaccessible: int = 12,
) -> bool:
    """Exact convexity certificate for the no-deck-copy probability q(k).

    q(k)-q(k+1) is nonnegative and monotonically nonincreasing.
    """
    values = tuple(
        missing_probability(k, n=n, inaccessible=inaccessible)
        for k in range(n + 1)
    )
    rescue = tuple(values[k] - values[k + 1] for k in range(n))
    return all(
        rescue[k] >= rescue[k + 1] >= 0
        for k in range(n - 1)
    )


def allocation_frontier(
    total_copies: int,
    *,
    max_copies_per_stage: int = 4,
    n: int = 59,
    hand: int = 6,
    prizes: int = 6,
) -> tuple[Allocation, ...]:
    """All legal-positive split choices, sorted by joint accessibility."""

    if total_copies < 2 or max_copies_per_stage < 1:
        raise ValueError("need at least one copy of each evolution stage")
    rows = tuple(
        Allocation(
            stage1=stage1,
            stage2=total_copies - stage1,
            both_deck=probability_full(
                n=n, hand=hand, prizes=prizes,
                first=stage1, second=total_copies - stage1,
            ),
        )
        for stage1 in range(1, total_copies)
        if stage1 <= max_copies_per_stage
        and total_copies - stage1 <= max_copies_per_stage
        and total_copies <= n
    )
    return tuple(sorted(rows, key=lambda row: (-row.both_deck, row.stage1)))


def optimal_splits(
    total_copies: int,
    *,
    max_copies_per_stage: int = 4,
    n: int = 59,
    hand: int = 6,
    prizes: int = 6,
) -> tuple[Allocation, ...]:
    rows = allocation_frontier(
        total_copies,
        max_copies_per_stage=max_copies_per_stage,
        n=n, hand=hand, prizes=prizes,
    )
    if not rows:
        return ()
    best = rows[0].both_deck
    return tuple(row for row in rows if row.both_deck == best)
