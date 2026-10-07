"""Per-target deadlines with typed connector output slots."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from connector_slot_collision_option import _matchable_subsets


@dataclass(frozen=True)
class SlotDeadlineState:
    target_counts: tuple[int, ...]
    secured: tuple[bool, ...]
    deadlines: tuple[int, ...]
    filler_count: int
    connector_available: bool
    draws_remaining: int


def slot_deadline_value(
    *,
    target_counts: tuple[int, ...],
    target_slots: tuple[tuple[str, ...], ...],
    connector_slots: tuple[str, ...],
    deadlines: tuple[int, ...],
    filler_count: int,
    draws_remaining: int,
) -> float:
    """Return exact optimal probability that all typed targets meet deadlines."""
    n = len(target_counts)
    if n == 0:
        raise ValueError("at least one target channel is required")
    if len(target_slots) != n or len(deadlines) != n:
        raise ValueError("target tuples must have the same length")
    if min(target_counts) < 0 or min(deadlines) < 0:
        raise ValueError("target counts and deadlines must be non-negative")
    if filler_count < 0 or draws_remaining < 0:
        raise ValueError("filler_count and draws_remaining must be non-negative")
    if not connector_slots or any(not slots for slots in target_slots):
        raise ValueError("connector and target slot eligibility must be non-empty")

    initial = SlotDeadlineState(
        target_counts=target_counts,
        secured=(False,) * n,
        deadlines=deadlines,
        filler_count=filler_count,
        connector_available=True,
        draws_remaining=draws_remaining,
    )

    @lru_cache(maxsize=None)
    def value(state: SlotDeadlineState) -> float:
        if all(state.secured):
            return 1.0

        choices: list[float] = []
        if state.connector_available:
            searchable = tuple(
                i for i, (count, done) in enumerate(
                    zip(state.target_counts, state.secured)
                )
                if count > 0 and not done
            )
            for subset in _matchable_subsets(
                searchable, target_slots, connector_slots
            ):
                next_counts = list(state.target_counts)
                next_secured = list(state.secured)
                for index in subset:
                    next_counts[index] -= 1
                    next_secured[index] = True
                choices.append(
                    value(
                        SlotDeadlineState(
                            target_counts=tuple(next_counts),
                            secured=tuple(next_secured),
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
                for deadline, done in zip(state.deadlines, state.secured)
                if not done
            )
        )
        deck_size = sum(state.target_counts) + state.filler_count
        if can_wait and deck_size > 0:
            wait_value = 0.0
            for index, count in enumerate(state.target_counts):
                if count == 0:
                    continue
                next_counts = list(state.target_counts)
                next_counts[index] -= 1
                next_secured = list(state.secured)
                next_secured[index] = True
                next_deadlines = tuple(
                    deadline if done else deadline - 1
                    for deadline, done in zip(state.deadlines, next_secured)
                )
                wait_value += count / deck_size * value(
                    SlotDeadlineState(
                        target_counts=tuple(next_counts),
                        secured=tuple(next_secured),
                        deadlines=next_deadlines,
                        filler_count=state.filler_count,
                        connector_available=state.connector_available,
                        draws_remaining=state.draws_remaining - 1,
                    )
                )
            if state.filler_count:
                next_deadlines = tuple(
                    deadline if done else deadline - 1
                    for deadline, done in zip(state.deadlines, state.secured)
                )
                wait_value += state.filler_count / deck_size * value(
                    SlotDeadlineState(
                        target_counts=state.target_counts,
                        secured=state.secured,
                        deadlines=next_deadlines,
                        filler_count=state.filler_count - 1,
                        connector_available=state.connector_available,
                        draws_remaining=state.draws_remaining - 1,
                    )
                )
            choices.append(wait_value)

        return max(choices, default=0.0)

    return value(initial)
