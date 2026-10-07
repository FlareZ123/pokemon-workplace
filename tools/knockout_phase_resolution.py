"""Knock Out phase routing and cross-player ordering adapters.

This module extends the simultaneous Knock Out conservation kernel without
encoding card-specific semantics. Upstream logic identifies which attachments a
resolved Knock Out trigger redirects. The adapter moves those physical cards out
of the doomed board relation before the batch-discard boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from board_position_state import AttachmentKind, BoardPokemon, replace_pokemon
from identity_materialization import assert_conserved, dematerialize, detach_instance
from simultaneous_knockout_conservation import PendingKnockOutBatch
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class AttachmentRoute:
    instance_id: str
    destination_zone: str

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("instance_id must be non-empty")
        if not self.destination_zone:
            raise ValueError("destination_zone must be non-empty")
        if self.destination_zone in {"attached", "in_play"}:
            raise ValueError("attachment route must leave the board relation")


@dataclass(frozen=True)
class KnockOutTrigger:
    trigger_id: str
    controller_id: str
    label: str = ""

    def __post_init__(self) -> None:
        if not self.trigger_id:
            raise ValueError("trigger_id must be non-empty")
        if not self.controller_id:
            raise ValueError("controller_id must be non-empty")


@dataclass(frozen=True)
class PlayerKnockOutBatch:
    player_id: str
    pending: PendingKnockOutBatch

    def __post_init__(self) -> None:
        if not self.player_id:
            raise ValueError("player_id must be non-empty")


@dataclass(frozen=True)
class TwoPlayerKnockOutPhase:
    sides: tuple[PlayerKnockOutBatch, PlayerKnockOutBatch]
    current_turn_player: str
    next_turn_player: str

    def __post_init__(self) -> None:
        player_ids = tuple(side.player_id for side in self.sides)
        if len(set(player_ids)) != 2:
            raise ValueError("Knock Out phase requires two distinct players")
        if self.current_turn_player not in player_ids:
            raise ValueError("current_turn_player must be one of the players")
        if self.next_turn_player not in player_ids:
            raise ValueError("next_turn_player must be one of the players")
        if self.current_turn_player == self.next_turn_player:
            raise ValueError("current and next turn players must differ")


def _attachment_locations(
    pending: PendingKnockOutBatch,
) -> dict[str, tuple[BoardPokemon, object]]:
    board = pending.state.board
    assert board is not None
    knocked_out = set(pending.knocked_out_ids)
    locations: dict[str, tuple[BoardPokemon, object]] = {}
    for pokemon in board.pokemon:
        if pokemon.pokemon_id not in knocked_out:
            continue
        for attachment in pokemon.attachments:
            if attachment.card_id in locations:
                raise ValueError(
                    f"duplicate attachment instance ID: {attachment.card_id}"
                )
            locations[attachment.card_id] = (pokemon, attachment)
    return locations


def route_pending_attachments(
    pending: PendingKnockOutBatch,
    routes: Iterable[AttachmentRoute],
) -> PendingKnockOutBatch | None:
    """Redirect selected doomed attachments before batch disposal.

    Every route is applied atomically against the same pre-routing snapshot.
    The semantic layer is responsible for supplying exactly the attachments
    eligible for a card effect such as an "instead of discard" recovery.
    """

    route_rows = tuple(routes)
    route_ids = tuple(route.instance_id for route in route_rows)
    if len(route_ids) != len(set(route_ids)):
        return None
    if not route_rows:
        return pending

    board = pending.state.board
    assert board is not None
    locations = _attachment_locations(pending)
    if any(instance_id not in locations for instance_id in route_ids):
        return None

    routed_ids = set(route_ids)
    next_board = board
    affected_pokemon = {
        locations[instance_id][0].pokemon_id
        for instance_id in route_ids
    }
    for pokemon_id in affected_pokemon:
        pokemon = board.get(pokemon_id)
        remaining = tuple(
            attachment
            for attachment in pokemon.attachments
            if attachment.card_id not in routed_ids
        )
        tool_present = any(
            attachment.kind == AttachmentKind.TOOL
            for attachment in remaining
        )
        updated = replace(
            pokemon,
            attachments=remaining,
            combat=replace(pokemon.combat, tool_attached=tool_present),
        )
        next_board = replace_pokemon(next_board, updated)

    ledger = pending.state.ledger
    for route in route_rows:
        ledger = detach_instance(
            ledger,
            route.instance_id,
            route.destination_zone,
        )
        ledger = dematerialize(ledger, route.instance_id)

    next_state = StackBoardMaterialState(ledger, next_board)
    assert_conserved(pending.state.ledger, next_state.ledger)
    return PendingKnockOutBatch(next_state, pending.knocked_out_ids)


def choose_knock_out_trigger_order(
    phase: TwoPlayerKnockOutPhase,
    triggers: Iterable[KnockOutTrigger],
    ordered_trigger_ids: Iterable[str],
    *,
    choosing_player: str,
) -> tuple[KnockOutTrigger, ...] | None:
    """Validate the global ordering authority for simultaneous KO triggers."""

    rows = tuple(triggers)
    ids = tuple(row.trigger_id for row in rows)
    if len(ids) != len(set(ids)):
        raise ValueError("trigger IDs must be unique")
    player_ids = {side.player_id for side in phase.sides}
    if any(row.controller_id not in player_ids for row in rows):
        raise ValueError("trigger controller is not part of this game")
    if choosing_player != phase.current_turn_player:
        return None

    requested = tuple(ordered_trigger_ids)
    if len(requested) != len(ids) or set(requested) != set(ids):
        return None
    by_id = {row.trigger_id: row for row in rows}
    return tuple(by_id[trigger_id] for trigger_id in requested)


def players_requiring_promotion(
    phase: TwoPlayerKnockOutPhase,
) -> tuple[str, ...]:
    """Return players whose Active is in the batch and who have a survivor."""

    required: list[str] = []
    for side in phase.sides:
        board = side.pending.state.board
        assert board is not None
        knocked_out = set(side.pending.knocked_out_ids)
        if board.active_id not in knocked_out:
            continue
        surviving_bench = tuple(
            pokemon_id
            for pokemon_id in board.bench_ids
            if pokemon_id not in knocked_out
        )
        if surviving_bench:
            required.append(side.player_id)
    return tuple(required)


def promotion_choice_order(
    phase: TwoPlayerKnockOutPhase,
) -> tuple[str, ...]:
    """Order replacement-Active choices after simultaneous Active Knock Outs."""

    required = players_requiring_promotion(phase)
    if len(required) <= 1:
        return required
    if phase.next_turn_player not in required:
        return required
    other = next(
        player_id
        for player_id in required
        if player_id != phase.next_turn_player
    )
    return (phase.next_turn_player, other)
