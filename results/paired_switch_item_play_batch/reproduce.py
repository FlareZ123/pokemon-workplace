"""Reproduce physical Item play batch and switch-boundary multiplicity."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from causal_event_journal import begin_journal, replay_journal
from committed_play_event import PlayKind, has_play_history
from paired_switch_event_bridge import record_paired_switch
from paired_switch_item_play_batch import item_play_batch_from_materialized_switch
from tools.identity_materialization import CardInstance, IdentityLedger, move_instance
from tools.multicopy_zone_state import ZoneCountState
from tools.paired_switch_identity_bridge import execute_materialized_paired_switch
from tools.paired_switch_order_catalog import PROGRAMS
from tools.turn_action_budget import TurnActionBudget


def ledger_for(name, count):
    return IdentityLedger(
        ZoneCountState(),
        tuple(CardInstance(f"src-{i}", name, name, "hand") for i in range(count)),
    )


def fails(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def run_case(name, own_bench):
    emp = make_pokemon(
        "emp", "Empoleon V", print_id="swsh5-40",
        tags={"Basic", "Water", "RuleBox"},
    )
    wob = make_pokemon(
        "wob", "Wobbuffet", print_id="xy4-36", tags={"Basic", "Psychic"},
    )
    bench_own = make_pokemon("own", "Own filler", tags={"Basic"})
    bench_opp = make_pokemon("opp", "Opponent filler", tags={"Basic"})
    own = make_board(emp, (bench_own,) if own_bench else ())
    opponent = make_board(wob, (bench_opp,))
    program = PROGRAMS[name]
    ids = tuple(f"src-{i}" for i in range(program.copies_together))
    before = ledger_for(name, program.copies_together)
    tx = execute_materialized_paired_switch(
        before, own, opponent, TurnActionBudget(), program,
        source_instance_ids=ids, opponent_promote_id="opp",
        own_promote_id="own" if own_bench else None,
    )
    assert tx is not None
    batch = item_play_batch_from_materialized_switch(
        before, tx, program, source_instance_ids=ids, player="A",
    )
    assert len(batch) == program.copies_together
    assert tuple(e.copy_id for e in batch) == ids
    assert all(e.kind is PlayKind.ITEM and not e.consumed_ordinary_quota for e in batch)

    start = begin_journal(own, opponent, first_player_owner="player")
    result = record_paired_switch(
        start, tx.board_resolution, program, action_id=f"{name}:{own_bench}",
        opponent_promote_id="opp", own_promote_id="own" if own_bench else None,
        committed_items=batch,
    )
    assert result.revision == (2 if own_bench else 1)
    assert result.boundaries[0].play_batch == batch
    assert all(not boundary.play_batch for boundary in result.boundaries[1:])
    assert result.committed_plays == batch
    assert replay_journal(result) == result
    assert has_play_history(result.committed_plays, player="A", kind=PlayKind.ITEM)

    fails(lambda: item_play_batch_from_materialized_switch(
        move_instance(before, ids[0], "deck"),
        tx, program, source_instance_ids=ids, player="A",
    ))
    fails(lambda: item_play_batch_from_materialized_switch(
        before, tx, program, source_instance_ids=ids + ids[:1], player="A",
    ))
    fails(lambda: record_paired_switch(
        start, tx.board_resolution, program, action_id="bad-card-batch",
        opponent_promote_id="opp", own_promote_id="own" if own_bench else None,
        committed_items=batch[:1] if len(batch) == 2 else batch + batch,
    ))
    return len(batch), result.revision


def main():
    measured = {}
    for name in ("Prime Catcher", "Cross Switcher"):
        for own_bench in (False, True):
            measured[(name, own_bench)] = run_case(name, own_bench)

    assert measured == {
        ("Prime Catcher", False): (1, 1),
        ("Prime Catcher", True): (1, 2),
        ("Cross Switcher", False): (2, 1),
        ("Cross Switcher", True): (2, 2),
    }
    print("paired_switch_item_play_batch regression: PASS", measured)


if __name__ == "__main__":
    main()
