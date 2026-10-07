"""Exact allocation of attack-effect damage counters across eligible targets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from board_object_kernel import BoardState
from damage_board_bridge import EffectCounterPlacement, apply_effect_counter_placement


@dataclass(frozen=True)
class CounterAllocationOutcome:
    requests: tuple[tuple[str, int], ...]
    placed: tuple[tuple[str, int], ...]
    newly_knocked_out_ids: tuple[str, ...]
    prize_value: int

    @property
    def knockout_count(self) -> int:
        return len(self.newly_knocked_out_ids)


def _compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, parts - 1):
            yield (first,) + rest


def enumerate_counter_allocations(
    board: BoardState,
    *,
    target_ids: tuple[str, ...],
    total_counters: int,
    hp_by_object_id: Mapping[str, int],
    prize_value_by_object_id: Mapping[str, int] | None = None,
    effect_immune_ids: frozenset[str] = frozenset(),
) -> tuple[CounterAllocationOutcome, ...]:
    """Enumerate every exact requested distribution over eligible targets."""

    if total_counters < 0:
        raise ValueError("total_counters must be non-negative")
    if len(target_ids) != len(set(target_ids)):
        raise ValueError("target_ids must be unique")
    if not target_ids:
        return ()

    values = prize_value_by_object_id or {}
    before_ko: dict[str, bool] = {}
    for target_id in target_ids:
        target = board.get(target_id)
        if target_id not in hp_by_object_id:
            raise ValueError(f"missing HP for {target_id!r}")
        hp = hp_by_object_id[target_id]
        if hp <= 0 or hp % 10 != 0:
            raise ValueError("Pokemon HP must be a positive multiple of 10")
        prize_value = values.get(target_id, 1)
        if prize_value < 0:
            raise ValueError("prize values must be non-negative")
        before_ko[target_id] = target.damage_counters * 10 >= hp

    outcomes: list[CounterAllocationOutcome] = []
    for allocation in _compositions(total_counters, len(target_ids)):
        current = board
        requests = tuple(zip(target_ids, allocation, strict=True))
        placed_rows: list[tuple[str, int]] = []
        for target_id, count in requests:
            current, placement = apply_effect_counter_placement(
                current,
                EffectCounterPlacement(
                    target_id,
                    count,
                    prevent_effects_of_attacks=target_id in effect_immune_ids,
                ),
            )
            placed_rows.append((target_id, placement.placed))

        newly_ko = tuple(
            target_id
            for target_id in target_ids
            if (
                not before_ko[target_id]
                and current.get(target_id).damage_counters * 10
                >= hp_by_object_id[target_id]
            )
        )
        prize_value = sum(values.get(target_id, 1) for target_id in newly_ko)
        outcomes.append(
            CounterAllocationOutcome(
                requests=requests,
                placed=tuple(placed_rows),
                newly_knocked_out_ids=newly_ko,
                prize_value=prize_value,
            )
        )

    return tuple(outcomes)


def best_by_knockouts(
    outcomes: tuple[CounterAllocationOutcome, ...],
) -> tuple[CounterAllocationOutcome, ...]:
    if not outcomes:
        return ()
    best = max(outcome.knockout_count for outcome in outcomes)
    return tuple(outcome for outcome in outcomes if outcome.knockout_count == best)


def best_by_prizes(
    outcomes: tuple[CounterAllocationOutcome, ...],
) -> tuple[CounterAllocationOutcome, ...]:
    if not outcomes:
        return ()
    best = max(outcome.prize_value for outcome in outcomes)
    return tuple(outcome for outcome in outcomes if outcome.prize_value == best)
