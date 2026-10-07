"""Compile typed Special Condition state into Checkup board mutations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from checkup_execution_kernel import (
    CheckupBoard,
    CheckupExecution,
    CounterMutation,
    MutationKind,
    execute_checkup_schedule,
)
from special_condition_state import (
    CHECKUP_ORDER,
    ConditionKind,
    ConditionModifier,
)
from timed_special_conditions import (
    BasicCheckupOutcome,
    TimedConditionState,
    resolve_basic_checkup,
)


@dataclass(frozen=True)
class CoinOutcomes:
    burn_heads: bool | None = None
    asleep_heads: bool | None = None


@dataclass(frozen=True)
class ConditionBlockCompilation:
    next_conditions: tuple[tuple[str, TimedConditionState], ...]
    outcomes: tuple[tuple[str, BasicCheckupOutcome], ...]
    mutations: tuple[CounterMutation, ...]

    def conditions_for(self, object_id: str) -> TimedConditionState:
        for key, state in self.next_conditions:
            if key == object_id:
                return state
        raise KeyError(object_id)


@dataclass(frozen=True)
class TypedCheckupExecution:
    condition_block: ConditionBlockCompilation
    board_execution: CheckupExecution


def compile_condition_block(
    condition_states: Mapping[str, TimedConditionState],
    *,
    completed_turn_player: str,
    completed_turn_serial: int,
    coin_outcomes: Mapping[str, CoinOutcomes] | None = None,
    modifiers: Mapping[str, tuple[ConditionModifier, ...]] | None = None,
) -> ConditionBlockCompilation:
    """Resolve each object's base conditions and compile ordered counter mutations."""

    coins = {} if coin_outcomes is None else dict(coin_outcomes)
    mods = {} if modifiers is None else dict(modifiers)

    unknown_coin_ids = set(coins) - set(condition_states)
    unknown_modifier_ids = set(mods) - set(condition_states)
    if unknown_coin_ids or unknown_modifier_ids:
        raise ValueError("coin/modifier IDs must refer to condition-state objects")

    outcomes: dict[str, BasicCheckupOutcome] = {}
    for object_id in sorted(condition_states):
        coin = coins.get(object_id, CoinOutcomes())
        outcomes[object_id] = resolve_basic_checkup(
            condition_states[object_id],
            completed_turn_player=completed_turn_player,
            completed_turn_serial=completed_turn_serial,
            burn_coin_heads=coin.burn_heads,
            asleep_coin_heads=coin.asleep_heads,
            modifiers=mods.get(object_id, ()),
        )

    mutations: list[CounterMutation] = []
    for kind in CHECKUP_ORDER:
        for object_id in sorted(outcomes):
            outcome = outcomes[object_id]
            for event_kind, amount in outcome.damage_counter_events:
                if event_kind != kind:
                    continue
                mutations.append(
                    CounterMutation(
                        mutation_id=f"condition:{kind.value}:{object_id}",
                        kind=MutationKind.PUT,
                        targets=(object_id,),
                        amount=amount,
                    )
                )

    return ConditionBlockCompilation(
        next_conditions=tuple(
            (object_id, outcomes[object_id].next_state)
            for object_id in sorted(outcomes)
        ),
        outcomes=tuple(
            (object_id, outcomes[object_id])
            for object_id in sorted(outcomes)
        ),
        mutations=tuple(mutations),
    )


def execute_static_typed_checkup(
    board: CheckupBoard,
    schedule: tuple[str, ...],
    *,
    condition_states: Mapping[str, TimedConditionState],
    completed_turn_player: str,
    completed_turn_serial: int,
    effect_mutations: Mapping[str, tuple[CounterMutation, ...]],
    coin_outcomes: Mapping[str, CoinOutcomes] | None = None,
    modifiers: Mapping[str, tuple[ConditionModifier, ...]] | None = None,
) -> TypedCheckupExecution:
    """Execute a schedule whose non-condition effects mutate counters only.

    Because the supplied effect mutations cannot change Special Conditions or
    modifier eligibility, the condition block can be compiled once and inserted
    at its scheduled position.
    """

    board_ids = {pokemon.object_id for pokemon in board.pokemon}
    if set(condition_states) != board_ids:
        raise ValueError("condition state IDs must match Checkup board IDs exactly")

    compiled = compile_condition_block(
        condition_states,
        completed_turn_player=completed_turn_player,
        completed_turn_serial=completed_turn_serial,
        coin_outcomes=coin_outcomes,
        modifiers=modifiers,
    )
    executed = execute_checkup_schedule(
        board,
        schedule,
        condition_mutations=compiled.mutations,
        effect_mutations=effect_mutations,
    )
    return TypedCheckupExecution(compiled, executed)
