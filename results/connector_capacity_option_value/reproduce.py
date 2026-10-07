"""Independent regressions for connector_capacity_option_value."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_capacity_option_value import (
    capacity_option_value,
    one_draw_closed_form,
)


def labeled_optimal_value(
    deck: tuple[str, ...],
    targets: tuple[str, ...],
    capacity: int,
    draws_remaining: int,
    *,
    discard_cost: int = 0,
    disposable_hand: int = 0,
) -> float:
    """Brute-force a labeled physical-card game tree.

    Labels beginning with ``D:`` are acceptable discard cards. Labels beginning
    with ``F:`` are filler. Target cards are named ``<channel>:<copy>``.
    """

    channels = frozenset(targets)

    def channel_of(label: str) -> str | None:
        prefix = label.split(":", 1)[0]
        return prefix if prefix in channels else None

    @lru_cache(maxsize=None)
    def value(
        remaining: tuple[str, ...],
        secured: frozenset[str],
        connector_available: bool,
        draws: int,
        dhand: int,
    ) -> float:
        if secured == channels:
            return 1.0

        best_use = 0.0
        if connector_available and dhand >= discard_cost:
            searchable = sorted(
                channel
                for channel in channels - secured
                if any(channel_of(card) == channel for card in remaining)
            )
            for count in range(1, min(capacity, len(searchable)) + 1):
                for subset in combinations(searchable, count):
                    next_deck = list(remaining)
                    for channel in subset:
                        index = next(
                            i
                            for i, card in enumerate(next_deck)
                            if channel_of(card) == channel
                        )
                        next_deck.pop(index)
                    best_use = max(
                        best_use,
                        value(
                            tuple(sorted(next_deck)),
                            secured | frozenset(subset),
                            False,
                            draws,
                            dhand - discard_cost,
                        ),
                    )

        wait = 0.0
        if draws and remaining:
            for index, card in enumerate(remaining):
                next_deck = remaining[:index] + remaining[index + 1 :]
                channel = channel_of(card)
                next_secured = secured | ({channel} if channel else set())
                next_dhand = dhand + int(card.startswith("D:"))
                wait += value(
                    tuple(sorted(next_deck)),
                    frozenset(next_secured),
                    connector_available,
                    draws - 1,
                    next_dhand,
                ) / len(remaining)
        return max(best_use, wait)

    return value(tuple(sorted(deck)), frozenset(), True, draws_remaining, disposable_hand)


def labeled_eager_value(
    deck: tuple[str, ...],
    targets: tuple[str, ...],
    capacity: int,
    draws_remaining: int,
) -> float:
    """Use immediately, choosing the best searchable subset, then draw."""

    channels = set(targets)

    def channel_of(label: str) -> str | None:
        prefix = label.split(":", 1)[0]
        return prefix if prefix in channels else None

    best = 0.0
    for subset in combinations(targets, min(capacity, len(targets))):
        next_deck = list(deck)
        for channel in subset:
            index = next(i for i, card in enumerate(next_deck) if channel_of(card) == channel)
            next_deck.pop(index)
        secured = set(subset)
        if secured == channels:
            best = 1.0
            continue

        @lru_cache(maxsize=None)
        def draws_only(remaining: tuple[str, ...], secured_key: tuple[str, ...], draws: int) -> float:
            secured_now = set(secured_key)
            if secured_now == channels:
                return 1.0
            if draws == 0:
                return 0.0
            total = 0.0
            for i, card in enumerate(remaining):
                next_remaining = remaining[:i] + remaining[i + 1 :]
                channel = channel_of(card)
                next_secured = secured_now | ({channel} if channel else set())
                total += draws_only(
                    tuple(sorted(next_remaining)),
                    tuple(sorted(next_secured)),
                    draws - 1,
                ) / len(remaining)
            return total

        best = max(
            best,
            draws_only(tuple(sorted(next_deck)), tuple(sorted(secured)), draws_remaining),
        )
    return best


def main() -> None:
    # Closed form and labeled one-draw enumeration independently reproduce the
    # capacity = channels - 1 family.
    for channels in range(2, 6):
        targets = tuple(chr(ord("A") + i) for i in range(channels))
        deck = tuple(
            [f"{target}:{copy}" for target in targets for copy in range(2)]
            + [f"F:{i}" for i in range(40 - 2 * channels)]
        )
        capacity = channels - 1
        exact = capacity_option_value(
            target_counts=(2,) * channels,
            filler_count=40 - 2 * channels,
            capacity=capacity,
            draws_remaining=1,
        )
        closed = one_draw_closed_form(
            channels=channels,
            copies_per_channel=2,
            deck_size=40,
        )
        brute_opt = labeled_optimal_value(deck, targets, capacity, 1)
        brute_eager = labeled_eager_value(deck, targets, capacity, 1)
        assert abs(exact.optimal_success - closed.optimal_success) < 1e-12
        assert abs(exact.eager_success - closed.eager_success) < 1e-12
        assert abs(exact.optimal_success - brute_opt) < 1e-12
        assert abs(exact.eager_success - brute_eager) < 1e-12

    # Independent labeled multi-draw regression.
    targets = ("A", "B", "C")
    deck = tuple(
        [f"{target}:{copy}" for target in targets for copy in range(2)]
        + [f"F:{i}" for i in range(3)]
    )
    exact = capacity_option_value(
        target_counts=(2, 2, 2),
        filler_count=3,
        capacity=2,
        draws_remaining=2,
    )
    brute = labeled_optimal_value(deck, targets, 2, 2)
    assert abs(exact.optimal_success - brute) < 1e-12

    # Discard-gated full-capacity regression: one acceptable draw is required
    # to move from two discard cards in hand to the cost-three threshold.
    targets = ("A", "B")
    deck = tuple(
        ["A:0", "B:0"]
        + [f"D:{i}" for i in range(2)]
        + [f"F:{i}" for i in range(4)]
    )
    exact = capacity_option_value(
        target_counts=(1, 1),
        filler_count=4,
        disposable_deck=2,
        disposable_hand=2,
        capacity=2,
        discard_cost=3,
        draws_remaining=1,
    )
    brute = labeled_optimal_value(
        deck,
        targets,
        2,
        1,
        discard_cost=3,
        disposable_hand=2,
    )
    assert abs(exact.optimal_success - brute) < 1e-12
    assert abs(exact.optimal_success - 0.25) < 1e-12

    print("all connector-capacity option-value regressions passed")


if __name__ == "__main__":
    main()
