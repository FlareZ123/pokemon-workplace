from __future__ import annotations

from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def payload_outcome_distribution(
    deck_size: int,
    other_starters: int,
    *,
    hand_size: int = 7,
    bench_limit: int = 5,
    reserve_slots: int = 0,
    payload_slots: int = 2,
) -> dict[str, float]:
    """Slot outcomes conditional on one trigger Basic being preserved in hand.

    The opening contains the trigger Basic plus at least one ordinary other
    starter. One other starter becomes Active. The setup policy Benches as many
    remaining other starters as possible while reserving `reserve_slots`.
    During the turn the trigger Basic must first enter the Bench, then its effect
    may put up to `payload_slots` additional Pokémon onto the Bench.
    """
    if deck_size <= 0 or not 0 <= other_starters < deck_size:
        raise ValueError("invalid deck or other-starter count")
    if not 0 <= reserve_slots <= bench_limit:
        raise ValueError("reserve_slots must fit the Bench")
    if not 0 <= payload_slots <= bench_limit:
        raise ValueError("payload_slots must fit the Bench")
    if hand_size < 2:
        raise ValueError("preservation requires the trigger and another starter")

    remaining_other_cards = deck_size - 1 - other_starters
    denominator = 0
    masses: dict[str, int] = {}

    for other_in_hand in range(1, min(other_starters, hand_size - 1) + 1):
        ways = _choose(other_starters, other_in_hand) * _choose(
            remaining_other_cards,
            hand_size - 1 - other_in_hand,
        )
        if ways == 0:
            continue
        denominator += ways

        setup_occupancy = min(
            other_in_hand - 1,
            bench_limit - reserve_slots,
        )
        if setup_occupancy >= bench_limit:
            key = "cannot_play_trigger"
        else:
            free_after_entry = bench_limit - (setup_occupancy + 1)
            payload_placed = min(payload_slots, free_after_entry)
            key = f"payload_{payload_placed}"
        masses[key] = masses.get(key, 0) + ways

    if denominator == 0:
        raise ValueError("conditioning event has zero probability")
    return {key: value / denominator for key, value in sorted(masses.items())}


def full_payload_probability(
    deck_size: int,
    other_starters: int,
    *,
    hand_size: int = 7,
    bench_limit: int = 5,
    reserve_slots: int = 0,
    payload_slots: int = 2,
) -> float:
    distribution = payload_outcome_distribution(
        deck_size,
        other_starters,
        hand_size=hand_size,
        bench_limit=bench_limit,
        reserve_slots=reserve_slots,
        payload_slots=payload_slots,
    )
    return distribution.get(f"payload_{payload_slots}", 0.0)


def radiant_eternatus_rows() -> list[dict[str, float | int]]:
    rows = []
    for total_starters in (8, 12, 16, 20, 24, 28, 32):
        distribution = payload_outcome_distribution(60, total_starters - 1)
        rows.append(
            {
                "total_basic_starters_including_radiant_eternatus": total_starters,
                "full_two_vmax_slot_probability_bench_all": distribution.get("payload_2", 0.0),
                "one_vmax_slot_probability_bench_all": distribution.get("payload_1", 0.0),
                "zero_vmax_slot_probability_bench_all": distribution.get("payload_0", 0.0),
                "cannot_play_radiant_eternatus_bench_all": distribution.get("cannot_play_trigger", 0.0),
                "full_two_vmax_slot_probability_reserve_three": full_payload_probability(
                    60,
                    total_starters - 1,
                    reserve_slots=3,
                ),
            }
        )
    return rows


if __name__ == "__main__":
    for row in radiant_eternatus_rows():
        print(row)
