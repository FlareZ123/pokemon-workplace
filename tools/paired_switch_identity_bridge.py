"""Conserved physical source-card routing for paired-switch Trainer actions.

A successful transaction resolves the audited two-sided physical switch
and moves exactly the supplied materialized hand copies into discard.
"""
from dataclasses import dataclass

from tools.board_object_kernel import BoardState
from tools.identity_materialization import (
    IdentityLedger, assert_conserved, move_instance,
    validate_board_attachment_bindings,
)
from tools.paired_switch_order_catalog import PairedSwitchProgram
from tools.paired_switch_physical_transaction import (
    SwitchTransaction, execute_paired_switch,
)
from tools.turn_action_budget import TurnActionBudget


@dataclass(frozen=True)
class MaterializedPairedSwitchTransaction:
    ledger: IdentityLedger
    board_resolution: SwitchTransaction


def execute_materialized_paired_switch(
    ledger: IdentityLedger,
    player_board: BoardState,
    opponent_board: BoardState,
    turn_budget: TurnActionBudget,
    program: PairedSwitchProgram,
    *,
    source_instance_ids: tuple[str, ...],
    opponent_promote_id: str | None,
    own_promote_id: str | None,
    item_play_allowed: bool = True,
) -> MaterializedPairedSwitchTransaction | None:
    """Return conserving immutable after-state or None when play is invalid.

    The supplied ledger belongs to the player and includes materialized
    attachments on that player's board. Opponent attachments are held in
    their own ledger outside this adapter.
    """
    ids = source_instance_ids
    if len(ids) != program.copies_together or len(set(ids)) != len(ids):
        return None
    source_by_id = {row.instance_id: row for row in ledger.instances}
    if any(
        card_id not in source_by_id
        or source_by_id[card_id].card_name != program.name
        or source_by_id[card_id].zone != "hand"
        for card_id in ids
    ):
        return None

    validate_board_attachment_bindings(ledger, player_board)
    resolved = execute_paired_switch(
        player_board, opponent_board, turn_budget, program,
        opponent_promote_id=opponent_promote_id,
        own_promote_id=own_promote_id,
        copies_available=len(ids),
        item_play_allowed=item_play_allowed,
    )
    if resolved is None:
        return None

    after = ledger
    for card_id in ids:
        after = move_instance(after, card_id, "discard")
    assert_conserved(ledger, after)
    validate_board_attachment_bindings(after, resolved.player_board)
    return MaterializedPairedSwitchTransaction(
        ledger=after, board_resolution=resolved
    )
