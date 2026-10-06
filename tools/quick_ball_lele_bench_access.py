from __future__ import annotations

from itertools import product
from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def setup_bench_count(other_starters_in_opening: int, *, reserve_slots: int) -> int:
    if other_starters_in_opening < 1:
        raise ValueError("a non-Lele starter is required for this setup branch")
    if not 0 <= reserve_slots <= 5:
        raise ValueError("reserve_slots must be between 0 and 5")
    return min(other_starters_in_opening - 1, 5 - reserve_slots)


def opening_gladion_access_with_bench_policy(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    opening_hand_size: int = 7,
    setup_reserve_slots: int = 0,
    allow_spare_quick_ball_discard: bool = False,
) -> float:
    """Exact current-window Gladion access with setup Bench occupancy.

    Exactly one Tapu Lele-GX-like Basic is modeled. If it is in the opening,
    the connector preserves it in hand only when another starter is available.
    Other opening starters are Benched as far as the reserve-slot policy allows.
    """
    support_basic = 1
    filler_nonstarter = (
        deck_size
        - support_basic
        - other_starters
        - critical_nonstarter
        - rescue_nonstarter
        - quick_ball_copies
        - disposable_nonstarter
    )
    if min(
        other_starters,
        critical_nonstarter,
        rescue_nonstarter,
        quick_ball_copies,
        disposable_nonstarter,
        filler_nonstarter,
    ) < 0:
        raise ValueError("modeled counts must be non-negative and fit in the deck")
    if not 0 <= setup_reserve_slots <= 5:
        raise ValueError("setup_reserve_slots must be between 0 and 5")

    sizes = (
        critical_nonstarter,
        rescue_nonstarter,
        support_basic,
        quick_ball_copies,
        disposable_nonstarter,
        other_starters,
        filler_nonstarter,
    )
    total_starters = support_basic + other_starters
    opening_denominator = _choose(deck_size, opening_hand_size)
    opening_acceptance = 1.0 - _choose(
        deck_size - total_starters, opening_hand_size
    ) / opening_denominator
    if opening_acceptance == 0.0:
        raise ValueError("valid opening has zero probability")

    access_mass = 0.0
    critical_mass = 0.0

    for opening in product(*[range(min(size, opening_hand_size) + 1) for size in sizes]):
        if sum(opening) != opening_hand_size:
            continue
        if opening[2] + opening[5] == 0:
            continue

        opening_ways = 1
        for size, count in zip(sizes, opening):
            opening_ways *= _choose(size, count)
        if opening_ways == 0:
            continue
        opening_mass = opening_ways / opening_denominator / opening_acceptance
        remaining = tuple(size - count for size, count in zip(sizes, opening))
        prize_denominator = _choose(deck_size - opening_hand_size, prize_count)

        for prizes in product(*[range(min(size, prize_count) + 1) for size in remaining]):
            if sum(prizes) != prize_count or prizes[0] == 0:
                continue
            prize_ways = 1
            for size, count in zip(remaining, prizes):
                prize_ways *= _choose(size, count)
            if prize_ways == 0:
                continue
            mass = opening_mass * prize_ways / prize_denominator
            critical_mass += mass

            rescue_in_hand = opening[1]
            rescue_in_deck = rescue_nonstarter - opening[1] - prizes[1]
            support_in_hand = opening[2] == 1
            support_in_deck = support_basic - opening[2] - prizes[2]

            support_preserved = support_in_hand and opening[5] >= 1
            bench_space_for_support = False
            if opening[5] >= 1:
                occupied = setup_bench_count(
                    opening[5], reserve_slots=setup_reserve_slots
                )
                bench_space_for_support = occupied < 5

            discardable = opening[4]
            if allow_spare_quick_ball_discard:
                discardable += max(0, opening[3] - 1)

            direct_rescue = rescue_in_hand >= 1
            preserved_support_line = (
                support_preserved
                and bench_space_for_support
                and rescue_in_deck >= 1
            )
            quick_ball_line = (
                opening[3] >= 1
                and discardable >= 1
                and support_in_deck >= 1
                and bench_space_for_support
                and rescue_in_deck >= 1
            )

            if direct_rescue or preserved_support_line or quick_ball_line:
                access_mass += mass

    return 0.0 if critical_mass == 0.0 else access_mass / critical_mass


def sensitivity_rows() -> list[dict[str, float | int]]:
    rows = []
    for total_starters in (8, 12, 16, 20, 24, 28):
        kwargs = dict(
            deck_size=60,
            prize_count=6,
            other_starters=total_starters - 1,
            critical_nonstarter=4,
            rescue_nonstarter=2,
            quick_ball_copies=4,
            disposable_nonstarter=12,
        )
        bench_all = opening_gladion_access_with_bench_policy(
            **kwargs, setup_reserve_slots=0
        )
        reserve_one = opening_gladion_access_with_bench_policy(
            **kwargs, setup_reserve_slots=1
        )
        rows.append(
            {
                "total_starters": total_starters,
                "bench_all_access": bench_all,
                "reserve_one_access": reserve_one,
                "absolute_recovery": reserve_one - bench_all,
            }
        )
    return rows


if __name__ == "__main__":
    for row in sensitivity_rows():
        print(row)
