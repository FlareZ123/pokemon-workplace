from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from lock_state_kernel import PokemonState, clear_attack_effects_on_position_or_evolution_change


class AttachmentKind(str, Enum):
    ENERGY = "energy"
    TOOL = "tool"
    OTHER = "other"


@dataclass(frozen=True)
class PokemonCard:
    card_id: str
    name: str
    evolves_from: str | None = None


@dataclass(frozen=True)
class Attachment:
    card_id: str
    name: str
    kind: AttachmentKind
    retreat_units: int = 0

    def __post_init__(self) -> None:
        if self.retreat_units < 0:
            raise ValueError("negative retreat units")
        if self.kind != AttachmentKind.ENERGY and self.retreat_units:
            raise ValueError("only Energy provides retreat units")


@dataclass(frozen=True)
class BoardPokemon:
    pokemon_id: str
    stack: tuple[PokemonCard, ...]
    retreat_cost: int
    damage_counters: int = 0
    attachments: tuple[Attachment, ...] = ()
    combat: PokemonState = PokemonState()
    special_conditions: frozenset[str] = frozenset()
    evolution_eligible: bool = True

    @property
    def name(self) -> str:
        return self.stack[-1].name


@dataclass(frozen=True)
class BoardState:
    pokemon: tuple[BoardPokemon, ...]
    active_id: str
    retreat_used: bool = False
    evolution_allowed: bool = True
    bench_capacity: int = 5

    def get(self, pokemon_id: str) -> BoardPokemon:
        return next(p for p in self.pokemon if p.pokemon_id == pokemon_id)

    @property
    def bench_ids(self) -> tuple[str, ...]:
        return tuple(p.pokemon_id for p in self.pokemon if p.pokemon_id != self.active_id)


@dataclass(frozen=True)
class BoardTransition:
    state: BoardState
    discarded_card_ids: tuple[str, ...] = ()


def make_state(
    pokemon: Iterable[BoardPokemon], *, active_id: str, retreat_used: bool = False,
    evolution_allowed: bool = True, bench_capacity: int = 5,
) -> BoardState:
    state = BoardState(tuple(pokemon), active_id, retreat_used, evolution_allowed, bench_capacity)
    validate_state(state)
    return state


def validate_state(state: BoardState) -> None:
    ids = [p.pokemon_id for p in state.pokemon]
    if state.bench_capacity < 0 or len(state.pokemon) - 1 > state.bench_capacity:
        raise ValueError("invalid Bench occupancy")
    if len(ids) != len(set(ids)) or state.active_id not in ids:
        raise ValueError("invalid Pokemon identity")
    physical_ids: list[str] = []
    for p in state.pokemon:
        if not p.stack or p.retreat_cost < 0 or p.damage_counters < 0:
            raise ValueError("invalid Pokemon state")
        physical_ids += [card.card_id for card in p.stack]
        physical_ids += [card.card_id for card in p.attachments]
        tools = [card for card in p.attachments if card.kind == AttachmentKind.TOOL]
        if len(tools) > 1 or p.combat.tool_attached != bool(tools):
            raise ValueError("Tool state mismatch")
        if p.pokemon_id != state.active_id and (
            p.special_conditions or p.combat.temporary_attack_lock or p.combat.temporary_retreat_lock
        ):
            raise ValueError("Benched Pokemon retains transient Active state")
    if len(physical_ids) != len(set(physical_ids)):
        raise ValueError("duplicate physical card ID")


def replace_pokemon(state: BoardState, updated: BoardPokemon) -> BoardState:
    next_state = replace(state, pokemon=tuple(
        updated if p.pokemon_id == updated.pokemon_id else p for p in state.pokemon
    ))
    validate_state(next_state)
    return next_state


def clear_for_bench(pokemon: BoardPokemon) -> BoardPokemon:
    return replace(
        pokemon,
        combat=clear_attack_effects_on_position_or_evolution_change(pokemon.combat),
        special_conditions=frozenset(),
    )
