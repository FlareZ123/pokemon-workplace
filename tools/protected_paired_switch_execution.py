"""Preflight target-effect protection for audited two-sided Trainer switches.

This narrow adapter preserves the printed If-you-do order. It assumes the
defender's immunity sources remain unchanged across the first own switch.
"""
from __future__ import annotations

from dataclasses import dataclass

from committed_play_event import PlayKind
from tools.board_object_kernel import BoardState, switch_active
from tools.paired_switch_order_catalog import PairedSwitchProgram
from tools.paired_switch_physical_transaction import (
    ITEMS, SUPPORTERS, SwitchTransaction, execute_paired_switch,
)
from tools.turn_action_budget import TurnAction, TurnActionBudget
from trainer_effect_gust_protection import (
    ProtectionResult, TrainerEffectOrigin, evaluate_bench_gust_protection,
)


@dataclass(frozen=True)
class ProtectedSwitchDecision:
    transaction: SwitchTransaction | None
    protection: ProtectionResult | None
    denied_first_effect: bool
    denied_second_effect: bool


def execute_protected_paired_switch(
    player_board: BoardState,
    opponent_board: BoardState,
    turn_budget: TurnActionBudget,
    program: PairedSwitchProgram,
    *,
    opponent_promote_id: str | None,
    own_promote_id: str | None,
    copies_available: int = 1,
    item_play_allowed: bool = True,
) -> ProtectedSwitchDecision:
    """Resolve a single already-typed source with target immunity at each step.

    The card-source permissions and legality of copy availability are supplied
    by the caller; this layer only adds protected-target effects.
    """
    if program.name not in ITEMS | SUPPORTERS:
        raise ValueError("unsupported protected paired-switch program")

    protection = (
        evaluate_bench_gust_protection(
            opponent_board,
            opponent_promote_id,
            TrainerEffectOrigin(
                PlayKind.ITEM if program.name in ITEMS else PlayKind.SUPPORTER,
                True,
            ),
        )
        if opponent_promote_id is not None
        else None
    )
    if protection is not None and not protection.allowed:
        if program.first == "opponent":
            # The first conditional switch cannot resolve; nothing can follow.
            return ProtectedSwitchDecision(None, protection, True, False)

        # Team Rocket's Giovanni switches its own eligible Pokemon FIRST.
        # That completed own switch and the spent Supporter remain even when
        # a separately protected opposing target cannot be promoted.
        if (
            copies_available < program.copies_together
            or turn_budget.turn_ended
            or own_promote_id not in player_board.bench_ids
            or "team_rocket" not in player_board.get(player_board.active_id).tags
            or "team_rocket" not in player_board.get(own_promote_id).tags
        ):
            return ProtectedSwitchDecision(None, protection, False, False)
        budget = turn_budget.consume(TurnAction.SUPPORTER)
        if budget is None:
            return ProtectedSwitchDecision(None, protection, False, False)
        own_after = switch_active(player_board, own_promote_id)
        assert own_after is not None
        partial = SwitchTransaction(
            player_board=own_after,
            opponent_board=opponent_board,
            turn_budget=budget,
            source_copies_spent=program.copies_together,
            effect_sequence=("own",),
        )
        return ProtectedSwitchDecision(partial, protection, False, True)

    ordinary = execute_paired_switch(
        player_board,
        opponent_board,
        turn_budget,
        program,
        opponent_promote_id=opponent_promote_id,
        own_promote_id=own_promote_id,
        copies_available=copies_available,
        item_play_allowed=item_play_allowed,
    )
    return ProtectedSwitchDecision(ordinary, protection, False, False)
