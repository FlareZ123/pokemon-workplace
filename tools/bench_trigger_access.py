from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class BenchTriggerAccess:
    valid_start_probability: Fraction
    naive_access_given_valid: Fraction
    zone_aware_access_given_valid: Fraction
    role_aware_access_given_valid: Fraction
    exact_access_given_valid: Fraction
    direct_to_bench_overstatement_given_valid: Fraction
    active_role_overstatement_given_valid: Fraction
    bench_capacity_overstatement_given_valid: Fraction
    combined_overstatement_given_valid: Fraction


def _vectors(capacities: tuple[int, ...], total: int) -> Iterator[tuple[int, ...]]:
    current = [0] * len(capacities)

    def visit(index: int, remaining: int) -> Iterator[tuple[int, ...]]:
        if index == len(capacities) - 1:
            if 0 <= remaining <= capacities[index]:
                current[index] = remaining
                yield tuple(current)
            return
        for value in range(min(capacities[index], remaining) + 1):
            current[index] = value
            yield from visit(index + 1, remaining - value)

    if 0 <= total <= sum(capacities):
        yield from visit(0, total)


def _ways(capacities: tuple[int, ...], counts: tuple[int, ...]) -> int:
    result = 1
    for capacity, count in zip(capacities, counts, strict=True):
        result *= comb(capacity, count)
    return result


def analyze_bench_trigger_access(
    *,
    deck_size: int = 60,
    opening_size: int = 7,
    prize_count: int = 6,
    extra_random_draws: int = 1,
    trigger_basics: int,
    other_basics: int,
    hand_connectors: int = 0,
    direct_bench_connectors: int = 0,
    available_bench_slots: int = 1,
) -> BenchTriggerAccess:
    """Exact setup-conditioned access to one hand-to-Bench trigger activation.

    Hand connectors are idealized deterministic non-Supporter effects that move a
    trigger Basic from deck to hand. Direct-bench connectors move it from deck
    directly to the Bench, so they do not satisfy a hand-to-Bench trigger.
    """

    counts = (trigger_basics, other_basics, hand_connectors, direct_bench_connectors)
    if any(value < 0 for value in counts):
        raise ValueError("card counts must be non-negative")
    if sum(counts) > deck_size:
        raise ValueError("modeled card counts cannot exceed deck_size")
    if opening_size <= 0 or opening_size > deck_size:
        raise ValueError("opening_size must be in 1..deck_size")
    if prize_count < 0 or prize_count > deck_size - opening_size:
        raise ValueError("invalid prize_count")
    if extra_random_draws < 0 or extra_random_draws > deck_size - opening_size - prize_count:
        raise ValueError("invalid extra_random_draws")
    if available_bench_slots < 0 or available_bench_slots > 5:
        raise ValueError("available_bench_slots must be in 0..5")

    filler = deck_size - sum(counts)
    capacities = (*counts, filler)
    opening_denominator = comb(deck_size, opening_size)

    valid_opening_ways = 0
    total_sequence_ways = 0
    naive_ways = 0
    zone_aware_ways = 0
    role_aware_ways = 0
    exact_ways = 0

    for opening in _vectors(capacities, opening_size):
        opening_ways = _ways(capacities, opening)
        open_trigger, open_other, open_hand_connector, open_direct_connector, _ = opening
        if open_trigger + open_other == 0:
            continue
        valid_opening_ways += opening_ways

        remaining_after_open = tuple(
            capacity - used
            for capacity, used in zip(capacities, opening, strict=True)
        )
        retained_open_trigger = open_trigger - int(open_other == 0 and open_trigger > 0)

        for prizes in _vectors(remaining_after_open, prize_count):
            prize_ways = _ways(remaining_after_open, prizes)
            remaining_after_prizes = tuple(
                capacity - used
                for capacity, used in zip(remaining_after_open, prizes, strict=True)
            )

            for draws in _vectors(remaining_after_prizes, extra_random_draws):
                draw_ways = _ways(remaining_after_prizes, draws)
                weight = opening_ways * prize_ways * draw_ways
                total_sequence_ways += weight

                draw_trigger, _, draw_hand_connector, draw_direct_connector, _ = draws
                searchable_trigger = trigger_basics - open_trigger - prizes[0] - draw_trigger

                role_naive_trigger_in_hand = open_trigger + draw_trigger
                role_aware_trigger_in_hand = retained_open_trigger + draw_trigger
                hand_connector_in_hand = open_hand_connector + draw_hand_connector
                any_connector_in_hand = (
                    hand_connector_in_hand
                    + open_direct_connector
                    + draw_direct_connector
                )

                naive = (
                    role_naive_trigger_in_hand > 0
                    or (any_connector_in_hand > 0 and searchable_trigger > 0)
                )
                zone_aware = (
                    role_naive_trigger_in_hand > 0
                    or (hand_connector_in_hand > 0 and searchable_trigger > 0)
                )
                role_aware = (
                    role_aware_trigger_in_hand > 0
                    or (hand_connector_in_hand > 0 and searchable_trigger > 0)
                )
                exact = role_aware and available_bench_slots > 0

                naive_ways += weight * int(naive)
                zone_aware_ways += weight * int(zone_aware)
                role_aware_ways += weight * int(role_aware)
                exact_ways += weight * int(exact)

    if valid_opening_ways == 0:
        zero = Fraction(0, 1)
        return BenchTriggerAccess(zero, zero, zero, zero, zero, zero, zero, zero, zero)

    valid_probability = Fraction(valid_opening_ways, opening_denominator)
    naive = Fraction(naive_ways, total_sequence_ways)
    zone_aware = Fraction(zone_aware_ways, total_sequence_ways)
    role_aware = Fraction(role_aware_ways, total_sequence_ways)
    exact = Fraction(exact_ways, total_sequence_ways)

    return BenchTriggerAccess(
        valid_start_probability=valid_probability,
        naive_access_given_valid=naive,
        zone_aware_access_given_valid=zone_aware,
        role_aware_access_given_valid=role_aware,
        exact_access_given_valid=exact,
        direct_to_bench_overstatement_given_valid=naive - zone_aware,
        active_role_overstatement_given_valid=zone_aware - role_aware,
        bench_capacity_overstatement_given_valid=role_aware - exact,
        combined_overstatement_given_valid=naive - exact,
    )
