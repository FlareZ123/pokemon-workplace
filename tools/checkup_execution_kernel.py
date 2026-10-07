"""Deterministic multi-Pokémon damage-counter execution for Pokémon Checkup.

This kernel preserves the Checkup phase boundary: counter mutations resolve in
chosen order while every Pokémon remains present, then the final zero-HP batch is
identified for downstream Knock Out processing.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping

from special_condition_state import CHECKUP_CONDITION_BLOCK


class MutationKind(str, Enum):
    PUT = "put"
    HEAL = "heal"


@dataclass(frozen=True)
class CheckupPokemon:
    object_id: str
    hp: int
    damage_counters: int = 0

    def __post_init__(self) -> None:
        if not self.object_id:
            raise ValueError("object_id must be non-empty")
        if self.hp <= 0:
            raise ValueError("hp must be positive")
        if self.damage_counters < 0:
            raise ValueError("damage_counters must be non-negative")

    @property
    def remaining_hp(self) -> int:
        return self.hp - 10 * self.damage_counters


@dataclass(frozen=True)
class CounterMutation:
    mutation_id: str
    kind: MutationKind
    targets: tuple[str, ...]
    amount: int

    def __post_init__(self) -> None:
        if not self.mutation_id:
            raise ValueError("mutation_id must be non-empty")
        if not self.targets or len(self.targets) != len(set(self.targets)):
            raise ValueError("targets must be non-empty and unique")
        if self.amount < 0:
            raise ValueError("amount must be non-negative")


@dataclass(frozen=True)
class CheckupBoard:
    pokemon: tuple[CheckupPokemon, ...]

    def __post_init__(self) -> None:
        ids = [row.object_id for row in self.pokemon]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("board Pokémon IDs must be non-empty and unique")

    def get(self, object_id: str) -> CheckupPokemon:
        for pokemon in self.pokemon:
            if pokemon.object_id == object_id:
                return pokemon
        raise KeyError(object_id)


@dataclass(frozen=True)
class CheckupSnapshot:
    token: str
    board: CheckupBoard
    zero_hp_ids: tuple[str, ...]


@dataclass(frozen=True)
class CheckupExecution:
    initial_board: CheckupBoard
    snapshots: tuple[CheckupSnapshot, ...]
    final_board: CheckupBoard
    knocked_out_ids: tuple[str, ...]


def zero_hp_ids(board: CheckupBoard) -> tuple[str, ...]:
    return tuple(
        pokemon.object_id
        for pokemon in board.pokemon
        if pokemon.remaining_hp <= 0
    )


def apply_mutation(board: CheckupBoard, mutation: CounterMutation) -> CheckupBoard:
    known = {pokemon.object_id for pokemon in board.pokemon}
    unknown = set(mutation.targets) - known
    if unknown:
        raise ValueError(f"unknown mutation targets: {sorted(unknown)!r}")

    updated: list[CheckupPokemon] = []
    targets = set(mutation.targets)
    for pokemon in board.pokemon:
        if pokemon.object_id not in targets:
            updated.append(pokemon)
            continue
        if mutation.kind == MutationKind.PUT:
            damage = pokemon.damage_counters + mutation.amount
        elif mutation.kind == MutationKind.HEAL:
            damage = max(0, pokemon.damage_counters - mutation.amount)
        else:
            raise ValueError(f"unsupported mutation kind: {mutation.kind!r}")
        updated.append(replace(pokemon, damage_counters=damage))
    return CheckupBoard(tuple(updated))


def _apply_mutation_sequence(
    board: CheckupBoard,
    mutations: tuple[CounterMutation, ...],
) -> CheckupBoard:
    for mutation in mutations:
        board = apply_mutation(board, mutation)
    return board


def execute_checkup_schedule(
    initial_board: CheckupBoard,
    schedule: tuple[str, ...],
    *,
    condition_mutations: tuple[CounterMutation, ...] = (),
    effect_mutations: Mapping[str, tuple[CounterMutation, ...]],
) -> CheckupExecution:
    """Apply one legal Checkup schedule and defer KO selection to the end.

    Intermediate snapshots may contain zero-HP Pokémon. They remain available as
    mutation targets until all scheduled Checkup work is complete. The returned
    knocked_out_ids is the final batch only; actual disposal/Prize resolution is
    delegated to the repository's Knock Out subsystem.
    """

    if schedule.count(CHECKUP_CONDITION_BLOCK) != 1:
        raise ValueError("schedule must contain exactly one condition block")
    effect_tokens = tuple(
        token for token in schedule if token != CHECKUP_CONDITION_BLOCK
    )
    if len(effect_tokens) != len(set(effect_tokens)):
        raise ValueError("effect IDs cannot repeat in a schedule")
    if set(effect_tokens) != set(effect_mutations):
        raise ValueError("schedule effect IDs must match effect_mutations")

    board = initial_board
    snapshots: list[CheckupSnapshot] = []
    for token in schedule:
        if token == CHECKUP_CONDITION_BLOCK:
            board = _apply_mutation_sequence(board, condition_mutations)
        else:
            board = _apply_mutation_sequence(board, effect_mutations[token])
        snapshots.append(CheckupSnapshot(token, board, zero_hp_ids(board)))

    return CheckupExecution(
        initial_board=initial_board,
        snapshots=tuple(snapshots),
        final_board=board,
        knocked_out_ids=zero_hp_ids(board),
    )
