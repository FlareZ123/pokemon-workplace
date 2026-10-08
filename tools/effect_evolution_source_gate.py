"""Compose direct-evolution profiles with generic source-action permissions."""

from __future__ import annotations

from dataclasses import dataclass

from tools.effect_evolution_execution import effect_evolve
from tools.effect_evolution_timing import EvolutionEffectProfile
from tools.board_position_state import BoardState, PokemonCard
from tools.lock_state_kernel import PlayerChannels
from tools.turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class SourceActionContext:
    is_players_first_turn: bool
    went_first: bool
    budget: TurnActionBudget = TurnActionBudget()
    channels: PlayerChannels = PlayerChannels()
    abilities_allowed: bool = True
    attacks_allowed: bool = True


@dataclass(frozen=True)
class SourceGatedEvolution:
    board: BoardState
    budget: TurnActionBudget


def _first_turn_source_open(
    profile: EvolutionEffectProfile,
    context: SourceActionContext,
) -> bool:
    if not context.is_players_first_turn or not context.went_first:
        return True
    return profile.intrinsic_source_window == "both"


def source_action_available(
    profile: EvolutionEffectProfile,
    context: SourceActionContext,
) -> bool:
    """Check generic source permissions without resolving card-specific costs."""

    if context.budget.turn_ended or not _first_turn_source_open(profile, context):
        return False

    channel = profile.source_channel
    if channel == "attack":
        return context.attacks_allowed and context.budget.can(TurnAction.ATTACK)
    if channel == "ability":
        return context.abilities_allowed
    if channel == "item":
        return context.channels.item_play
    if channel == "supporter":
        return (
            context.channels.supporter_play
            and context.budget.can(TurnAction.SUPPORTER)
        )
    if channel == "stadium":
        return (
            context.channels.stadium_play
            and context.budget.can(TurnAction.STADIUM_PLAY)
        )
    return False


def consume_source_action(
    profile: EvolutionEffectProfile,
    context: SourceActionContext,
) -> TurnActionBudget | None:
    """Consume only the generic quota owned by the represented source channel."""

    if not source_action_available(profile, context):
        return None

    channel = profile.source_channel
    if channel == "attack":
        return context.budget.consume(TurnAction.ATTACK)
    if channel == "supporter":
        return context.budget.consume(TurnAction.SUPPORTER)
    if channel == "stadium":
        return context.budget.consume(TurnAction.STADIUM_PLAY)
    return context.budget


def execute_source_gated_evolution(
    profile: EvolutionEffectProfile,
    context: SourceActionContext,
    board: BoardState,
    pokemon_id: str,
    evolution_card: PokemonCard,
    *,
    new_retreat_cost: int,
) -> SourceGatedEvolution | None:
    """Atomically compose the generic source gate with C-12 board evolution."""

    next_budget = consume_source_action(profile, context)
    if next_budget is None:
        return None

    transition = effect_evolve(
        board,
        pokemon_id,
        evolution_card,
        new_retreat_cost=new_retreat_cost,
        first_turn_policy=profile.timing_policy,
        entry_turn_policy=profile.entry_turn_policy,
        source_available=True,
    )
    if transition is None:
        return None

    return SourceGatedEvolution(transition.state, next_budget)
