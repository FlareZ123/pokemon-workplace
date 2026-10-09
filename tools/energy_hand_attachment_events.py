"""Physical Energy-from-hand events separated from manual attachment quota."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from next_turn_attachment_window import NextTurnAttachmentWindow
from turn_action_budget import TurnAction, TurnActionBudget


class AttachmentChannel(str, Enum):
    MANUAL = "manual"
    EFFECT = "effect"


@dataclass(frozen=True)
class EnergyCard:
    copy_id: str
    name: str


@dataclass(frozen=True)
class EnergyAttachmentEvent:
    copy_id: str
    card_name: str
    player: str
    target_id: str
    source_zone: str
    channel: AttachmentChannel


@dataclass(frozen=True)
class EnergyAttachmentState:
    budget: TurnActionBudget
    hand: tuple[EnergyCard, ...] = ()
    attached: tuple[tuple[str, EnergyCard], ...] = ()
    events: tuple[EnergyAttachmentEvent, ...] = ()


def attach_from_hand(
    state: EnergyAttachmentState,
    selections: tuple[tuple[str, str], ...],
    *,
    player: str,
    channel: AttachmentChannel,
    manual_window: NextTurnAttachmentWindow | None = None,
) -> EnergyAttachmentState | None:
    if not selections:
        return None
    if channel is AttachmentChannel.MANUAL and len(selections) != 1:
        return None

    budget = state.budget
    if channel is AttachmentChannel.MANUAL:
        budget = (
            manual_window.consume_manual_attachment(player, budget)
            if manual_window is not None
            else budget.consume(TurnAction.MANUAL_ENERGY_ATTACHMENT)
        )
        if budget is None:
            return None

    requested = [copy_id for copy_id, _target in selections]
    if len(requested) != len(set(requested)):
        return None
    by_id = {card.copy_id: card for card in state.hand}
    if any(copy_id not in by_id for copy_id in requested):
        return None

    requested_set = set(requested)
    hand = tuple(card for card in state.hand if card.copy_id not in requested_set)
    attached = list(state.attached)
    events = list(state.events)
    for copy_id, target_id in selections:
        card = by_id[copy_id]
        attached.append((target_id, card))
        events.append(
            EnergyAttachmentEvent(
                copy_id, card.name, player, target_id, "hand", channel
            )
        )
    return replace(
        state, budget=budget, hand=hand, attached=tuple(attached), events=tuple(events)
    )


def hand_attachment_events(
    state: EnergyAttachmentState,
    *,
    player: str | None = None,
) -> tuple[EnergyAttachmentEvent, ...]:
    return tuple(
        event for event in state.events
        if event.source_zone == "hand" and (player is None or event.player == player)
    )
