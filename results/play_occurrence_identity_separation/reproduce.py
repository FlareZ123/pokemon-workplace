"""Reproduce source-identity gaps separately from named physical play evidence."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from causal_event_journal import (
    UnmaterializedPlay, append_boundary, begin_journal, replay_journal,
)
from committed_play_event import PlayKind
from paired_switch_event_bridge import record_paired_switch
from paired_switch_item_play_batch import item_play_batch_from_materialized_switch
from tools.identity_materialization import CardInstance, IdentityLedger
from tools.multicopy_zone_state import ZoneCountState
from tools.paired_switch_identity_bridge import execute_materialized_paired_switch
from tools.paired_switch_order_catalog import PROGRAMS
from tools.turn_action_budget import TurnActionBudget


def fails(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    active = make_pokemon("active", "Attacker", tags={"Basic"})
    target = make_pokemon("target", "Target", tags={"Basic"})
    bench = make_pokemon("bench", "Bench", tags={"Basic"})
    player = make_board(active)
    opponent = make_board(target, (bench,))
    program = PROGRAMS["Prime Catcher"]
    before = IdentityLedger(
        ZoneCountState(),
        (CardInstance("prime-1", program.name, program.name, "hand"),),
    )
    transaction = execute_materialized_paired_switch(
        before, player, opponent, TurnActionBudget(), program,
        source_instance_ids=("prime-1",),
        opponent_promote_id="bench", own_promote_id=None,
    )
    assert transaction is not None
    start = begin_journal(player, opponent)
    assert start.queried_play(player="A", kind=PlayKind.ITEM) is False
    assert start.play_history_complete and start.occurrence_history_complete

    # One Item play is known by action source and card name, but copy ID is opaque.
    opaque = record_paired_switch(
        start, transaction.board_resolution, program,
        action_id="opaque-prime", opponent_promote_id="bench",
        own_promote_id=None, acting_player="A",
    )
    assert opaque.committed_plays == ()
    assert not opaque.play_history_complete
    assert opaque.occurrence_history_complete
    assert opaque.unmaterialized_plays == (
        UnmaterializedPlay("A", PlayKind.ITEM, "Prime Catcher", 1),
    )
    assert opaque.queried_play(player="A", kind=PlayKind.ITEM) is True
    assert opaque.queried_play(
        player="A", kind=PlayKind.ITEM, name_contains="Cross Switcher",
    ) is False
    assert opaque.queried_play(player="A", kind=PlayKind.SUPPORTER) is False
    assert opaque.queried_play(player="B", kind=PlayKind.ITEM) is False
    assert replay_journal(opaque) == opaque

    # Identical board effects, but physical source IDs are now certified.
    batch = item_play_batch_from_materialized_switch(
        before, transaction, program,
        source_instance_ids=("prime-1",), player="A",
    )
    complete = record_paired_switch(
        start, transaction.board_resolution, program,
        action_id="materialized-prime", opponent_promote_id="bench",
        own_promote_id=None, committed_items=batch, acting_player="A",
    )
    assert complete.play_history_complete and complete.occurrence_history_complete
    assert complete.committed_plays == batch
    assert complete.unmaterialized_plays == ()
    assert complete.queried_play(player="A", kind=PlayKind.ITEM) is True
    assert complete.queried_play(player="A", kind=PlayKind.SUPPORTER) is False
    assert replay_journal(complete) == complete
    assert complete.boundaries[-1].opponent_board == opaque.boundaries[-1].opponent_board
    assert complete.lock_state == opaque.lock_state

    # Only a truly unspecified play's occurrence forces an indeterminate query.
    followed = append_boundary(
        opaque, expected_revision=opaque.revision,
        event_id="unclassified-play", description="missing action classification",
        player_board=player, opponent_board=opaque.boundaries[-1].opponent_board,
        play_record_complete=False,
    )
    assert not followed.occurrence_history_complete
    assert followed.queried_play(player="A", kind=PlayKind.ITEM) is True
    assert followed.queried_play(player="A", kind=PlayKind.SUPPORTER) is None
    assert replay_journal(followed) == followed

    fails(lambda: append_boundary(
        start, expected_revision=start.revision,
        event_id="contradictory-opaque", description="bad provenance",
        player_board=player, opponent_board=opponent,
        unmaterialized_plays=opaque.unmaterialized_plays,
        play_record_complete=True,
    ))
    fails(lambda: append_boundary(
        start, expected_revision=start.revision,
        event_id="contradictory-physical", description="bad provenance",
        player_board=player, opponent_board=opponent,
        committed_plays=batch, play_record_complete=False,
    ))
    print(
        "play_occurrence_identity_separation regression: PASS; "
        "known named Item play with unknown physical copy; "
        "per-source positive/negative/unknown and replay verified"
    )


if __name__ == "__main__":
    main()
