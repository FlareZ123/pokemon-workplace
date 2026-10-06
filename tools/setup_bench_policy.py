from __future__ import annotations

from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def accepted_basic_count_distribution(
    deck_size: int,
    basic_count: int,
    *,
    hand_size: int = 7,
) -> dict[int, float]:
    """Return P(K=k | opening contains at least one ordinary legal Basic)."""
    if deck_size <= 0 or not 0 <= basic_count <= deck_size:
        raise ValueError("invalid deck or Basic count")
    if not 0 <= hand_size <= deck_size:
        raise ValueError("invalid hand size")
    denominator = _choose(deck_size, hand_size) - _choose(deck_size - basic_count, hand_size)
    if denominator == 0:
        raise ValueError("opening can never contain a Basic")

    result = {}
    for k in range(1, min(hand_size, basic_count) + 1):
        ways = _choose(basic_count, k) * _choose(deck_size - basic_count, hand_size - k)
        if ways:
            result[k] = ways / denominator
    return result


def setup_bench_occupancy(
    basics_in_opening: int,
    *,
    reserve_slots: int = 0,
    bench_limit: int = 5,
) -> int:
    """Bench as many extra opening Basics as possible while reserving slots."""
    if basics_in_opening < 1:
        raise ValueError("an accepted ordinary opening needs at least one Basic")
    if not 0 <= reserve_slots <= bench_limit:
        raise ValueError("reserve_slots must fit within the Bench limit")
    available_for_setup = bench_limit - reserve_slots
    return min(basics_in_opening - 1, available_for_setup)


def connector_block_probability(
    deck_size: int,
    basic_count: int,
    required_slots: int,
    *,
    hand_size: int = 7,
    reserve_slots: int = 0,
    bench_limit: int = 5,
) -> float:
    """Exact probability setup occupancy blocks a route needing `required_slots`."""
    if not 0 <= required_slots <= bench_limit:
        raise ValueError("required_slots must fit within the Bench limit")
    distribution = accepted_basic_count_distribution(
        deck_size,
        basic_count,
        hand_size=hand_size,
    )
    return sum(
        mass
        for basics, mass in distribution.items()
        if setup_bench_occupancy(
            basics,
            reserve_slots=reserve_slots,
            bench_limit=bench_limit,
        )
        + required_slots
        > bench_limit
    )


def sensitivity_table(
    basic_counts: tuple[int, ...] = (8, 12, 16, 20, 24, 28, 32),
) -> list[dict[str, float | int]]:
    rows = []
    for basics in basic_counts:
        rows.append(
            {
                "basic_count": basics,
                "one_slot_blocked_if_bench_all": connector_block_probability(60, basics, 1),
                "two_slots_blocked_if_bench_all": connector_block_probability(60, basics, 2),
                "three_slots_blocked_if_bench_all": connector_block_probability(60, basics, 3),
                "one_slot_blocked_if_reserve_one": connector_block_probability(
                    60, basics, 1, reserve_slots=1
                ),
                "two_slots_blocked_if_reserve_two": connector_block_probability(
                    60, basics, 2, reserve_slots=2
                ),
            }
        )
    return rows


if __name__ == "__main__":
    for row in sensitivity_table():
        print(row)
