"""Executable E-31 Bench-entry effects for selected face-down Prize cards."""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_position_state import BoardPokemon, PokemonCard
from prize_pending_take import (
    PrizePendingTakeState,
    resolve_next_pending_prize,
    stage_additional_prize_front,
)
from promotion_pending_conservation import PromotionPendingState


LUCKY_BONUS_CARD_CLASS = "sv3pt5-113"
WISH_UPON_A_STAR_CARD_CLASS = "sm7-97"


@dataclass(frozen=True)
class PrizeBenchEntryTransition:
    before_prizes: PrizePendingTakeState
    after_prizes: PrizePendingTakeState
    before_board: PromotionPendingState
    after_board: PromotionPendingState
    entered_instance_id: str
    extra_prize_staged: bool


def _next_pending_matches(
    prizes: PrizePendingTakeState,
    card_class: str,
) -> bool:
    if not prizes.pending:
        return False
    row = prizes.pending[0]
    if not row.was_face_down:
        return False
    return prizes.physical.ledger.instance(row.instance_id).card_class == card_class


def _put_next_pending_basic_on_bench(
    prizes: PrizePendingTakeState,
    board: PromotionPendingState,
    *,
    expected_card_class: str,
    pokemon_id: str,
    card_name: str,
    retreat_cost: int,
    take_extra_prize: bool,
    extra_prize_position: int = 0,
) -> PrizeBenchEntryTransition | None:
    if prizes.physical.ledger != board.ledger:
        raise ValueError("Prize and board states must share the same physical ledger")
    if not _next_pending_matches(prizes, expected_card_class):
        return None
    if board.open_bench_slots <= 0:
        return None
    if any(row.pokemon_id == pokemon_id for row in board.pokemon):
        raise ValueError("pokemon_id already exists on the board")

    resolved = resolve_next_pending_prize(
        prizes,
        destination_zone="in_play",
        board_object_id=pokemon_id,
    )
    instance_id = resolved.resolved.instance_id
    pokemon = BoardPokemon(
        pokemon_id,
        (PokemonCard(instance_id, card_name),),
        retreat_cost=retreat_cost,
    )
    after_board = replace(
        board,
        ledger=resolved.after.physical.ledger,
        pokemon=board.pokemon + (pokemon,),
    )
    after_prizes = resolved.after
    extra_staged = False

    if take_extra_prize and after_prizes.physical.prize_instance_ids:
        if not 0 <= extra_prize_position < len(
            after_prizes.physical.prize_instance_ids
        ):
            raise IndexError("extra Prize position out of range")
        after_prizes = stage_additional_prize_front(
            after_prizes,
            position=extra_prize_position,
        )
        after_board = after_board.with_ledger(after_prizes.physical.ledger)
        extra_staged = True

    return PrizeBenchEntryTransition(
        before_prizes=prizes,
        after_prizes=after_prizes,
        before_board=board,
        after_board=after_board,
        entered_instance_id=instance_id,
        extra_prize_staged=extra_staged,
    )


def use_lucky_bonus(
    prizes: PrizePendingTakeState,
    board: PromotionPendingState,
    *,
    pokemon_id: str,
    coin_heads: bool,
    extra_prize_position: int = 0,
) -> PrizeBenchEntryTransition | None:
    """Use Chansey's Lucky Bonus on the next face-down pending Prize."""

    return _put_next_pending_basic_on_bench(
        prizes,
        board,
        expected_card_class=LUCKY_BONUS_CARD_CLASS,
        pokemon_id=pokemon_id,
        card_name="Chansey",
        retreat_cost=2,
        take_extra_prize=coin_heads,
        extra_prize_position=extra_prize_position,
    )


def use_wish_upon_a_star(
    prizes: PrizePendingTakeState,
    board: PromotionPendingState,
    *,
    pokemon_id: str,
    extra_prize_position: int = 0,
) -> PrizeBenchEntryTransition | None:
    """Use Jirachi Prism Star's Wish Upon a Star on the next pending Prize."""

    return _put_next_pending_basic_on_bench(
        prizes,
        board,
        expected_card_class=WISH_UPON_A_STAR_CARD_CLASS,
        pokemon_id=pokemon_id,
        card_name="Jirachi ◇",
        retreat_cost=1,
        take_extra_prize=True,
        extra_prize_position=extra_prize_position,
    )
