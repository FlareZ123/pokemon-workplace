"""Independent regressions for connector_slot_deadlines."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_slot_deadlines import slot_deadline_value


def brute_value(
    deck: tuple[str, ...],
    targets: tuple[str, ...],
    target_slots: dict[str, tuple[str, ...]],
    connector_slots: tuple[str, ...],
    deadlines: tuple[int, ...],
    draws_remaining: int,
) -> float:
    deadline0 = dict(zip(targets, deadlines))

    def channel_of(card: str) -> str | None:
        prefix = card.split(":", 1)[0]
        return prefix if prefix in deadline0 else None

    def legal_subsets(remaining: tuple[str, ...], secured: frozenset[str]):
        live = [
            target for target in targets
            if target not in secured
            and any(channel_of(card) == target for card in remaining)
        ]
        out: set[tuple[str, ...]] = set()
        for size in range(1, min(len(live), len(connector_slots)) + 1):
            for subset in combinations(live, size):
                for slots in permutations(range(len(connector_slots)), size):
                    if all(
                        connector_slots[slot] in target_slots[target]
                        for target, slot in zip(subset, slots)
                    ):
                        out.add(tuple(sorted(subset)))
                        break
        return sorted(out)

    @lru_cache(maxsize=None)
    def solve(
        remaining: tuple[str, ...],
        secured: frozenset[str],
        deadline_key: tuple[tuple[str, int], ...],
        connector_available: bool,
        draws: int,
    ) -> float:
        if secured == frozenset(targets):
            return 1.0
        ds = dict(deadline_key)
        choices: list[float] = []

        if connector_available:
            for subset in legal_subsets(remaining, secured):
                next_deck = list(remaining)
                for target in subset:
                    idx = next(
                        i for i, card in enumerate(next_deck)
                        if channel_of(card) == target
                    )
                    next_deck.pop(idx)
                choices.append(
                    solve(
                        tuple(sorted(next_deck)),
                        secured | frozenset(subset),
                        deadline_key,
                        False,
                        draws,
                    )
                )

        can_wait = draws > 0 and all(
            ds[target] > 0 for target in targets if target not in secured
        )
        if can_wait and remaining:
            total = 0.0
            for i, card in enumerate(remaining):
                next_deck = remaining[:i] + remaining[i + 1 :]
                target = channel_of(card)
                next_secured = secured | ({target} if target else set())
                next_ds = dict(ds)
                for name in targets:
                    if name not in next_secured:
                        next_ds[name] -= 1
                total += solve(
                    tuple(sorted(next_deck)),
                    frozenset(next_secured),
                    tuple(sorted(next_ds.items())),
                    connector_available,
                    draws - 1,
                ) / len(remaining)
            choices.append(total)

        return max(choices, default=0.0)

    return solve(
        tuple(sorted(deck)), frozenset(), tuple(sorted(deadline0.items())),
        True, draws_remaining,
    )


def main() -> None:
    targets = ("A", "B", "C", "D")
    target_slots_tuple = (("Item",), ("Tool",), ("Tool",), ("Supporter",))
    target_slots = dict(zip(targets, target_slots_tuple))
    connector_slots = ("Item", "Tool", "Supporter", "Stadium")
    deck = tuple(
        [f"{target}:{copy}" for target in targets for copy in range(2)]
        + [f"F:{i}" for i in range(32)]
    )

    cases = {
        (1, 1, 1, 1): 0.1,
        (0, 1, 1, 1): 2 / 37,
        (1, 0, 1, 1): 2 / 37,
        (1, 0, 0, 1): 0.0,
        (0, 0, 0, 0): 0.0,
    }
    for deadlines, expected in cases.items():
        exact = slot_deadline_value(
            target_counts=(2, 2, 2, 2),
            target_slots=target_slots_tuple,
            connector_slots=connector_slots,
            deadlines=deadlines,
            filler_count=32,
            draws_remaining=1,
        )
        brute = brute_value(
            deck, targets, target_slots, connector_slots, deadlines, 1
        )
        assert abs(exact - brute) < 1e-12
        assert abs(exact - expected) < 1e-12

    # Scalar nominal capacity would solve four urgent channels immediately,
    # while typed matching fails when the two Tool-only channels are both urgent.
    distinct = (("Item",), ("Tool",), ("Supporter",), ("Stadium",))
    full = slot_deadline_value(
        target_counts=(1, 1, 1, 1),
        target_slots=distinct,
        connector_slots=connector_slots,
        deadlines=(0, 0, 0, 0),
        filler_count=4,
        draws_remaining=0,
    )
    collided = slot_deadline_value(
        target_counts=(1, 1, 1, 1),
        target_slots=target_slots_tuple,
        connector_slots=connector_slots,
        deadlines=(0, 0, 0, 0),
        filler_count=4,
        draws_remaining=0,
    )
    assert full == 1.0
    assert collided == 0.0

    print("all typed slot-deadline regressions passed")


if __name__ == "__main__":
    main()
