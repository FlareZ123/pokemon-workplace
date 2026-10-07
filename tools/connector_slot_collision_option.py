"""Finite-horizon option value with typed connector output slots.

Each connector output slot can search at most one target channel. A target may
be eligible for one or more slot labels. One connector use chooses any injective
assignment from searched target channels to physical output slots.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from typing import Literal

Policy = Literal["optimal", "eager"]


@dataclass(frozen=True)
class SlotOptionResult:
    optimal_success: float
    eager_success: float
    immediate_matching_size: int

    @property
    def waiting_gain(self) -> float:
        return self.optimal_success - self.eager_success


def _matchable(
    subset: tuple[int, ...],
    target_slots: tuple[tuple[str, ...], ...],
    connector_slots: tuple[str, ...],
) -> bool:
    """Return whether targets in subset can be injected into physical slots."""
    if not subset:
        return True
    if len(subset) > len(connector_slots):
        return False

    order = sorted(subset, key=lambda i: len(target_slots[i]))

    def visit(position: int, used: int) -> bool:
        if position == len(order):
            return True
        target = order[position]
        eligible = set(target_slots[target])
        for slot_index, label in enumerate(connector_slots):
            if used & (1 << slot_index) or label not in eligible:
                continue
            if visit(position + 1, used | (1 << slot_index)):
                return True
        return False

    return visit(0, 0)


def _matchable_subsets(
    searchable: tuple[int, ...],
    target_slots: tuple[tuple[str, ...], ...],
    connector_slots: tuple[str, ...],
) -> tuple[tuple[int, ...], ...]:
    out: list[tuple[int, ...]] = []
    for size in range(1, min(len(searchable), len(connector_slots)) + 1):
        for subset in combinations(searchable, size):
            if _matchable(subset, target_slots, connector_slots):
                out.append(subset)
    return tuple(out)


def slot_collision_option_value(
    *,
    target_counts: tuple[int, ...],
    target_slots: tuple[tuple[str, ...], ...],
    connector_slots: tuple[str, ...],
    filler_count: int,
    draws_remaining: int,
) -> SlotOptionResult:
    """Return optimal and eager exact success for one typed connector use."""
    if not target_counts:
        raise ValueError("at least one target channel is required")
    if len(target_counts) != len(target_slots):
        raise ValueError("target_counts and target_slots must have the same length")
    if min(target_counts) < 0 or filler_count < 0 or draws_remaining < 0:
        raise ValueError("counts and draws must be non-negative")
    if not connector_slots:
        raise ValueError("at least one connector output slot is required")
    if any(not slots for slots in target_slots):
        raise ValueError("every target must be eligible for at least one slot")

    all_targets = tuple(range(len(target_counts)))
    immediate_subsets = _matchable_subsets(all_targets, target_slots, connector_slots)
    immediate_matching_size = max((len(s) for s in immediate_subsets), default=0)

    def solve(policy: Policy) -> float:
        @lru_cache(maxsize=None)
        def value(
            counts: tuple[int, ...],
            secured: tuple[bool, ...],
            filler: int,
            connector_available: bool,
            draws: int,
        ) -> float:
            if all(secured):
                return 1.0

            use_values: list[float] = []
            if connector_available:
                searchable = tuple(
                    i for i, (count, done) in enumerate(zip(counts, secured))
                    if count > 0 and not done
                )
                for subset in _matchable_subsets(
                    searchable, target_slots, connector_slots
                ):
                    next_counts = list(counts)
                    next_secured = list(secured)
                    for index in subset:
                        next_counts[index] -= 1
                        next_secured[index] = True
                    use_values.append(
                        value(
                            tuple(next_counts),
                            tuple(next_secured),
                            filler,
                            False,
                            draws,
                        )
                    )

            wait_value = 0.0
            deck_size = sum(counts) + filler
            if draws > 0 and deck_size > 0:
                for index, count in enumerate(counts):
                    if count == 0:
                        continue
                    next_counts = list(counts)
                    next_counts[index] -= 1
                    next_secured = list(secured)
                    next_secured[index] = True
                    wait_value += count / deck_size * value(
                        tuple(next_counts),
                        tuple(next_secured),
                        filler,
                        connector_available,
                        draws - 1,
                    )
                if filler:
                    wait_value += filler / deck_size * value(
                        counts,
                        secured,
                        filler - 1,
                        connector_available,
                        draws - 1,
                    )

            if policy == "eager" and use_values:
                return max(use_values)
            return max([wait_value, *use_values], default=0.0)

        return value(
            target_counts,
            (False,) * len(target_counts),
            filler_count,
            True,
            draws_remaining,
        )

    return SlotOptionResult(
        optimal_success=solve("optimal"),
        eager_success=solve("eager"),
        immediate_matching_size=immediate_matching_size,
    )
