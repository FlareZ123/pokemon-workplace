"""Compose direct-evolution profiles with generic source-action permissions."""

from __future__ import annotations

from dataclasses import dataclass, field

from tools.board_position_state import BoardState, PokemonCard
from tools.effect_evolution_execution import effect_evolve
from tools.effect_evolution_timing import EvolutionEffectProfile
from tools.lock_state_kernel import PlayerChannels
from tools.stadium_effect_instance_usage import (
    StadiumEffectState,
    can_use_current_stadium_effect,
    use_current_stadium_effect,
)
from turn_action_budget import TurnAction, TurnActionBudget
from tools.turn_attack_window import (
    TurnExecutionWindow,
    can_take_action,
    consume_action,
    fresh_turn,
)


@dataclass(frozen=True)
class SourceActionContext:
    is_players_first_turn: bool
    went_first: bool
    window: TurnExecutionWindow = field(default_factory=fresh_turn)
    channels: PlayerChannels = PlayerChannels()
    abilities_allowed: bool = True
    attacks_allowed: bool = True
    attacker_object_id: str | None = None
    stadium_state: StadiumEffectState | None = None

    @property
    def budget(self) -> TurnActionBudget:
        return self.window.action_budget


@dataclass(frozen=True)
class SourceGatedEvolution:
    board: BoardState
    window: TurnExecutionWindow
    stadium_state: StadiumEffectState | None = None

    @property
    def budget(self) -> TurnActionBudget:
        return self.window.action_budget


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

    if context.window.attack_phase.turn_ended or not _first_turn_source_open(profile, context):
        return False

    channel = profile.source_channel
    if channel == "attack":
        return (
            context.attacks_allowed
            and context.attacker_object_id is not None
            and can_take_action(
                context.window,
                TurnAction.ATTACK,
                attacker_object_id=context.attacker_object_id,
            )
        )

    if not context.window.attack_phase.ordinary_actions_open:
        return False
    if channel == "ability":
        return context.abilities_allowed
    if channel == "item":
        return context.channels.item_play
    if channel == "supporter":
        return (
            context.channels.supporter_play
            and can_take_action(context.window, TurnAction.SUPPORTER)
        )
    if channel == "stadium":
        stadium = context.stadium_state
        return (
            stadium is not None
            and stadium.in_play is not None
            and stadium.in_play.card.name == profile.card_name
            and can_use_current_stadium_effect(stadium)
        )
    return False


def consume_source_action(
    profile: EvolutionEffectProfile,
    context: SourceActionContext,
) -> TurnExecutionWindow | None:
    """Consume only the generic action owned by the represented source channel."""

    if not source_action_available(profile, context):
        return None

    channel = profile.source_channel
    if channel == "attack":
        assert context.attacker_object_id is not None
        return consume_action(
            context.window,
            TurnAction.ATTACK,
            attacker_object_id=context.attacker_object_id,
        )
    if channel == "supporter":
        return consume_action(context.window, TurnAction.SUPPORTER)
    if channel == "stadium":
        # The in-play effect-use allowance is separate from Stadium play.
        return context.window
    return context.window


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

    next_window = consume_source_action(profile, context)
    if next_window is None:
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

    stadium_state = context.stadium_state
    if profile.source_channel == "stadium":
        assert stadium_state is not None
        stadium_state = use_current_stadium_effect(stadium_state)
        assert stadium_state is not None

    return SourceGatedEvolution(transition.state, next_window, stadium_state)
