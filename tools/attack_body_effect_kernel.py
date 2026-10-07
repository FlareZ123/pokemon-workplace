"""Ordered attack-body effect kernel for copy-semantics witnesses."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TypeAlias

from board_object_kernel import BoardPokemon, BoardState, EnergyAttachment


WILDCARD_ENERGY = "*"


@dataclass(frozen=True)
class EffectState:
    actor_board: BoardState
    opponent_board: BoardState
    events: tuple[str, ...] = ()
    discarded_energy: tuple[EnergyAttachment, ...] = ()


@dataclass(frozen=True)
class DiscardAllEnergyOfType:
    symbol: str


@dataclass(frozen=True)
class DiscardOneEnergyOfType:
    symbol: str


@dataclass(frozen=True)
class AddDamageCounters:
    object_id: str
    count: int

    def __post_init__(self) -> None:
        if self.count < 0:
            raise ValueError("damage-counter count must be non-negative")


@dataclass(frozen=True)
class IfDid:
    prerequisite: "EffectStep"
    consequent: tuple["EffectStep", ...]


EffectStep: TypeAlias = (
    DiscardAllEnergyOfType
    | DiscardOneEnergyOfType
    | AddDamageCounters
    | IfDid
)


def _replace_board_object(board: BoardState, pokemon: BoardPokemon) -> BoardState:
    next_board = replace(
        board,
        objects=tuple(
            pokemon if row.object_id == pokemon.object_id else row
            for row in board.objects
        ),
    )
    next_board.validate()
    return next_board


def _provides_type(energy: EnergyAttachment, symbol: str) -> bool:
    return symbol in energy.units or WILDCARD_ENERGY in energy.units


def _apply(state: EffectState, step: EffectStep) -> tuple[EffectState, bool]:
    if isinstance(step, DiscardAllEnergyOfType):
        actor = state.actor_board.get(state.actor_board.active_id)
        discarded = tuple(
            energy for energy in actor.energy
            if _provides_type(energy, step.symbol)
        )
        kept = tuple(
            energy for energy in actor.energy
            if not _provides_type(energy, step.symbol)
        )
        if not discarded:
            return state, False
        next_actor = replace(actor, energy=kept)
        return (
            replace(
                state,
                actor_board=_replace_board_object(state.actor_board, next_actor),
                discarded_energy=state.discarded_energy + discarded,
                events=state.events + (f"discard_all_{step.symbol}_energy",),
            ),
            True,
        )

    if isinstance(step, DiscardOneEnergyOfType):
        actor = state.actor_board.get(state.actor_board.active_id)
        index = next(
            (
                i
                for i, energy in enumerate(actor.energy)
                if _provides_type(energy, step.symbol)
            ),
            None,
        )
        if index is None:
            return state, False
        discarded = actor.energy[index]
        kept = actor.energy[:index] + actor.energy[index + 1 :]
        next_actor = replace(actor, energy=kept)
        return (
            replace(
                state,
                actor_board=_replace_board_object(state.actor_board, next_actor),
                discarded_energy=state.discarded_energy + (discarded,),
                events=state.events + (f"discard_one_{step.symbol}_energy",),
            ),
            True,
        )

    if isinstance(step, AddDamageCounters):
        try:
            target = state.opponent_board.get(step.object_id)
        except KeyError:
            return state, False
        next_target = replace(
            target,
            damage_counters=target.damage_counters + step.count,
        )
        return (
            replace(
                state,
                opponent_board=_replace_board_object(
                    state.opponent_board,
                    next_target,
                ),
                events=state.events + (f"add_{step.count}_damage_counters",),
            ),
            True,
        )

    if isinstance(step, IfDid):
        after_prerequisite, did = _apply(state, step.prerequisite)
        if not did:
            return after_prerequisite, False
        current = after_prerequisite
        for consequent in step.consequent:
            current, _ = _apply(current, consequent)
        return current, True

    raise TypeError(step)


def execute_program(
    state: EffectState,
    steps: tuple[EffectStep, ...],
) -> EffectState:
    """Apply ordinary steps best-effort; IfDid explicitly gates dependents."""

    current = state
    for step in steps:
        current, _ = _apply(current, step)
    return current
