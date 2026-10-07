"""Beginning-of-turn deck-loss check followed by one physical draw."""

from __future__ import annotations

from dataclasses import dataclass

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from physical_start_of_turn_resolution import resolve_physical_start_of_turn_deck_out
from post_knockout_game_resolution import Outcome, Resolution
from top_prize_physical_bridge import TopPrizePhysicalState
from turn_start_deck_loss import (
    resolve_exact_top_turn_start_draw,
    resolve_sampled_turn_start_draw,
)


@dataclass(frozen=True)
class TurnStartPhaseResult:
    resolution: Resolution
    after_draw: SearchableDeckPhysicalState | None
    drawn_instance_id: str | None

    @property
    def terminal(self) -> bool:
        return self.resolution.terminal


def begin_turn_with_exact_top(
    state: TopPrizePhysicalState,
    *,
    player_ids: tuple[str, str],
    current_turn_player: str,
) -> TurnStartPhaseResult:
    """Resolve deck-out timing, then draw the exact materialized top card."""

    resolution = resolve_physical_start_of_turn_deck_out(
        player_ids=player_ids,
        current_turn_player=current_turn_player,
        current_turn_player_ledger=state.ledger,
    )
    if resolution.terminal:
        return TurnStartPhaseResult(resolution, None, None)

    draw = resolve_exact_top_turn_start_draw(state)
    if draw is None:
        raise AssertionError("nonterminal exact-top state must have a drawable card")
    return TurnStartPhaseResult(
        resolution,
        draw.after,
        draw.draw.drawn_instance_id,
    )


def begin_turn_with_sampled_draw(
    state: SearchableDeckPhysicalState,
    *,
    player_ids: tuple[str, str],
    current_turn_player: str,
    card_class: str | None = None,
    card_name: str | None = None,
    instance_id: str | None = None,
) -> TurnStartPhaseResult:
    """Resolve deck-out timing, then draw one supplied sample if nonterminal."""

    resolution = resolve_physical_start_of_turn_deck_out(
        player_ids=player_ids,
        current_turn_player=current_turn_player,
        current_turn_player_ledger=state.ledger,
    )
    if resolution.terminal:
        return TurnStartPhaseResult(resolution, None, None)

    if card_class is None or card_name is None or instance_id is None:
        raise ValueError("a sampled card is required for a nonempty unordered deck")

    draw = resolve_sampled_turn_start_draw(
        state,
        card_class=card_class,
        card_name=card_name,
        instance_id=instance_id,
    )
    if draw is None:
        raise AssertionError("nonterminal unordered deck must have a drawable card")
    return TurnStartPhaseResult(
        resolution,
        draw.after,
        draw.drawn_instance_id,
    )


def player_continues(result: TurnStartPhaseResult, player_id: str) -> bool:
    """Return whether one player's outcome remains CONTINUE after the check."""

    return result.resolution.outcome(player_id) == Outcome.CONTINUE
