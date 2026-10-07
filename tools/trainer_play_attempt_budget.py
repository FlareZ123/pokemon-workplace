"""Transactional quota consumption for Trainer plays gated before use.

Seismitoad me55-84 / Quaking Fist makes the opponent flip when they try to use
a Trainer from hand. On tails, the card is discarded instead of being used.
Official rulings establish that a failed Supporter or Stadium attempt does not
spend that card type's once-per-turn allowance.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from turn_action_budget import TurnAction, TurnActionBudget


class QuotaTrainerKind(str, Enum):
    SUPPORTER = "supporter"
    STADIUM = "stadium"


@dataclass(frozen=True)
class TrainerCard:
    copy_id: str
    name: str
    kind: QuotaTrainerKind

    def __post_init__(self) -> None:
        if not self.copy_id or not self.name:
            raise ValueError("Trainer card identity must be non-empty")


@dataclass(frozen=True)
class TrainerAttemptState:
    budget: TurnActionBudget
    hand: tuple[TrainerCard, ...] = ()
    pending: TrainerCard | None = None
    discard: tuple[TrainerCard, ...] = ()
    stadium_in_play: TrainerCard | None = None
    successful_supporters: int = 0
    successful_stadium_plays: int = 0

    def __post_init__(self) -> None:
        cards = list(self.hand) + list(self.discard)
        if self.pending is not None:
            cards.append(self.pending)
        if self.stadium_in_play is not None:
            cards.append(self.stadium_in_play)
        ids = [card.copy_id for card in cards]
        if len(ids) != len(set(ids)):
            raise ValueError("a physical Trainer copy cannot occupy two zones")


def _turn_action(kind: QuotaTrainerKind) -> TurnAction:
    if kind is QuotaTrainerKind.SUPPORTER:
        return TurnAction.SUPPORTER
    return TurnAction.STADIUM_PLAY


def begin_trainer_attempt(
    state: TrainerAttemptState,
    copy_id: str,
) -> TrainerAttemptState | None:
    """Move a quota-limited Trainer into a pending gate without spending quota."""

    if state.pending is not None or state.budget.turn_ended:
        return None

    selected = None
    remaining = []
    for card in state.hand:
        if card.copy_id == copy_id and selected is None:
            selected = card
        else:
            remaining.append(card)
    if selected is None:
        return None

    action = _turn_action(selected.kind)
    if not state.budget.can(action):
        return None

    if (
        selected.kind is QuotaTrainerKind.STADIUM
        and state.stadium_in_play is not None
        and state.stadium_in_play.name == selected.name
    ):
        return None

    return replace(state, hand=tuple(remaining), pending=selected)


def fail_quaking_fist_gate(
    state: TrainerAttemptState,
) -> TrainerAttemptState | None:
    """Resolve tails: discard the attempted Trainer without spending its quota."""

    if state.pending is None:
        return None
    return replace(
        state,
        pending=None,
        discard=state.discard + (state.pending,),
    )


def pass_quaking_fist_gate(
    state: TrainerAttemptState,
) -> TrainerAttemptState | None:
    """Resolve heads: commit the ordinary play and consume quota exactly now."""

    card = state.pending
    if card is None:
        return None

    action = _turn_action(card.kind)
    budget = state.budget.consume(action)
    if budget is None:
        return None

    if card.kind is QuotaTrainerKind.SUPPORTER:
        return replace(
            state,
            budget=budget,
            pending=None,
            discard=state.discard + (card,),
            successful_supporters=state.successful_supporters + 1,
        )

    discard = state.discard
    if state.stadium_in_play is not None:
        discard = discard + (state.stadium_in_play,)
    return replace(
        state,
        budget=budget,
        pending=None,
        discard=discard,
        stadium_in_play=card,
        successful_stadium_plays=state.successful_stadium_plays + 1,
    )
