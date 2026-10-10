"""Join physical Stadium-entry semantics to Grand Tree voluntary activation.

This is a deliberately narrow witness: Gothitelle's Teleport Room selects a
Grand Tree previously in discard, then Grand Tree may perform one Stage 1
evolution without spending the Stadium-play allowance.

StadiumEntryState is the sole owner of Stadium card zones and turn budget.
A StadiumEffectState is a transient projection for the evolution source gate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from tools.board_position_state import BoardState, PokemonCard
from tools.effect_evolution_source_gate import SourceActionContext
from tools.effect_evolution_timing import EvolutionEffectProfile
from tools.grand_tree_chain_execution import execute_grand_tree_chain
from tools.stadium_effect_instance_usage import (
    StadiumCard,
    StadiumEffectState,
    StadiumInPlay,
)
from tools.stadium_entry_channels import StadiumEntryState, use_teleport_room
from tools.turn_attack_window import fresh_turn


@dataclass(frozen=True)
class TeleportGrandTreeState:
    entry: StadiumEntryState
    epoch: int = 0
    used_effect_instances: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if self.epoch < 0:
            raise ValueError("Stadium entry epoch must be nonnegative")

    def effect_view(self) -> StadiumEffectState:
        """Project live Stadium card state without duplicating zone ownership."""
        current = self.entry.in_play
        in_play = (
            StadiumInPlay(
                StadiumCard(current.copy_id, current.name),
                f"{current.copy_id}@{self.epoch}",
            )
            if current is not None
            else None
        )
        return StadiumEffectState(
            budget=self.entry.budget,
            in_play=in_play,
            used_effect_instances=self.used_effect_instances,
        )


@dataclass(frozen=True)
class TeleportGrandTreeResult:
    state: TeleportGrandTreeState
    board: BoardState


def teleport_grand_tree_from_discard(
    state: TeleportGrandTreeState,
    *,
    gothitelle_source_id: str,
    grand_tree_copy_id: str,
) -> TeleportGrandTreeState | None:
    """Effect-place the Grand Tree copy after discarding another Stadium."""

    found = next(
        (card for card in state.entry.discard if card.copy_id == grand_tree_copy_id),
        None,
    )
    if found is None or found.name != "Grand Tree":
        return None

    next_entry = use_teleport_room(
        state.entry, gothitelle_source_id, grand_tree_copy_id
    )
    if next_entry is None:
        return None
    if next_entry.in_play is None or next_entry.in_play.name != "Grand Tree":
        return None
    return replace(state, entry=next_entry, epoch=state.epoch + 1)


def activate_teleported_grand_tree(
    state: TeleportGrandTreeState,
    profile: EvolutionEffectProfile,
    board: BoardState,
    pokemon_id: str,
    stage1: PokemonCard,
    *,
    stage1_retreat_cost: int,
    went_first: bool,
    stage2: PokemonCard | None = None,
    stage2_retreat_cost: int | None = None,
) -> TeleportGrandTreeResult | None:
    """Activate in-play Grand Tree after effect placement, once in this turn."""

    if state.entry.budget.turn_ended:
        return None
    stadium = state.effect_view()
    context = SourceActionContext(
        is_players_first_turn=False,
        went_first=went_first,
        window=fresh_turn(action_budget=state.entry.budget),
        stadium_state=stadium,
    )
    transition = execute_grand_tree_chain(
        profile,
        context,
        board,
        pokemon_id,
        stage1,
        stage1_retreat_cost=stage1_retreat_cost,
        stage2=stage2,
        stage2_retreat_cost=stage2_retreat_cost,
    )
    if transition is None:
        return None
    assert transition.stadium_state is not None
    assert transition.budget == state.entry.budget

    return TeleportGrandTreeResult(
        replace(
            state,
            used_effect_instances=transition.stadium_state.used_effect_instances,
        ),
        transition.board,
    )
