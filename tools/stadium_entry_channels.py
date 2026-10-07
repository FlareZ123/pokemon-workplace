"""Separate ordinary Stadium play from effect-based Stadium entry.

The generic turn budget constrains playing a Stadium during the turn. Some card
effects instead put a Stadium into play. Those are distinct transition channels:
the effect can change the Stadium in play without consuming the ordinary
Stadium-play quota unless its text explicitly says otherwise.

This module models the concrete legal Expanded witness Gothitelle xy3-41 /
Teleport Room while preserving physical Stadium-copy identity.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class StadiumCopy:
    copy_id: str
    name: str

    def __post_init__(self) -> None:
        if not self.copy_id:
            raise ValueError("Stadium copy_id must be non-empty")
        if not self.name:
            raise ValueError("Stadium name must be non-empty")


@dataclass(frozen=True)
class StadiumEntryState:
    budget: TurnActionBudget
    hand: tuple[StadiumCopy, ...] = ()
    discard: tuple[StadiumCopy, ...] = ()
    in_play: StadiumCopy | None = None
    teleport_room_sources: frozenset[str] = frozenset()
    teleport_room_used: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        copies = list(self.hand) + list(self.discard)
        if self.in_play is not None:
            copies.append(self.in_play)
        copy_ids = [card.copy_id for card in copies]
        if len(copy_ids) != len(set(copy_ids)):
            raise ValueError("A physical Stadium copy cannot occupy two zones")
        if not self.teleport_room_used <= self.teleport_room_sources:
            raise ValueError("Used Teleport Room sources must exist in the state")


def _remove_copy(
    cards: tuple[StadiumCopy, ...],
    copy_id: str,
) -> tuple[StadiumCopy, tuple[StadiumCopy, ...]] | None:
    for index, card in enumerate(cards):
        if card.copy_id == copy_id:
            return card, cards[:index] + cards[index + 1 :]
    return None


def play_stadium_from_hand(
    state: StadiumEntryState,
    copy_id: str,
) -> StadiumEntryState | None:
    """Play one Stadium from hand, consuming the ordinary Stadium-play quota."""

    if not state.budget.can(TurnAction.STADIUM_PLAY):
        return None
    found = _remove_copy(state.hand, copy_id)
    if found is None:
        return None
    stadium, remaining_hand = found
    if state.in_play is not None and state.in_play.name == stadium.name:
        return None

    budget = state.budget.consume(TurnAction.STADIUM_PLAY)
    if budget is None:
        return None

    discard = state.discard
    if state.in_play is not None:
        discard = discard + (state.in_play,)
    return replace(
        state,
        budget=budget,
        hand=remaining_hand,
        discard=discard,
        in_play=stadium,
    )


def use_teleport_room(
    state: StadiumEntryState,
    source_id: str,
    replacement_copy_id: str | None = None,
) -> StadiumEntryState | None:
    """Use one physical Gothitelle's Teleport Room Ability.

    The current Stadium is discarded first. If a differently named Stadium is
    then available in the discard pile, putting one into play is mandatory, so
    callers must identify which physical copy is selected. If no legal
    replacement exists, the first half still resolves and the Stadium zone
    remains empty.

    The ordinary Stadium-play quota is intentionally unchanged.
    """

    if not state.budget.can(TurnAction.ATTACK):
        return None
    if source_id not in state.teleport_room_sources:
        return None
    if source_id in state.teleport_room_used:
        return None
    current = state.in_play
    if current is None:
        return None

    post_discard = state.discard + (current,)
    eligible = tuple(card for card in post_discard if card.name != current.name)

    if eligible:
        if replacement_copy_id is None:
            return None
        found = _remove_copy(eligible, replacement_copy_id)
        if found is None:
            return None
        replacement, _ = found
        remaining_discard = tuple(
            card for card in post_discard if card.copy_id != replacement.copy_id
        )
        in_play = replacement
    else:
        if replacement_copy_id is not None:
            return None
        remaining_discard = post_discard
        in_play = None

    return replace(
        state,
        discard=remaining_discard,
        in_play=in_play,
        teleport_room_used=state.teleport_room_used | {source_id},
    )


def teleport_room_options(
    state: StadiumEntryState,
    source_id: str,
) -> tuple[StadiumEntryState, ...]:
    """Enumerate every legal Teleport Room successor for one source."""

    if not state.budget.can(TurnAction.ATTACK):
        return ()
    if source_id not in state.teleport_room_sources:
        return ()
    if source_id in state.teleport_room_used:
        return ()
    current = state.in_play
    if current is None:
        return ()

    post_discard = state.discard + (current,)
    eligible_ids = tuple(
        card.copy_id
        for card in post_discard
        if card.name != current.name
    )
    if not eligible_ids:
        successor = use_teleport_room(state, source_id, None)
        return () if successor is None else (successor,)

    successors = []
    for copy_id in eligible_ids:
        successor = use_teleport_room(state, source_id, copy_id)
        if successor is not None:
            successors.append(successor)
    return tuple(successors)
