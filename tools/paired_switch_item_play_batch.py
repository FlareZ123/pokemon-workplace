"""Construct physical Item play-batch records from a validated identity transaction.

Cross Switcher spends two distinct cards simultaneously for one effect.
The output is a batch of card identities; it does not imply sequential effect use.
"""
from __future__ import annotations

from committed_play_event import CommittedPlayEvent, PlayChannel, PlayKind
from tools.identity_materialization import IdentityLedger
from tools.paired_switch_identity_bridge import MaterializedPairedSwitchTransaction
from tools.paired_switch_order_catalog import PairedSwitchProgram
from tools.paired_switch_physical_transaction import ITEMS


def item_play_batch_from_materialized_switch(
    before: IdentityLedger,
    after: MaterializedPairedSwitchTransaction,
    program: PairedSwitchProgram,
    *,
    source_instance_ids: tuple[str, ...],
    player: str,
) -> tuple[CommittedPlayEvent, ...]:
    """Project one validated physical Item transaction into one grouped play batch."""
    ids = source_instance_ids
    if not player or program.name not in ITEMS:
        raise ValueError("requires an Item source and an acting player")
    if len(ids) != program.copies_together or len(set(ids)) != len(ids):
        raise ValueError("wrong number of distinct physical Item source cards")
    if after.board_resolution.source_copies_spent != len(ids):
        raise ValueError("transaction source count differs from Item play batch")
    if before.totals() != after.ledger.totals():
        raise ValueError("source ledger does not conserve card totals")

    for instance_id in ids:
        try:
            previous = before.instance(instance_id)
            current = after.ledger.instance(instance_id)
        except KeyError as exc:
            raise ValueError("missing materialized physical Item source") from exc
        if (
            previous.zone != "hand"
            or current.zone != "discard"
            or previous.card_name != program.name
            or current.card_name != program.name
        ):
            raise ValueError("source Item must move from hand to discard")
    return tuple(
        CommittedPlayEvent(
            PlayKind.ITEM, PlayChannel.ORDINARY, player, player, player,
            instance_id, program.name, False,
        )
        for instance_id in ids
    )
