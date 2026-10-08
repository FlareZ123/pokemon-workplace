"""Record each switch inside a validated two-sided Trainer transaction.

The source transaction remains authoritative for source legality and payment.
This adapter preserves its effect order as separate causal lock boundaries.
"""
from __future__ import annotations

from board_object_kernel import switch_active
from causal_event_journal import (
    CausalEventJournal, UnmaterializedPlay, append_boundary,
)
from committed_play_event import CommittedPlayEvent, PlayChannel, PlayKind
from paired_switch_order_catalog import PairedSwitchProgram
from paired_switch_physical_transaction import (
    ITEMS, SUPPORTERS, SwitchTransaction,
)


def record_paired_switch(
    journal: CausalEventJournal,
    transaction: SwitchTransaction,
    program: PairedSwitchProgram,
    *,
    action_id: str,
    opponent_promote_id: str | None,
    own_promote_id: str | None,
    committed_supporter: CommittedPlayEvent | None = None,
    committed_items: tuple[CommittedPlayEvent, ...] = (),
    acting_player: str = "player",
) -> CausalEventJournal:
    """Fold a complete validated transaction at its individual switch boundaries.

    The successful physical transaction is supplied by execute_paired_switch.
    The optional supporter event is produced by a committed-play adapter.
    Item source identities are optional when the upstream transaction has not
    materialized its source cards. That boundary is marked partially observed.
    """
    if not action_id or not acting_player:
        raise ValueError("action_id and acting_player must be nonempty")
    if program.name not in ITEMS | SUPPORTERS:
        raise ValueError("unsupported paired switch program")
    if transaction.source_copies_spent != program.copies_together:
        raise ValueError("source copy count disagrees with program")
    if transaction.effect_sequence not in {
        (program.first,), (program.first, program.second),
    }:
        raise ValueError("effect order disagrees with program")

    if program.name in SUPPORTERS:
        if (
            committed_supporter is None
            or committed_supporter.kind is not PlayKind.SUPPORTER
            or committed_supporter.channel is not PlayChannel.ORDINARY
            or committed_supporter.card_name != program.name
            or not committed_supporter.consumed_ordinary_quota
            or committed_supporter.out_of_turn
            or committed_items
        ):
            raise ValueError("successful ordinary Supporter requires matching play event")
    else:
        if committed_supporter is not None:
            raise ValueError("Item cannot masquerade as a Supporter play")
        if committed_items and (
            len(committed_items) != program.copies_together
            or len({event.copy_id for event in committed_items}) != len(committed_items)
            or any(
                event.kind is not PlayKind.ITEM
                or event.channel is not PlayChannel.ORDINARY
                or event.card_name != program.name
                or event.consumed_ordinary_quota
                or event.out_of_turn
                for event in committed_items
            )
        ):
            raise ValueError("Item batch must match physical source copy count")

    last = journal.boundaries[-1] if journal.boundaries else None
    player = last.player_board if last is not None else journal.initial_player_board
    opponent = last.opponent_board if last is not None else journal.initial_opponent_board
    stadium_name = last.stadium_name if last is not None else journal.initial_stadium_name

    result = journal
    for index, side in enumerate(transaction.effect_sequence, 1):
        if side == "opponent":
            switched = switch_active(opponent, opponent_promote_id)
            if switched is None:
                raise ValueError("opponent switch disagrees with starting board")
            opponent = switched
        else:
            switched = switch_active(player, own_promote_id)
            if switched is None:
                raise ValueError("own switch disagrees with starting board")
            player = switched
        result = append_boundary(
            result,
            expected_revision=result.revision,
            event_id=f"{action_id}:{index}",
            description=f"{program.name}: {side} switch",
            player_board=player,
            opponent_board=opponent,
            stadium_name=stadium_name,
            committed_plays=(
                ((committed_supporter,) if committed_supporter is not None else committed_items)
                if index == 1 else ()
            ),
            play_record_complete=(
                bool(committed_items) if index == 1 and program.name in ITEMS
                else True
            ),
            unmaterialized_plays=(
                (UnmaterializedPlay(
                    acting_player, PlayKind.ITEM, program.name, program.copies_together,
                ),)
                if index == 1 and program.name in ITEMS and not committed_items
                else ()
            ),
        )

    if (
        player != transaction.player_board
        or opponent != transaction.opponent_board
    ):
        raise ValueError("replayed microsteps disagree with the supplied transaction")
    return result
