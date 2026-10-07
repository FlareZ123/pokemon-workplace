"""Physical position and ordinary evolution transitions for Expanded."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from lock_state_kernel import clear_attack_effects_on_position_or_evolution_change
from board_position_state import (
    Attachment, AttachmentKind, BoardPokemon, BoardState, BoardTransition, PokemonCard,
    clear_for_bench, replace_pokemon, validate_state,
)


def _swap(state: BoardState, promote_id: str, *, consume_retreat: bool) -> BoardState | None:
    if promote_id == state.active_id or promote_id not in state.bench_ids:
        return None
    state = replace_pokemon(state, clear_for_bench(state.get(state.active_id)))
    state = replace(state, active_id=promote_id, retreat_used=state.retreat_used or consume_retreat)
    validate_state(state)
    return state


def switch_active(state: BoardState, promote_id: str) -> BoardTransition | None:
    next_state = _swap(state, promote_id, consume_retreat=False)
    return None if next_state is None else BoardTransition(next_state)


def _valid_retreat_payment(selected: tuple[Attachment, ...], cost: int) -> bool:
    """Validate the exact physical Energy cards selected for a Retreat Cost."""

    if cost == 0:
        return not selected
    return (
        bool(selected)
        and len(selected) <= cost
        and all(card.retreat_units > 0 for card in selected)
        and sum(card.retreat_units for card in selected) >= cost
    )


def normal_retreat(
    state: BoardState, promote_id: str, *, discard_energy_ids: Iterable[str] = (),
) -> BoardTransition | None:
    if state.retreat_used or promote_id not in state.bench_ids:
        return None
    active = state.get(state.active_id)
    if active.combat.temporary_retreat_lock:
        return None

    escape_board_active = (
        active.combat.tool_effect_enabled
        and any(
            card.kind == AttachmentKind.TOOL and card.name == "Escape Board"
            for card in active.attachments
        )
    )
    if (
        active.special_conditions & {"Asleep", "Paralyzed"}
        and not escape_board_active
    ):
        return None
    selected_ids = tuple(discard_energy_ids)
    if len(selected_ids) != len(set(selected_ids)):
        return None
    by_id = {card.card_id: card for card in active.attachments}
    if any(card_id not in by_id for card_id in selected_ids):
        return None
    selected = tuple(by_id[card_id] for card_id in selected_ids)
    if any(card.kind != AttachmentKind.ENERGY for card in selected):
        return None
    if not _valid_retreat_payment(selected, active.retreat_cost):
        return None
    discarded = frozenset(selected_ids)
    paid = replace(active, attachments=tuple(
        card for card in active.attachments if card.card_id not in discarded
    ))
    paid = replace(paid, combat=replace(
        paid.combat,
        tool_attached=any(card.kind == AttachmentKind.TOOL for card in paid.attachments),
    ))
    next_state = _swap(replace_pokemon(state, paid), promote_id, consume_retreat=True)
    return None if next_state is None else BoardTransition(next_state, selected_ids)


def normal_evolve(
    state: BoardState, pokemon_id: str, evolution_card: PokemonCard, *, new_retreat_cost: int,
) -> BoardTransition | None:
    if not state.evolution_allowed or new_retreat_cost < 0:
        return None
    pokemon = state.get(pokemon_id)
    if not pokemon.evolution_eligible or evolution_card.evolves_from != pokemon.name:
        return None
    evolved = replace(
        pokemon, stack=pokemon.stack + (evolution_card,), retreat_cost=new_retreat_cost,
        evolution_eligible=False,
    )
    if pokemon_id == state.active_id:
        evolved = replace(
            evolved,
            combat=clear_attack_effects_on_position_or_evolution_change(evolved.combat),
            special_conditions=frozenset(),
        )
    return BoardTransition(replace_pokemon(state, evolved))


def begin_next_turn(state: BoardState) -> BoardState:
    state = replace(
        state, pokemon=tuple(replace(p, evolution_eligible=True) for p in state.pokemon),
        retreat_used=False, evolution_allowed=True,
    )
    validate_state(state)
    return state


def devolve_top(
    state: BoardState,
    pokemon_id: str,
    *,
    new_retreat_cost: int,
) -> tuple[BoardState, PokemonCard] | None:
    """Remove the highest Evolution card while preserving the Pokemon object."""

    if new_retreat_cost < 0:
        return None
    pokemon = state.get(pokemon_id)
    if len(pokemon.stack) < 2:
        return None

    removed = pokemon.stack[-1]
    devolved = replace(
        pokemon,
        stack=pokemon.stack[:-1],
        retreat_cost=new_retreat_cost,
        evolution_eligible=False,
        combat=clear_attack_effects_on_position_or_evolution_change(
            pokemon.combat
        ),
        special_conditions=frozenset(),
    )
    next_state = replace_pokemon(state, devolved)
    return next_state, removed
