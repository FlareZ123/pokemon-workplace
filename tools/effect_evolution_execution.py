"""Execute C-12 effect-based evolution on conserved physical Pokémon state."""

from __future__ import annotations

from dataclasses import dataclass, replace

from tools.board_position_state import (
    BoardPokemon,
    BoardState,
    BoardTransition,
    PokemonCard,
    replace_pokemon,
)
from tools.effect_evolution_timing import TimingPolicy
from tools.identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
    validate_board_position_stack_bindings,
)
from tools.lock_state_kernel import clear_attack_effects_on_position_or_evolution_change


@dataclass(frozen=True)
class MaterializedEffectEvolution:
    board: BoardState
    ledger: IdentityLedger


def _policy_allows_bypass(policy: TimingPolicy) -> bool:
    return policy in {"c12_default_permitted", "explicit_permitted"}


def effect_evolve(
    state: BoardState,
    pokemon_id: str,
    evolution_card: PokemonCard,
    *,
    new_retreat_cost: int,
    first_turn_policy: TimingPolicy,
    entry_turn_policy: TimingPolicy,
    source_available: bool = True,
) -> BoardTransition | None:
    """Resolve one effect-based evolution after source-action legality is known.

    ``state.evolution_allowed`` represents the ordinary player-first-turn gate.
    ``pokemon.evolution_eligible`` represents the ordinary target-entry-turn gate.
    C-12 may bypass either gate independently unless the effect text overrides it.
    The caller supplies ``source_available`` because attack, Supporter, lock, and
    other source-action legality belongs to a separate execution layer.
    """

    if not source_available or new_retreat_cost < 0:
        return None

    try:
        pokemon = state.get(pokemon_id)
    except StopIteration:
        return None

    if not state.evolution_allowed and not _policy_allows_bypass(first_turn_policy):
        return None
    if not pokemon.evolution_eligible and not _policy_allows_bypass(entry_turn_policy):
        return None
    if evolution_card.evolves_from != pokemon.name:
        return None

    evolved: BoardPokemon = replace(
        pokemon,
        stack=pokemon.stack + (evolution_card,),
        retreat_cost=new_retreat_cost,
        evolution_eligible=False,
    )
    if pokemon_id == state.active_id:
        evolved = replace(
            evolved,
            combat=clear_attack_effects_on_position_or_evolution_change(evolved.combat),
            special_conditions=frozenset(),
        )

    return BoardTransition(replace_pokemon(state, evolved))


def materialized_effect_evolve(
    ledger: IdentityLedger,
    state: BoardState,
    pokemon_id: str,
    evolution_card: PokemonCard,
    *,
    card_class: str,
    source_zone: str,
    new_retreat_cost: int,
    first_turn_policy: TimingPolicy,
    entry_turn_policy: TimingPolicy,
    source_available: bool = True,
) -> MaterializedEffectEvolution | None:
    """Atomically materialize an Evolution card and execute the C-12 transition."""

    try:
        staged_ledger = materialize(
            ledger,
            card_class=card_class,
            card_name=evolution_card.name,
            source_zone=source_zone,
            instance_id=evolution_card.card_id,
        )
        staged_ledger = put_in_play_instance(
            staged_ledger,
            evolution_card.card_id,
            pokemon_id,
        )
    except (KeyError, ValueError):
        return None

    transition = effect_evolve(
        state,
        pokemon_id,
        evolution_card,
        new_retreat_cost=new_retreat_cost,
        first_turn_policy=first_turn_policy,
        entry_turn_policy=entry_turn_policy,
        source_available=source_available,
    )
    if transition is None:
        return None

    validate_board_position_stack_bindings(staged_ledger, transition.state)
    assert_conserved(ledger, staged_ledger)
    return MaterializedEffectEvolution(transition.state, staged_ledger)
