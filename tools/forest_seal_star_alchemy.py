"""Physical Forest Seal Stone -> Star Alchemy search transaction.

This narrow card-specific bridge represents the mechanics required by Forest
Seal Stone in the current paper rules:
- the Tool must be played from hand onto a Pokemon with no Tool;
- Tool play uses the Tool channel rather than the Item channel;
- Star Alchemy is available only from a Pokemon V holding an effective Forest
  Seal Stone and able to use Abilities;
- the once-per-game VSTAR Power budget must still be unused;
- Star Alchemy searches exactly one requested deck card into hand.

The bridge preserves physical card counts in ZoneCountState and the board
object's Tool attachment. Shuffle order is intentionally outside this state
because callers here reason only about card identity access.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from board_object_kernel import (
    BoardPokemon,
    BoardState,
    ToolAttachment,
)
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from trainer_search_transaction import TrainerSearchExecutionState
from turn_action_budget import TurnActionBudget


FOREST_SEAL_STONE_NAME = "Forest Seal Stone"


@dataclass(frozen=True)
class ForestSealSearchState:
    zones: ZoneCountState
    board: BoardState
    budget: TurnActionBudget = field(default_factory=TurnActionBudget)
    channels: PlayerChannels = field(default_factory=PlayerChannels)
    vstar_power_used: bool = False


def _replace_pokemon(board: BoardState, pokemon: BoardPokemon) -> BoardState:
    next_board = replace(
        board,
        objects=tuple(
            pokemon if row.object_id == pokemon.object_id else row
            for row in board.objects
        ),
    )
    next_board.validate()
    return next_board


def attach_forest_seal_stone(
    state: ForestSealSearchState,
    *,
    holder_object_id: str,
    tool_card_class: str = "forest_seal_stone",
    tool_instance_id: str = "forest-seal-stone-1",
) -> ForestSealSearchState:
    """Attach Forest Seal Stone from hand through the Tool-play channel."""

    if not state.channels.tool_play:
        raise ValueError("Pokemon Tool play is locked")
    if state.zones.count(tool_card_class, "hand") < 1:
        raise ValueError("Forest Seal Stone is not in hand")

    try:
        holder = state.board.get(holder_object_id)
    except KeyError as exc:
        raise ValueError("Tool holder is not in play") from exc
    if holder.tool is not None:
        raise ValueError("Pokemon already has a Pokemon Tool attached")

    tool = ToolAttachment(
        instance_id=tool_instance_id,
        card_name=FOREST_SEAL_STONE_NAME,
        print_id="swsh12-156",
    )
    next_holder = replace(
        holder,
        tool=tool,
        pokemon_state=replace(holder.pokemon_state, tool_attached=True),
    )
    next_board = _replace_pokemon(state.board, next_holder)
    next_zones = state.zones.move(tool_card_class, "hand", "attached")

    if state.zones.total(tool_card_class) != next_zones.total(tool_card_class):
        raise AssertionError("Forest Seal Stone card total changed")

    return replace(
        state,
        zones=next_zones,
        board=next_board,
    )


def use_star_alchemy(
    state: ForestSealSearchState,
    *,
    holder_object_id: str,
    target_card_class: str,
) -> ForestSealSearchState:
    """Use Star Alchemy once to move one exact requested deck card to hand."""

    if state.vstar_power_used:
        raise ValueError("VSTAR Power has already been used this game")

    try:
        holder = state.board.get(holder_object_id)
    except KeyError as exc:
        raise ValueError("Star Alchemy holder is not in play") from exc

    if "V" not in holder.tags:
        raise ValueError("Forest Seal Stone grants Star Alchemy only to Pokemon V")
    if holder.tool is None or holder.tool.card_name != FOREST_SEAL_STONE_NAME:
        raise ValueError("Pokemon V does not have Forest Seal Stone attached")
    if not holder.pokemon_state.tool_effect_enabled:
        raise ValueError("Forest Seal Stone has no effect")
    if not holder.abilities_enabled:
        raise ValueError("Pokemon V cannot use the granted Ability")
    if state.zones.count(target_card_class, "deck") < 1:
        raise ValueError("requested Star Alchemy target is not in deck")

    next_zones = state.zones.move(target_card_class, "deck", "hand")
    if state.zones.total(target_card_class) != next_zones.total(target_card_class):
        raise AssertionError("Star Alchemy target card total changed")

    return replace(
        state,
        zones=next_zones,
        vstar_power_used=True,
    )


def as_trainer_execution_state(
    state: ForestSealSearchState,
) -> TrainerSearchExecutionState:
    """Project shared zones/budget/channels for downstream Trainer execution."""

    return TrainerSearchExecutionState(
        zones=state.zones,
        budget=state.budget,
        channels=state.channels,
    )
