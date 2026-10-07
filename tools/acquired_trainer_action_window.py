"""Evaluate the action-window status of Trainer cards already acquired to hand.

This is deliberately a narrow bridge. It answers whether the generic play channel
and turn quota needed by a Trainer subtype remain available. Card-specific play
conditions, targets, and effects remain downstream responsibilities.
"""

from __future__ import annotations

from dataclasses import dataclass

from trainer_search_transaction import TrainerSearchExecutionState
from turn_action_budget import TurnAction


@dataclass(frozen=True)
class AcquiredTrainerActionWindow:
    """Generic hand/action-window prerequisites for one acquired Trainer."""

    card_class: str
    action_class: str
    copies_in_hand: int
    channel_open: bool
    quota_remaining: int | None
    window_available: bool


def evaluate_acquired_trainer_action_window(
    state: TrainerSearchExecutionState,
    *,
    card_class: str,
    action_class: str,
) -> AcquiredTrainerActionWindow:
    """Return whether a hand-held Trainer still has its generic action window.

    ``window_available`` is necessary for later execution, not sufficient for
    full card legality. For example, a Stadium may still fail a same-name check,
    and a Pokémon Tool may still lack a legal attachment target.
    """

    if not card_class:
        raise ValueError("card_class must be non-empty")

    copies_in_hand = state.zones.count(card_class, "hand")

    if action_class == "Item":
        channel_open = state.channels.item_play
        quota_remaining = None
    elif action_class == "Pokémon Tool":
        channel_open = state.channels.tool_play
        quota_remaining = None
    elif action_class == "Supporter":
        channel_open = state.channels.supporter_play
        quota_remaining = state.budget.remaining(TurnAction.SUPPORTER)
    elif action_class == "Stadium":
        channel_open = state.channels.stadium_play
        quota_remaining = state.budget.remaining(TurnAction.STADIUM_PLAY)
    else:
        raise ValueError(
            f"unsupported Trainer action class: {action_class!r}"
        )

    quota_open = quota_remaining is None or quota_remaining > 0
    return AcquiredTrainerActionWindow(
        card_class=card_class,
        action_class=action_class,
        copies_in_hand=copies_in_hand,
        channel_open=channel_open,
        quota_remaining=quota_remaining,
        window_available=(
            copies_in_hand > 0
            and channel_open
            and quota_open
        ),
    )
