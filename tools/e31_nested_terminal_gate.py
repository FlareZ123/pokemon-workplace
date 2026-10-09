"""Check game resolution while a nested E-31 Prize chain leaves an older sibling pending."""

from __future__ import annotations

from board_position_state import BoardPokemon, PokemonCard
from e31_greedy_order_physical import play_dream, play_greedy, profiles_and_target
from e31_peonia_seed_execution import initial_physical, play_peonia
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from post_knockout_game_resolution import Outcome
from post_prize_window_game_resolution import resolve_after_prize_window
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import stage_prize_takes
from promotion_pending_conservation import (
    PostKnockOutPromotionContext,
    PostKnockOutStage,
    PromotionPendingState,
    unresolved_prize_window_count,
)


def opponent_after_ko():
    """The opponent has a surviving former Bench Pokemon, awaiting promotion."""
    instance = CardInstance(
        "opponent-bench-card", "OPP", "Opponent Bench", "in_play",
        board_object_id="opponent-bench",
    )
    return PromotionPendingState(
        IdentityLedger(ZoneCountState(), (instance,)),
        (BoardPokemon(
            "opponent-bench",
            (PokemonCard("opponent-bench-card", "Opponent Bench"),),
            retreat_cost=1,
        ),),
        active_id=None,
    )


def context(board):
    return PostKnockOutPromotionContext(
        (("A", board), ("B", opponent_after_ko())),
        next_player_id="B",
    )


def branch(*, heads: bool):
    initial, board, physical = initial_physical()
    board, physical = play_peonia(board, physical)
    staged = stage_prize_takes(physical, positions=(0, 1))
    board = board.with_ledger(staged.physical.ledger)
    order = PendingPrizeBatchOrder.from_staged(staged)
    greedy, dream, target, action = profiles_and_target()

    assert resolve_after_prize_window(
        context(board), prizes_remaining={"A": 2, "B": 2},
    ) is None

    pending = order.choose_next("greedy")
    pending, board = play_greedy(
        pending, board, greedy,
        heads=heads, extra_position=0, use_jirachi=True,
    )
    order = order.advance_after_resolution(
        pending, resolved_instance_id="greedy",
    )
    assert order is not None
    assert tuple(card.instance_id for card in pending.pending) == ("dream",)

    count = len(pending.physical.prize_instance_ids)
    assert count == (0 if heads else 2)

    # The original Dream Ball is pending even if a nested Jirachi chain
    # exhausted every Prize card. Terminal state is still premature.
    open_context = context(board)
    assert unresolved_prize_window_count(open_context) == 1
    assert resolve_after_prize_window(
        open_context, prizes_remaining={"A": count, "B": 2},
    ) is None

    pending = order.choose_next("dream")
    pending, board = play_dream(
        pending, board, dream, target, action,
    )
    assert order.advance_after_resolution(
        pending, resolved_instance_id="dream",
    ) is None
    assert_conserved(initial, board.ledger)

    closed_context = context(board)
    assert unresolved_prize_window_count(closed_context) == 0
    terminal = resolve_after_prize_window(
        closed_context, prizes_remaining={"A": count, "B": 2},
    )
    assert terminal is not None
    if heads:
        assert terminal.context.stage == PostKnockOutStage.TERMINAL
        assert terminal.resolution.outcome("A") == Outcome.WIN
        assert terminal.resolution.outcome("B") == Outcome.LOSS
    else:
        assert terminal.context.stage == PostKnockOutStage.PROMOTION
        assert terminal.resolution.outcome("A") == Outcome.CONTINUE
        assert terminal.resolution.outcome("B") == Outcome.CONTINUE
    return terminal


def main() -> None:
    head = branch(heads=True)
    tail = branch(heads=False)
    assert head.resolution.terminal
    assert not tail.resolution.terminal
    print("Nested Greedy/Jirachi final Prize does not bypass older Dream Ball E-31 sibling")
    print("Heads: terminal win after Prize window; tails: game continues to promotion")


if __name__ == "__main__":
    main()
