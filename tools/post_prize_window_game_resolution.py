"""Resolve terminal game state only after the E-31 Prize window closes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from before_hand_prize_executor import RESOLVING_TRAINER_ZONE
from post_knockout_game_resolution import Resolution, resolve_prize_and_board_loss_conditions
from promotion_pending_conservation import (
    PostKnockOutPromotionContext,
    PostKnockOutStage,
    unresolved_prize_count,
)


@dataclass(frozen=True)
class PrizeWindowResolution:
    context: PostKnockOutPromotionContext
    resolution: Resolution


def unresolved_prize_window_count(
    context: PostKnockOutPromotionContext,
) -> int:
    """Count cards whose before-hand Prize work has not finished."""

    total = unresolved_prize_count(context)
    for _player_id, state in context.players:
        total += sum(
            row.zone == RESOLVING_TRAINER_ZONE
            for row in state.ledger.instances
        )
        total += sum(
            count
            for _card_class, zone, count in state.ledger.exchangeable.counts
            if zone == RESOLVING_TRAINER_ZONE
        )
    return total


def resolve_after_prize_window(
    context: PostKnockOutPromotionContext,
    *,
    prizes_remaining: Mapping[str, int],
) -> PrizeWindowResolution | None:
    """Resolve Prize/no-Pokemon loss conditions after all E-31 effects finish.

    Returns None while any Prize card is still pending. If the game continues,
    the context advances to the promotion phase. If the game is terminal, it
    advances to the terminal phase.
    """

    if context.stage != PostKnockOutStage.PRIZES:
        return None
    if unresolved_prize_window_count(context):
        return None

    player_ids = tuple(player_id for player_id, _state in context.players)
    if len(player_ids) != 2:
        raise ValueError("exactly two players are required")
    if set(prizes_remaining) != set(player_ids):
        raise ValueError("prizes_remaining must contain exactly both players")

    pokemon_in_play = {
        player_id: len(state.pokemon)
        for player_id, state in context.players
    }
    resolution = resolve_prize_and_board_loss_conditions(
        player_ids=(player_ids[0], player_ids[1]),
        prizes_remaining=prizes_remaining,
        pokemon_in_play=pokemon_in_play,
    )

    next_stage = (
        PostKnockOutStage.TERMINAL
        if resolution.terminal
        else PostKnockOutStage.PROMOTION
    )
    return PrizeWindowResolution(
        replace(context, stage=next_stage),
        resolution,
    )
