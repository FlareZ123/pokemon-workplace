"""Independent regressions for connector_capacity_deadlines."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_capacity_deadlines import capacity_deadline_value
from connector_capacity_option_value import capacity_option_value


def labeled_value(
    deck: tuple[str, ...],
    targets: tuple[str, ...],
    deadlines: tuple[int, ...],
    capacity: int,
    draws_remaining: int,
) -> float:
    channels = tuple(targets)
    deadline_by_channel = dict(zip(channels, deadlines))

    def channel_of(card: str) -> str | None:
        prefix = card.split(":", 1)[0]
        return prefix if prefix in deadline_by_channel else None

    @lru_cache(maxsize=None)
    def solve(
        remaining: tuple[str, ...],
        secured_key: tuple[str, ...],
        deadlines_key: tuple[tuple[str, int], ...],
        connector_available: bool,
        draws: int,
    ) -> float:
        secured = set(secured_key)
        current_deadlines = dict(deadlines_key)
        if secured == set(channels):
            return 1.0

        choices: list[float] = []
        if connector_available:
            searchable = [
                channel
                for channel in channels
                if channel not in secured
                and any(channel_of(card) == channel for card in remaining)
            ]
            for n in range(1, min(capacity, len(searchable)) + 1):
                for subset in combinations(searchable, n):
                    next_deck = list(remaining)
                    for channel in subset:
                        idx = next(
                            i for i, card in enumerate(next_deck)
                            if channel_of(card) == channel
                        )
                        next_deck.pop(idx)
                    choices.append(
                        solve(
                            tuple(sorted(next_deck)),
                            tuple(sorted(secured | set(subset))),
                            deadlines_key,
                            False,
                            draws,
                        )
                    )

        can_wait = draws > 0 and all(
            current_deadlines[channel] > 0
            for channel in channels
            if channel not in secured
        )
        if can_wait and remaining:
            total = 0.0
            for i, card in enumerate(remaining):
                next_deck = remaining[:i] + remaining[i + 1 :]
                channel = channel_of(card)
                next_secured = secured | ({channel} if channel else set())
                next_deadlines = dict(current_deadlines)
                for target in channels:
                    if target not in next_secured:
                        next_deadlines[target] -= 1
                total += solve(
                    tuple(sorted(next_deck)),
                    tuple(sorted(next_secured)),
                    tuple(sorted(next_deadlines.items())),
                    connector_available,
                    draws - 1,
                ) / len(remaining)
            choices.append(total)

        return max(choices, default=0.0)

    return solve(
        tuple(sorted(deck)),
        (),
        tuple(sorted(deadline_by_channel.items())),
        True,
        draws_remaining,
    )


def main() -> None:
    # One early channel forces immediate commitment in the symmetric m=k+1 family.
    for channels in range(2, 6):
        capacity = channels - 1
        target_names = tuple(chr(ord("A") + i) for i in range(channels))
        deck = tuple(
            [f"{target}:{copy}" for target in target_names for copy in range(2)]
            + [f"F:{i}" for i in range(40 - 2 * channels)]
        )
        relaxed = capacity_deadline_value(
            target_counts=(2,) * channels,
            deadlines=(1,) * channels,
            filler_count=40 - 2 * channels,
            capacity=capacity,
            draws_remaining=1,
        )
        urgent = capacity_deadline_value(
            target_counts=(2,) * channels,
            deadlines=(0,) + (1,) * (channels - 1),
            filler_count=40 - 2 * channels,
            capacity=capacity,
            draws_remaining=1,
        )
        prior = capacity_option_value(
            target_counts=(2,) * channels,
            filler_count=40 - 2 * channels,
            capacity=capacity,
            draws_remaining=1,
        )
        brute_relaxed = labeled_value(
            deck, target_names, (1,) * channels, capacity, 1
        )
        brute_urgent = labeled_value(
            deck, target_names, (0,) + (1,) * (channels - 1), capacity, 1
        )
        assert abs(relaxed - prior.optimal_success) < 1e-12
        assert abs(urgent - prior.eager_success) < 1e-12
        assert abs(relaxed - brute_relaxed) < 1e-12
        assert abs(urgent - brute_urgent) < 1e-12

    # Multi-draw deadline regression: one urgent channel removes the adaptive
    # hold option while the unresolved channel can still arrive later.
    target_names = ("A", "B", "C", "D")
    deck = tuple(
        [f"{target}:{copy}" for target in target_names for copy in range(2)]
        + [f"F:{i}" for i in range(7)]
    )
    exact = capacity_deadline_value(
        target_counts=(2, 2, 2, 2),
        deadlines=(0, 3, 3, 3),
        filler_count=7,
        capacity=3,
        draws_remaining=3,
    )
    brute = labeled_value(deck, target_names, (0, 3, 3, 3), 3, 3)
    assert abs(exact - brute) < 1e-12

    # More immediate deadlines than connector capacity is impossible.
    impossible = capacity_deadline_value(
        target_counts=(1, 1, 1),
        deadlines=(0, 0, 0),
        filler_count=7,
        capacity=2,
        draws_remaining=2,
    )
    assert impossible == 0.0

    print("all connector-capacity deadline regressions passed")


if __name__ == "__main__":
    main()
