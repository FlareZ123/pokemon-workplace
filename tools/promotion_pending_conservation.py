"""Conserved post-Knock-Out state before replacement Active choices.

A normal BoardState always has an Active Pokemon. Knock Out resolution has a
rules-visible interval where a player's Active Pokemon can already be gone while
surviving former Bench Pokemon remain and Prize cards still have to resolve.
This module represents that interval without inventing a replacement Active.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from board_position_state import (
    AttachmentKind,
    BoardPokemon,
    BoardState,
    validate_state,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    dematerialize,
    detach_instance,
    move_instance,
    validate_board_position_stack_bindings,
)
from simultaneous_knockout_conservation import PendingKnockOutBatch
from stack_knockout_conservation import StackBoardMaterialState


DISCARD = "discard"
PRIZE_PENDING = "prize_pending"


class PostKnockOutStage(str, Enum):
    PRIZES = "prizes"
    PROMOTION = "promotion"
    TERMINAL = "terminal"


@dataclass(frozen=True)
class PromotionPendingState:
    """Physical board state after KO disposal and before optional promotion."""

    ledger: IdentityLedger
    pokemon: tuple[BoardPokemon, ...]
    active_id: str | None
    retreat_used: bool = False
    evolution_allowed: bool = True
    bench_capacity: int = 5

    def __post_init__(self) -> None:
        self.validate()

    @property
    def requires_promotion(self) -> bool:
        return self.active_id is None and bool(self.pokemon)

    @property
    def promotion_candidates(self) -> tuple[str, ...]:
        if not self.requires_promotion:
            return ()
        return tuple(row.pokemon_id for row in self.pokemon)

    @property
    def bench_occupancy(self) -> int:
        if self.active_id is None:
            return len(self.pokemon)
        return len(self.pokemon) - 1

    @property
    def open_bench_slots(self) -> int:
        return self.bench_capacity - self.bench_occupancy

    def validate(self) -> None:
        if self.bench_capacity < 0:
            raise ValueError("bench_capacity must be non-negative")

        ids = tuple(row.pokemon_id for row in self.pokemon)
        if len(ids) != len(set(ids)):
            raise ValueError("Pokemon object IDs must be unique")

        if self.active_id is not None:
            board = BoardState(
                self.pokemon,
                self.active_id,
                self.retreat_used,
                self.evolution_allowed,
                self.bench_capacity,
            )
            validate_state(board)
        else:
            if len(self.pokemon) > self.bench_capacity:
                raise ValueError(
                    "promotion-pending survivors exceed the former Bench capacity"
                )
            physical_ids: list[str] = []
            for pokemon in self.pokemon:
                if (
                    not pokemon.stack
                    or pokemon.retreat_cost < 0
                    or pokemon.damage_counters < 0
                ):
                    raise ValueError("invalid Pokemon state")
                if (
                    pokemon.special_conditions
                    or pokemon.combat.temporary_attack_lock
                    or pokemon.combat.temporary_retreat_lock
                ):
                    raise ValueError(
                        "former Benched Pokemon retains transient Active state"
                    )
                tools = tuple(
                    card
                    for card in pokemon.attachments
                    if card.kind == AttachmentKind.TOOL
                )
                if len(tools) > 1 or pokemon.combat.tool_attached != bool(tools):
                    raise ValueError("Tool state mismatch")
                physical_ids.extend(card.card_id for card in pokemon.stack)
                physical_ids.extend(card.card_id for card in pokemon.attachments)
            if len(physical_ids) != len(set(physical_ids)):
                raise ValueError("duplicate physical card ID")

        _validate_material_bindings(self.ledger, self.pokemon)

    def with_ledger(self, ledger: IdentityLedger) -> "PromotionPendingState":
        """Replace only the canonical ledger after another subsystem mutates it."""

        return replace(self, ledger=ledger)

    def with_active(self, pokemon_id: str) -> "PromotionPendingState" | None:
        if not self.requires_promotion:
            return None
        if pokemon_id not in self.promotion_candidates:
            return None
        return replace(self, active_id=pokemon_id)

    def to_stack_state(self) -> StackBoardMaterialState | None:
        """Return the ordinary board representation once promotion is settled."""

        if self.requires_promotion:
            return None
        if not self.pokemon:
            return StackBoardMaterialState(self.ledger, None)
        assert self.active_id is not None
        board = BoardState(
            self.pokemon,
            self.active_id,
            self.retreat_used,
            self.evolution_allowed,
            self.bench_capacity,
        )
        validate_state(board)
        return StackBoardMaterialState(self.ledger, board)


@dataclass(frozen=True)
class PostKnockOutPromotionContext:
    """Two-player sequencing state after physical KO disposal."""

    players: tuple[tuple[str, PromotionPendingState], ...]
    next_player_id: str
    stage: PostKnockOutStage = PostKnockOutStage.PRIZES

    def __post_init__(self) -> None:
        if len(self.players) != 2:
            raise ValueError("Pokemon TCG context requires exactly two players")
        ids = tuple(player_id for player_id, _state in self.players)
        if len(set(ids)) != 2 or any(not player_id for player_id in ids):
            raise ValueError("player IDs must be two distinct non-empty values")
        if self.next_player_id not in ids:
            raise ValueError("next_player_id must identify one player")

    def state_for(self, player_id: str) -> PromotionPendingState:
        for current_id, state in self.players:
            if current_id == player_id:
                return state
        raise KeyError(player_id)


def _validate_material_bindings(
    ledger: IdentityLedger,
    pokemon: tuple[BoardPokemon, ...],
) -> None:
    class _BoardView:
        def __init__(self, rows: tuple[BoardPokemon, ...]) -> None:
            self.pokemon = rows

    validate_board_position_stack_bindings(ledger, _BoardView(pokemon))

    expected: dict[str, tuple[str, str]] = {}
    for row in pokemon:
        for attachment in row.attachments:
            if attachment.card_id in expected:
                raise ValueError(
                    f"duplicate board attachment ID: {attachment.card_id}"
                )
            expected[attachment.card_id] = (
                row.pokemon_id,
                attachment.name,
            )

    actual = {
        row.instance_id: (row.attached_to, row.card_name)
        for row in ledger.instances
        if row.zone == "attached"
    }
    if actual != expected:
        raise ValueError(
            "attachment bindings differ between identity ledger and pending board"
        )


def dispose_pending_before_promotion(
    pending: PendingKnockOutBatch,
) -> PromotionPendingState:
    """Dispose a complete KO batch without selecting a replacement Active."""

    board = pending.state.board
    assert board is not None

    knocked_out = set(pending.knocked_out_ids)
    removed = tuple(
        pokemon for pokemon in board.pokemon if pokemon.pokemon_id in knocked_out
    )
    survivors = tuple(
        pokemon for pokemon in board.pokemon if pokemon.pokemon_id not in knocked_out
    )
    active_id = None if board.active_id in knocked_out else board.active_id

    ledger = pending.state.ledger
    for pokemon in removed:
        for card in pokemon.stack:
            ledger = move_instance(ledger, card.card_id, DISCARD)
            ledger = dematerialize(ledger, card.card_id)
        for attachment in pokemon.attachments:
            ledger = detach_instance(ledger, attachment.card_id, DISCARD)
            ledger = dematerialize(ledger, attachment.card_id)

    result = PromotionPendingState(
        ledger,
        survivors,
        active_id,
        board.retreat_used,
        board.evolution_allowed,
        board.bench_capacity,
    )
    assert_conserved(pending.state.ledger, result.ledger)
    return result


def replace_player_state(
    context: PostKnockOutPromotionContext,
    *,
    player_id: str,
    state: PromotionPendingState,
) -> PostKnockOutPromotionContext:
    context.state_for(player_id)
    players = tuple(
        (current_id, state if current_id == player_id else current_state)
        for current_id, current_state in context.players
    )
    return replace(context, players=players)


def unresolved_prize_count(context: PostKnockOutPromotionContext) -> int:
    """Count exact or exchangeable cards still inside the Prize timing window."""

    total = 0
    for _player_id, state in context.players:
        total += sum(
            row.zone == PRIZE_PENDING
            for row in state.ledger.instances
        )
        total += sum(
            count
            for _card_class, zone, count in state.ledger.exchangeable.counts
            if zone == PRIZE_PENDING
        )
    return total


def advance_after_prizes(
    context: PostKnockOutPromotionContext,
    *,
    game_continues: bool,
) -> PostKnockOutPromotionContext | None:
    """Close the Prize window after an external terminal-state evaluation."""

    if context.stage != PostKnockOutStage.PRIZES:
        return None
    if unresolved_prize_count(context):
        return None
    return replace(
        context,
        stage=(
            PostKnockOutStage.PROMOTION
            if game_continues
            else PostKnockOutStage.TERMINAL
        ),
    )


def promotion_order(
    context: PostKnockOutPromotionContext,
) -> tuple[str, ...]:
    requiring = tuple(
        player_id
        for player_id, state in context.players
        if state.requires_promotion
    )
    if len(requiring) <= 1:
        return requiring
    if context.next_player_id not in requiring:
        return requiring
    other = next(
        player_id for player_id in requiring
        if player_id != context.next_player_id
    )
    return (context.next_player_id, other)


def next_promotion_player(
    context: PostKnockOutPromotionContext,
) -> str | None:
    if context.stage != PostKnockOutStage.PROMOTION:
        return None
    order = promotion_order(context)
    return order[0] if order else None


def choose_promotion(
    context: PostKnockOutPromotionContext,
    *,
    player_id: str,
    pokemon_id: str,
) -> PostKnockOutPromotionContext | None:
    """Apply exactly the next legal replacement-Active decision."""

    if next_promotion_player(context) != player_id:
        return None

    state = context.state_for(player_id).with_active(pokemon_id)
    if state is None:
        return None
    return replace_player_state(context, player_id=player_id, state=state)


def finalize_promotions(
    context: PostKnockOutPromotionContext,
) -> tuple[tuple[str, StackBoardMaterialState], ...] | None:
    if context.stage != PostKnockOutStage.PROMOTION:
        return None
    if next_promotion_player(context) is not None:
        return None

    output: list[tuple[str, StackBoardMaterialState]] = []
    for player_id, state in context.players:
        resolved = state.to_stack_state()
        if resolved is None:
            return None
        output.append((player_id, resolved))
    return tuple(output)
