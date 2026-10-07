"""Finite-horizon target deadlines for one bounded-capacity connector.

A deadline is the number of natural draws that may still occur before a target
must be secured. A target with deadline zero must be secured at the current
action point before the policy may take another natural draw.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations


@dataclass(frozen=True)
class DeadlineState:
    target_counts: tuple[int, ...]
    secured: tuple[bool, ...]
    deadlines: tuple[int, ...]
    filler_count: int
    connector_available: bool
    draws_remaining: int


def capacity_deadline_value(
    *,
    target_counts: tuple[int, ...],
    deadlines: tuple[int, ...],
    filler_count: int,
    capacity: int,
    draws_remaining: int,
) -> float:
    """Return the exact optimal probability of securing every target in time."""

    if not target_counts:
        raise ValueError("at least one target channel is required")
    if len(target_counts) != len(deadlines):
        raise ValueError("target_counts and deadlines must have the same length")
    if min(target_counts) < 0 or min(deadlines) < 0:
        raise ValueError("counts and deadlines must be non-negative")
    if filler_count < 0 or draws_remaining < 0:
        raise ValueError("filler_count and draws_remaining must be non-negative")
    if capacity <= 0:
        raise ValueError("capacity must be positive")

    initial = DeadlineState(
        target_counts=target_counts,
        secured=(False,) * len(target_counts),
        deadlines=deadlines,
        filler_count=filler_count,
        connector_available=True,
        draws_remaining=draws_remaining,
    )

    @lru_cache(maxsize=None)
    def value(state: DeadlineState) -> float:
        if all(state.secured):
            return 1.0
        if any(
            deadline < 0
            for deadline, secured in zip(state.deadlines, state.secured)
            if not secured
        ):
            return 0.0

        choices: list[float] = []

        if state.connector_available:
            searchable = [
                index
                for index, (count, secured) in enumerate(
                    zip(state.target_counts, state.secured)
                )
                if not secured and count > 0
            ]
            for output_count in range(1, min(capacity, len(searchable)) + 1):
                for subset in combinations(searchable, output_count):
                    counts = list(state.target_counts)
                    secured = list(state.secured)
                    for index in subset:
                        counts[index] -= 1
                        secured[index] = True
                    choices.append(
                        value(
                            DeadlineState(
                                target_counts=tuple(counts),
                                secured=tuple(secured),
                                deadlines=state.deadlines,
                                filler_count=state.filler_count,
                                connector_available=False,
                                draws_remaining=state.draws_remaining,
                            )
                        )
                    )

        can_wait = (
            state.draws_remaining > 0
            and all(
                deadline > 0
                for deadline, secured in zip(state.deadlines, state.secured)
                if not secured
            )
        )
        total_deck = sum(state.target_counts) + state.filler_count
        if can_wait and total_deck > 0:
            wait_value = 0.0
            for index, count in enumerate(state.target_counts):
                if count == 0:
                    continue
                counts = list(state.target_counts)
                counts[index] -= 1
                secured = list(state.secured)
                secured[index] = True
                deadlines_next = tuple(
                    deadline if is_secured else deadline - 1
                    for deadline, is_secured in zip(state.deadlines, secured)
                )
                wait_value += count / total_deck * value(
                    DeadlineState(
                        target_counts=tuple(counts),
                        secured=tuple(secured),
                        deadlines=deadlines_next,
                        filler_count=state.filler_count,
                        connector_available=state.connector_available,
                        draws_remaining=state.draws_remaining - 1,
                    )
                )

            if state.filler_count:
                deadlines_next = tuple(
                    deadline if secured else deadline - 1
                    for deadline, secured in zip(state.deadlines, state.secured)
                )
                wait_value += state.filler_count / total_deck * value(
                    DeadlineState(
                        target_counts=state.target_counts,
                        secured=state.secured,
                        deadlines=deadlines_next,
                        filler_count=state.filler_count - 1,
                        connector_available=state.connector_available,
                        draws_remaining=state.draws_remaining - 1,
                    )
                )
            choices.append(wait_value)

        return max(choices, default=0.0)

    return value(initial)
