"""Finite-horizon option value for a bounded-capacity universal connector.

The model starts at an action point with one connector already in hand. Each
missing target channel has one or more searchable copies remaining in deck.
The connector may search one copy from each of up to ``capacity`` distinct
missing channels. It may require a scalar number of currently acceptable
discard cards. Between action points the player may wait for a natural draw.

The objective is deliberately narrow: secure every target channel by the
specified draw horizon. This isolates informational option value from other
uses of the connector.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from typing import Literal

Policy = Literal["optimal", "eager"]


@dataclass(frozen=True)
class CapacityOptionResult:
    optimal_success: float
    eager_success: float

    @property
    def waiting_gain(self) -> float:
        return self.optimal_success - self.eager_success


@dataclass(frozen=True)
class ConnectorState:
    target_counts: tuple[int, ...]
    secured: tuple[bool, ...]
    filler_count: int
    disposable_deck: int
    disposable_hand: int
    connector_available: bool
    draws_remaining: int


def _validate_state(state: ConnectorState, capacity: int, discard_cost: int) -> None:
    if len(state.target_counts) == 0:
        raise ValueError("at least one target channel is required")
    if len(state.target_counts) != len(state.secured):
        raise ValueError("target_counts and secured must have the same length")
    if min(state.target_counts) < 0:
        raise ValueError("target counts must be non-negative")
    if state.filler_count < 0 or state.disposable_deck < 0 or state.disposable_hand < 0:
        raise ValueError("resource counts must be non-negative")
    if state.draws_remaining < 0:
        raise ValueError("draws_remaining must be non-negative")
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    if discard_cost < 0:
        raise ValueError("discard_cost must be non-negative")


def capacity_option_value(
    *,
    target_counts: tuple[int, ...],
    filler_count: int,
    capacity: int,
    draws_remaining: int,
    discard_cost: int = 0,
    disposable_deck: int = 0,
    disposable_hand: int = 0,
) -> CapacityOptionResult:
    """Return optimal and eager success probabilities from one action point.

    ``optimal`` may preserve the connector and take another natural draw.
    ``eager`` uses the connector immediately whenever it is payable; when
    several output subsets are legal, it still chooses the best subset.

    Search removes one physical target copy from deck for every channel it
    secures. Natural target draws also remove one copy and secure that channel.
    Drawing additional copies of an already secured channel only shrinks deck.
    """

    initial = ConnectorState(
        target_counts=target_counts,
        secured=(False,) * len(target_counts),
        filler_count=filler_count,
        disposable_deck=disposable_deck,
        disposable_hand=disposable_hand,
        connector_available=True,
        draws_remaining=draws_remaining,
    )
    _validate_state(initial, capacity, discard_cost)

    def solve(policy: Policy) -> float:
        @lru_cache(maxsize=None)
        def value(state: ConnectorState) -> float:
            if all(state.secured):
                return 1.0

            total_deck = (
                sum(state.target_counts)
                + state.filler_count
                + state.disposable_deck
            )

            use_values: list[float] = []
            if state.connector_available and state.disposable_hand >= discard_cost:
                searchable = [
                    index
                    for index, (count, secured) in enumerate(
                        zip(state.target_counts, state.secured)
                    )
                    if not secured and count > 0
                ]
                max_outputs = min(capacity, len(searchable))
                for output_count in range(1, max_outputs + 1):
                    for subset in combinations(searchable, output_count):
                        counts = list(state.target_counts)
                        secured = list(state.secured)
                        for index in subset:
                            counts[index] -= 1
                            secured[index] = True
                        use_values.append(
                            value(
                                ConnectorState(
                                    target_counts=tuple(counts),
                                    secured=tuple(secured),
                                    filler_count=state.filler_count,
                                    disposable_deck=state.disposable_deck,
                                    disposable_hand=state.disposable_hand - discard_cost,
                                    connector_available=False,
                                    draws_remaining=state.draws_remaining,
                                )
                            )
                        )

            wait_value = 0.0
            if state.draws_remaining > 0 and total_deck > 0:
                for index, count in enumerate(state.target_counts):
                    if count == 0:
                        continue
                    counts = list(state.target_counts)
                    counts[index] -= 1
                    secured = list(state.secured)
                    secured[index] = True
                    wait_value += count / total_deck * value(
                        ConnectorState(
                            target_counts=tuple(counts),
                            secured=tuple(secured),
                            filler_count=state.filler_count,
                            disposable_deck=state.disposable_deck,
                            disposable_hand=state.disposable_hand,
                            connector_available=state.connector_available,
                            draws_remaining=state.draws_remaining - 1,
                        )
                    )

                if state.disposable_deck:
                    wait_value += state.disposable_deck / total_deck * value(
                        ConnectorState(
                            target_counts=state.target_counts,
                            secured=state.secured,
                            filler_count=state.filler_count,
                            disposable_deck=state.disposable_deck - 1,
                            disposable_hand=state.disposable_hand + 1,
                            connector_available=state.connector_available,
                            draws_remaining=state.draws_remaining - 1,
                        )
                    )

                if state.filler_count:
                    wait_value += state.filler_count / total_deck * value(
                        ConnectorState(
                            target_counts=state.target_counts,
                            secured=state.secured,
                            filler_count=state.filler_count - 1,
                            disposable_deck=state.disposable_deck,
                            disposable_hand=state.disposable_hand,
                            connector_available=state.connector_available,
                            draws_remaining=state.draws_remaining - 1,
                        )
                    )

            if policy == "eager" and use_values:
                return max(use_values)
            return max([wait_value, *use_values], default=0.0)

        return value(initial)

    return CapacityOptionResult(
        optimal_success=solve("optimal"),
        eager_success=solve("eager"),
    )


def one_draw_closed_form(*, channels: int, copies_per_channel: int, deck_size: int) -> CapacityOptionResult:
    """Closed form for capacity = channels - 1, cost 0, one future draw."""
    if channels < 2:
        raise ValueError("channels must be at least 2")
    if copies_per_channel <= 0:
        raise ValueError("copies_per_channel must be positive")
    targets = channels * copies_per_channel
    if deck_size < targets:
        raise ValueError("deck_size cannot be smaller than target population")
    capacity = channels - 1
    optimal = targets / deck_size
    eager = copies_per_channel / (deck_size - capacity)
    return CapacityOptionResult(optimal_success=optimal, eager_success=eager)
