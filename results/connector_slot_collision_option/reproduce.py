"""Independent regressions for connector_slot_collision_option."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations, permutations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_slot_collision_option import slot_collision_option_value


def labeled_value(
    deck: tuple[str, ...],
    targets: tuple[str, ...],
    target_slots: dict[str, tuple[str, ...]],
    connector_slots: tuple[str, ...],
    draws_remaining: int,
    *,
    eager: bool,
) -> float:
    """Brute force labels and explicit target-to-slot assignments."""

    def channel_of(card: str) -> str | None:
        prefix = card.split(":", 1)[0]
        return prefix if prefix in targets else None

    def searchable_subsets(remaining: tuple[str, ...], secured: frozenset[str]):
        live = [
            target for target in targets
            if target not in secured
            and any(channel_of(card) == target for card in remaining)
        ]
        legal: set[tuple[str, ...]] = set()
        for size in range(1, min(len(live), len(connector_slots)) + 1):
            for subset in combinations(live, size):
                for chosen_slots in permutations(range(len(connector_slots)), size):
                    if all(
                        connector_slots[slot] in target_slots[target]
                        for target, slot in zip(subset, chosen_slots)
                    ):
                        legal.add(tuple(sorted(subset)))
                        break
        return sorted(legal)

    @lru_cache(maxsize=None)
    def solve(
        remaining: tuple[str, ...],
        secured: frozenset[str],
        connector_available: bool,
        draws: int,
    ) -> float:
        if secured == frozenset(targets):
            return 1.0

        use_values: list[float] = []
        if connector_available:
            for subset in searchable_subsets(remaining, secured):
                next_deck = list(remaining)
                for target in subset:
                    index = next(
                        i for i, card in enumerate(next_deck)
                        if channel_of(card) == target
                    )
                    next_deck.pop(index)
                use_values.append(
                    solve(
                        tuple(sorted(next_deck)),
                        secured | frozenset(subset),
                        False,
                        draws,
                    )
                )

        wait = 0.0
        if draws and remaining:
            for index, card in enumerate(remaining):
                next_deck = remaining[:index] + remaining[index + 1 :]
                target = channel_of(card)
                wait += solve(
                    tuple(sorted(next_deck)),
                    secured | ({target} if target else set()),
                    connector_available,
                    draws - 1,
                ) / len(remaining)

        if eager and use_values:
            return max(use_values)
        return max([wait, *use_values], default=0.0)

    return solve(tuple(sorted(deck)), frozenset(), True, draws_remaining)


def main() -> None:
    connector_slots = ("Item", "Tool", "Supporter", "Stadium")
    targets = ("A", "B", "C", "D")
    deck = tuple(
        [f"{target}:{copy}" for target in targets for copy in range(2)]
        + [f"F:{i}" for i in range(32)]
    )

    # Distinct slots have full immediate matching capacity.
    distinct = (("Item",), ("Tool",), ("Supporter",), ("Stadium",))
    result = slot_collision_option_value(
        target_counts=(2, 2, 2, 2),
        target_slots=distinct,
        connector_slots=connector_slots,
        filler_count=32,
        draws_remaining=4,
    )
    assert result.immediate_matching_size == 4
    assert result.optimal_success == 1.0
    assert result.eager_success == 1.0

    # One pair of Tool-only targets creates one unit of matching deficiency.
    pair = (("Item",), ("Tool",), ("Tool",), ("Supporter",))
    for draws in range(1, 5):
        result = slot_collision_option_value(
            target_counts=(2, 2, 2, 2),
            target_slots=pair,
            connector_slots=connector_slots,
            filler_count=32,
            draws_remaining=draws,
        )
        brute_opt = labeled_value(
            deck, targets,
            dict(zip(targets, pair)),
            connector_slots, draws, eager=False,
        )
        brute_eager = labeled_value(
            deck, targets,
            dict(zip(targets, pair)),
            connector_slots, draws, eager=True,
        )
        closed_opt = 1.0 - comb(36, draws) / comb(40, draws)
        closed_eager = 1.0 - comb(35, draws) / comb(37, draws)
        assert result.immediate_matching_size == 3
        assert abs(result.optimal_success - brute_opt) < 1e-12
        assert abs(result.eager_success - brute_eager) < 1e-12
        assert abs(result.optimal_success - closed_opt) < 1e-12
        assert abs(result.eager_success - closed_eager) < 1e-12

    # A third Tool-only target creates two units of matching deficiency.
    triple = (("Item",), ("Tool",), ("Tool",), ("Tool",))
    result = slot_collision_option_value(
        target_counts=(2, 2, 2, 2),
        target_slots=triple,
        connector_slots=connector_slots,
        filler_count=32,
        draws_remaining=2,
    )
    brute_opt = labeled_value(
        deck, targets, dict(zip(targets, triple)),
        connector_slots, 2, eager=False,
    )
    brute_eager = labeled_value(
        deck, targets, dict(zip(targets, triple)),
        connector_slots, 2, eager=True,
    )
    assert result.immediate_matching_size == 2
    assert abs(result.optimal_success - 12 / comb(40, 2)) < 1e-12
    assert abs(result.eager_success - 4 / comb(38, 2)) < 1e-12
    assert abs(result.optimal_success - brute_opt) < 1e-12
    assert abs(result.eager_success - brute_eager) < 1e-12

    # Alternative eligibility removes the pair collision.
    flexible = (("Item",), ("Tool",), ("Tool", "Stadium"), ("Supporter",))
    result = slot_collision_option_value(
        target_counts=(2, 2, 2, 2),
        target_slots=flexible,
        connector_slots=connector_slots,
        filler_count=32,
        draws_remaining=1,
    )
    assert result.immediate_matching_size == 4
    assert result.optimal_success == 1.0

    print("all connector slot-collision option regressions passed")


if __name__ == "__main__":
    main()
