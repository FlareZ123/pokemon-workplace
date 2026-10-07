"""Per-Pokemon board-object state for Active/Bench movement.

The model preserves persistent state on a Pokemon object while position changes:
attached Energy cards, Tool attachment, damage, and card identity stay with the
object. Temporary attack effects and Special Conditions clear from an outgoing
Active when it moves to the Bench, matching the rulebook movement semantics.

This is a deterministic mechanics kernel. Card-effect access and strategic
choice remain upstream.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from itertools import combinations
from typing import Iterable

from bench_capacity_transition import BenchOccupant, resolve_capacity_transition
from lock_state_kernel import (
    PokemonState,
    clear_attack_effects_on_position_or_evolution_change,
)


@dataclass(frozen=True)
class EnergyAttachment:
    instance_id: str
    card_name: str
    units: tuple[str, ...]
    print_id: str | None = None

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("Energy instance_id must be non-empty")
        if not self.units:
            raise ValueError("Energy attachment must provide at least one unit")


@dataclass(frozen=True)
class ToolAttachment:
    instance_id: str
    card_name: str
    print_id: str | None = None

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("Tool instance_id must be non-empty")


@dataclass(frozen=True)
class BoardPokemon:
    object_id: str
    card_name: str
    print_id: str | None = None
    abilities_enabled: bool = True
    tags: frozenset[str] = frozenset()
    energy: tuple[EnergyAttachment, ...] = ()
    tool: ToolAttachment | None = None
    pokemon_state: PokemonState = field(default_factory=PokemonState)
    damage_counters: int = 0
    special_conditions: frozenset[str] = frozenset()
    retention_value: float = 0.0

    def __post_init__(self) -> None:
        if not self.object_id:
            raise ValueError("object_id must be non-empty")
        if self.damage_counters < 0:
            raise ValueError("damage_counters must be non-negative")
        if self.retention_value < 0:
            raise ValueError("retention_value must be non-negative")
        if self.pokemon_state.tool_attached != (self.tool is not None):
            raise ValueError("PokemonState.tool_attached must match tool presence")


@dataclass(frozen=True)
class BoardState:
    active_id: str
    bench_ids: tuple[str, ...]
    objects: tuple[BoardPokemon, ...]
    bench_capacity: int = 5
    retreat_used: bool = False

    def get(self, object_id: str) -> BoardPokemon:
        for pokemon in self.objects:
            if pokemon.object_id == object_id:
                return pokemon
        raise KeyError(object_id)

    def validate(self) -> None:
        if self.bench_capacity < 0:
            raise ValueError("bench_capacity must be non-negative")
        if len(self.bench_ids) > self.bench_capacity:
            raise ValueError("Bench occupancy exceeds capacity")

        object_ids = [pokemon.object_id for pokemon in self.objects]
        if len(object_ids) != len(set(object_ids)):
            raise ValueError("Pokemon object IDs must be unique")

        in_play_ids = {self.active_id, *self.bench_ids}
        if set(object_ids) != in_play_ids:
            raise ValueError("objects must match exactly the Active and Bench IDs")
        if self.active_id in self.bench_ids:
            raise ValueError("Active object cannot also be on the Bench")
        if len(self.bench_ids) != len(set(self.bench_ids)):
            raise ValueError("Bench IDs must be unique")

        attached_ids: list[str] = []
        for pokemon in self.objects:
            attached_ids.extend(card.instance_id for card in pokemon.energy)
            if pokemon.tool is not None:
                attached_ids.append(pokemon.tool.instance_id)
        if len(attached_ids) != len(set(attached_ids)):
            raise ValueError("attached physical card IDs must be unique")


def make_pokemon(
    object_id: str,
    card_name: str,
    *,
    print_id: str | None = None,
    abilities_enabled: bool = True,
    tags: Iterable[str] = (),
    energy: tuple[EnergyAttachment, ...] = (),
    tool: ToolAttachment | None = None,
    tool_effect_enabled: bool = True,
    temporary_attack_lock: bool = False,
    temporary_retreat_lock: bool = False,
    damage_counters: int = 0,
    special_conditions: Iterable[str] = (),
    retention_value: float = 0.0,
) -> BoardPokemon:
    return BoardPokemon(
        object_id=object_id,
        card_name=card_name,
        print_id=print_id,
        abilities_enabled=abilities_enabled,
        tags=frozenset(tags),
        energy=energy,
        tool=tool,
        pokemon_state=PokemonState(
            tool_attached=tool is not None,
            tool_effect_enabled=tool_effect_enabled,
            temporary_attack_lock=temporary_attack_lock,
            temporary_retreat_lock=temporary_retreat_lock,
        ),
        damage_counters=damage_counters,
        special_conditions=frozenset(special_conditions),
        retention_value=retention_value,
    )


def make_board(
    active: BoardPokemon,
    bench: Iterable[BoardPokemon] = (),
    *,
    bench_capacity: int = 5,
    retreat_used: bool = False,
) -> BoardState:
    bench_tuple = tuple(bench)
    state = BoardState(
        active_id=active.object_id,
        bench_ids=tuple(pokemon.object_id for pokemon in bench_tuple),
        objects=(active,) + bench_tuple,
        bench_capacity=bench_capacity,
        retreat_used=retreat_used,
    )
    state.validate()
    return state


def _replace_object(state: BoardState, pokemon: BoardPokemon) -> BoardState:
    objects = tuple(
        pokemon if row.object_id == pokemon.object_id else row
        for row in state.objects
    )
    next_state = replace(state, objects=objects)
    next_state.validate()
    return next_state


def _clear_outgoing_active_effects(pokemon: BoardPokemon) -> BoardPokemon:
    return replace(
        pokemon,
        pokemon_state=clear_attack_effects_on_position_or_evolution_change(
            pokemon.pokemon_state
        ),
        special_conditions=frozenset(),
    )


def switch_active(
    state: BoardState,
    bench_object_id: str,
) -> BoardState | None:
    """Resolve an effect-based Active/Bench switch.

    No Energy is discarded. A temporary retreat lock on the outgoing Active does
    not block this transition because retreat and switching are distinct rules.
    """

    if bench_object_id not in state.bench_ids:
        return None

    outgoing_id = state.active_id
    outgoing = _clear_outgoing_active_effects(state.get(outgoing_id))
    next_state = _replace_object(state, outgoing)

    bench_ids = tuple(
        outgoing_id if object_id == bench_object_id else object_id
        for object_id in next_state.bench_ids
    )
    next_state = replace(
        next_state,
        active_id=bench_object_id,
        bench_ids=bench_ids,
    )
    next_state.validate()
    return next_state


def legal_retreat_energy_choices(
    pokemon: BoardPokemon,
    retreat_cost: int,
) -> tuple[tuple[str, ...], ...]:
    """Enumerate exact physical Energy-card selections that can pay retreat.

    Multi-unit Energy can overfill the numeric requirement. The selected
    physical-card count cannot exceed the Retreat Cost itself.
    """

    if retreat_cost < 0:
        raise ValueError("retreat_cost must be non-negative")
    if retreat_cost == 0:
        return ((),)

    cards = pokemon.energy
    choices: list[tuple[str, ...]] = []
    for size in range(1, min(len(cards), retreat_cost) + 1):
        for indices in combinations(range(len(cards)), size):
            units = sum(len(cards[index].units) for index in indices)
            if units >= retreat_cost:
                choices.append(tuple(cards[index].instance_id for index in indices))

    return tuple(choices)


def retreat(
    state: BoardState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
) -> tuple[BoardState, tuple[EnergyAttachment, ...]] | None:
    """Perform the normal once-per-turn retreat action."""

    if state.retreat_used or bench_object_id not in state.bench_ids:
        return None

    outgoing = state.get(state.active_id)
    if outgoing.pokemon_state.temporary_retreat_lock:
        return None

    escape_board_active = (
        outgoing.tool is not None
        and outgoing.tool.card_name == "Escape Board"
        and outgoing.pokemon_state.tool_effect_enabled
    )
    if (
        outgoing.special_conditions & {"Asleep", "Paralyzed"}
        and not escape_board_active
    ):
        return None

    requested = tuple(discard_energy_ids)
    requested_set = set(requested)
    if len(requested) != len(requested_set):
        return None

    legal_sets = {
        frozenset(choice)
        for choice in legal_retreat_energy_choices(outgoing, retreat_cost)
    }
    if frozenset(requested) not in legal_sets:
        return None

    discarded = tuple(
        energy for energy in outgoing.energy
        if energy.instance_id in requested_set
    )
    remaining = tuple(
        energy for energy in outgoing.energy
        if energy.instance_id not in requested_set
    )
    moved_outgoing = replace(outgoing, energy=remaining)
    moved_outgoing = _clear_outgoing_active_effects(moved_outgoing)

    next_state = _replace_object(state, moved_outgoing)
    switched = switch_active(next_state, bench_object_id)
    assert switched is not None
    switched = replace(switched, retreat_used=True)
    switched.validate()
    return switched, discarded


def evolve(
    state: BoardState,
    object_id: str,
    *,
    new_card_name: str,
    new_tags: Iterable[str] | None = None,
) -> BoardState | None:
    """Replace the top card identity while preserving persistent board state."""

    try:
        pokemon = state.get(object_id)
    except KeyError:
        return None

    evolved = replace(
        pokemon,
        card_name=new_card_name,
        tags=(
            frozenset(new_tags)
            if new_tags is not None
            else pokemon.tags
        ),
        pokemon_state=clear_attack_effects_on_position_or_evolution_change(
            pokemon.pokemon_state
        ),
        special_conditions=frozenset(),
    )
    return _replace_object(state, evolved)


def contract_bench(
    state: BoardState,
    *,
    new_capacity: int,
) -> tuple[BoardState, tuple[BoardPokemon, ...]]:
    """Apply a maximum-retention Bench contraction to full Pokemon objects."""

    if new_capacity < 0:
        raise ValueError("new_capacity must be non-negative")
    if len(state.bench_ids) <= new_capacity:
        next_state = replace(state, bench_capacity=new_capacity)
        next_state.validate()
        return next_state, ()

    bench_objects = tuple(state.get(object_id) for object_id in state.bench_ids)
    occupants = tuple(
        BenchOccupant(
            name=pokemon.object_id,
            role=pokemon.card_name,
            retention_value=pokemon.retention_value,
        )
        for pokemon in bench_objects
    )
    transition = resolve_capacity_transition(
        occupants,
        old_capacity=max(state.bench_capacity, len(bench_objects)),
        new_capacity=new_capacity,
    )
    retained_ids = {row.name for row in transition.retained}
    discarded_ids = {
        row.name for row in transition.discarded
    }

    discarded = tuple(
        pokemon for pokemon in bench_objects
        if pokemon.object_id in discarded_ids
    )
    next_state = replace(
        state,
        bench_ids=tuple(
            object_id for object_id in state.bench_ids
            if object_id in retained_ids
        ),
        objects=tuple(
            pokemon for pokemon in state.objects
            if pokemon.object_id not in discarded_ids
        ),
        bench_capacity=new_capacity,
    )
    next_state.validate()
    return next_state, discarded


def next_turn(state: BoardState) -> BoardState:
    next_state = replace(state, retreat_used=False)
    next_state.validate()
    return next_state


def knock_out(
    state: BoardState,
    object_id: str,
    *,
    promote_object_id: str | None = None,
) -> tuple[BoardState | None, BoardPokemon] | None:
    """Remove one Knocked Out Pokemon and return the complete removed object.

    If the Active Pokemon is Knocked Out while a Bench remains, a valid
    promotion must be supplied. If no Benched Pokemon remains, the returned
    BoardState is None to represent the terminal no-Pokemon board without
    constructing an invalid BoardState.

    Knock Out triggers, Prize taking, simultaneous Knock Outs, and win/loss
    resolution remain outside this mechanical board-object transition.
    """

    try:
        knocked_out = state.get(object_id)
    except KeyError:
        return None

    remaining_objects = tuple(
        pokemon
        for pokemon in state.objects
        if pokemon.object_id != object_id
    )

    if object_id == state.active_id:
        if not state.bench_ids:
            if promote_object_id is not None:
                return None
            return None, knocked_out

        if promote_object_id not in state.bench_ids:
            return None

        next_state = BoardState(
            active_id=promote_object_id,
            bench_ids=tuple(
                bench_id
                for bench_id in state.bench_ids
                if bench_id != promote_object_id
            ),
            objects=remaining_objects,
            bench_capacity=state.bench_capacity,
            retreat_used=state.retreat_used,
        )
        next_state.validate()
        return next_state, knocked_out

    if promote_object_id is not None:
        return None
    if object_id not in state.bench_ids:
        return None

    next_state = BoardState(
        active_id=state.active_id,
        bench_ids=tuple(
            bench_id
            for bench_id in state.bench_ids
            if bench_id != object_id
        ),
        objects=remaining_objects,
        bench_capacity=state.bench_capacity,
        retreat_used=state.retreat_used,
    )
    next_state.validate()
    return next_state, knocked_out


def move_energy_between_pokemon(
    state: BoardState,
    instance_id: str,
    *,
    source_object_id: str,
    target_object_id: str,
) -> BoardState | None:
    """Move one physical Energy attachment between two in-play Pokemon."""

    if source_object_id == target_object_id:
        return None
    try:
        source = state.get(source_object_id)
        target = state.get(target_object_id)
    except KeyError:
        return None

    matches = tuple(
        energy
        for energy in source.energy
        if energy.instance_id == instance_id
    )
    if len(matches) != 1:
        return None
    moved = matches[0]

    next_source = replace(
        source,
        energy=tuple(
            energy
            for energy in source.energy
            if energy.instance_id != instance_id
        ),
    )
    next_target = replace(
        target,
        energy=target.energy + (moved,),
    )
    next_state = replace(
        state,
        objects=tuple(
            next_source
            if row.object_id == source_object_id
            else next_target
            if row.object_id == target_object_id
            else row
            for row in state.objects
        ),
    )
    next_state.validate()
    return next_state
