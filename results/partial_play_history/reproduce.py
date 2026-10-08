"""Regress true/false/unknown play queries after observable and opaque transactions."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from causal_event_journal import (
    append_boundary, begin_journal, replay_journal,
)
from committed_play_event import PlayKind
from paired_switch_event_bridge import record_paired_switch
from paired_switch_item_play_batch import item_play_batch_from_materialized_switch
from tools.identity_materialization import CardInstance, IdentityLedger
from tools.multicopy_zone_state import ZoneCountState
from tools.paired_switch_identity_bridge import execute_materialized_paired_switch
from tools.paired_switch_order_catalog import PROGRAMS
from tools.turn_action_budget import TurnActionBudget


def expect_error(f):
    try:
        f()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    active = make_pokemon("active", "Attacker", tags={"Basic"})
    target = make_pokemon("target", "Target", tags={"Basic"})
    bench = make_pokemon("bench", "Bench", tags={"Basic"})
    player = make_board(active)
    opponent = make_board(target, (bench,))
    prime = PROGRAMS["Prime Catcher"]
    transaction = execute_materialized_paired_switch(
        IdentityLedger(
            ZoneCountState(), (CardInstance("prime-1", prime.name, prime.name, "hand"),),
        ),
        player, opponent, TurnActionBudget(), prime,
        source_instance_ids=("prime-1",),
        opponent_promote_id="bench", own_promote_id=None,
    )
    assert transaction is not None
    start = begin_journal(player, opponent)
    assert start.queried_play(player="A", kind=PlayKind.ITEM) is False
    assert start.play_history_complete

    # Physical effect is executed, but source Item identity was never supplied.
    opaque = record_paired_switch(
        start, transaction.board_resolution, prime,
        action_id="opaque-prime", opponent_promote_id="bench",
        own_promote_id=None,
    )
    assert opaque.committed_plays == ()
    assert not opaque.play_history_complete
    assert opaque.queried_play(player="A", kind=PlayKind.ITEM) is None
    assert opaque.queried_play(player="A", kind=PlayKind.SUPPORTER) is None
    assert replay_journal(opaque) == opaque

    # An already-observed positive play survives later incomplete boundaries.
    batch = item_play_batch_from_materialized_switch(
        IdentityLedger(
            ZoneCountState(), (CardInstance("prime-1", prime.name, prime.name, "hand"),),
        ),
        transaction, prime, source_instance_ids=("prime-1",), player="A",
    )
    complete = record_paired_switch(
        start, transaction.board_resolution, prime,
        action_id="materialized-prime", opponent_promote_id="bench",
        own_promote_id=None, committed_items=batch,
    )
    assert complete.play_history_complete
    assert complete.committed_plays == batch
    assert complete.queried_play(player="A", kind=PlayKind.ITEM) is True
    assert complete.queried_play(player="A", kind=PlayKind.SUPPORTER) is False
    assert complete.queried_play(player="B", kind=PlayKind.ITEM) is False
    assert replay_journal(complete) == complete
    assert complete.boundaries[-1].opponent_board == opaque.boundaries[-1].opponent_board
    assert complete.lock_state == opaque.lock_state

    followed = append_boundary(
        complete, expected_revision=complete.revision,
        event_id="incomplete-future", description="unobserved physical source",
        player_board=player, opponent_board=complete.boundaries[-1].opponent_board,
        play_record_complete=False,
    )
    assert not followed.play_history_complete
    assert followed.queried_play(player="A", kind=PlayKind.ITEM) is True
    assert followed.queried_play(player="A", kind=PlayKind.SUPPORTER) is None
    assert replay_journal(followed) == followed

    expect_error(lambda: append_boundary(
        start, expected_revision=start.revision,
        event_id="contradictory", description="bad provenance",
        player_board=player, opponent_board=opponent,
        committed_plays=batch, play_record_complete=False,
    ))
    print(
        "partial_play_history regression: PASS; "
        "observed positive=True, verified negative=False, unobserved=None; "
        "replay and contradiction guards pass"
    )


if __name__ == "__main__":
    main()
