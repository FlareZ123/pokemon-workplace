"""Reproduce ordered two-sided switch microsteps in one causal journal."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from causal_event_journal import begin_journal, replay_journal
from committed_play_event import from_supporter_execution
from paired_switch_event_bridge import record_paired_switch
from supporter_play_event_history import (
    SupporterExecutionState, SupporterIdentity, play_supporter_from_hand,
)
from tools.paired_switch_order_catalog import PROGRAMS
from tools.paired_switch_physical_transaction import execute_paired_switch
from tools.turn_action_budget import TurnActionBudget


def committed(name: str):
    base = SupporterExecutionState()
    played = play_supporter_from_hand(base, SupporterIdentity(name+"-copy", name))
    assert played is not None
    event = from_supporter_execution(base, played, player="A")
    assert event is not None
    return event


def fails(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    empoleon = make_pokemon(
        "emp", "Empoleon V", print_id="swsh5-40",
        tags={"Basic", "Water", "RuleBox"},
    )
    wobbuffet = make_pokemon(
        "wob", "Wobbuffet", print_id="xy4-36",
        tags={"Basic", "Psychic"},
    )
    own_filler = make_pokemon("own-fill", "Own filler", tags={"Basic"})
    opponent_filler = make_pokemon("opp-fill", "Opponent filler", tags={"Basic"})
    player = make_board(empoleon, (own_filler,))
    opponent = make_board(wobbuffet, (opponent_filler,))
    start = begin_journal(player, opponent, first_player_owner="player")
    assert start.lock_state.basis == "setup_first_player"

    guzma = PROGRAMS["Guzma"]
    tx = execute_paired_switch(
        player, opponent, TurnActionBudget(), guzma,
        opponent_promote_id="opp-fill", own_promote_id="own-fill",
    )
    assert tx is not None and tx.effect_sequence == ("opponent", "own")
    event = committed("Guzma")
    journal = record_paired_switch(
        start, tx, guzma, action_id="guzma-action",
        opponent_promote_id="opp-fill", own_promote_id="own-fill",
        committed_supporter=event,
    )
    assert journal.revision == 2
    assert journal.committed_plays == (event,)
    assert journal.boundaries[0].opponent_board.active_id == "opp-fill"
    assert journal.boundaries[0].player_board.active_id == "emp"
    assert journal.boundaries[1].player_board.active_id == "own-fill"
    assert all(row.lock_state.basis == "snapshot" for row in journal.boundaries)
    assert replay_journal(journal) == journal

    fails(lambda: record_paired_switch(
        start, tx, guzma, action_id="missing-play",
        opponent_promote_id="opp-fill", own_promote_id="own-fill",
    ))
    fails(lambda: record_paired_switch(
        start, replace(tx, player_board=player), guzma,
        action_id="wrong-result", opponent_promote_id="opp-fill",
        own_promote_id="own-fill", committed_supporter=event,
    ))

    # Prime Catcher with no own Bench has exactly one executed half.
    prime = PROGRAMS["Prime Catcher"]
    solo = make_board(empoleon)
    prime_tx = execute_paired_switch(
        solo, opponent, TurnActionBudget(), prime,
        opponent_promote_id="opp-fill", own_promote_id=None,
    )
    assert prime_tx is not None and prime_tx.effect_sequence == ("opponent",)
    prime_start = begin_journal(solo, opponent, first_player_owner="player")
    prime_journal = record_paired_switch(
        prime_start, prime_tx, prime, action_id="prime-action",
        opponent_promote_id="opp-fill", own_promote_id=None,
    )
    assert prime_journal.revision == 1
    assert prime_journal.committed_plays == ()
    assert prime_journal.lock_state.basis == "snapshot"
    assert replay_journal(prime_journal) == prime_journal

    # Giovanni's order is the reverse: own eligible Team Rocket pair first.
    tr_active = make_pokemon(
        "tr-active", "TR active", tags={"Basic", "team_rocket"},
    )
    tr_bench = make_pokemon(
        "tr-bench", "TR bench", tags={"Basic", "team_rocket"},
    )
    tr_player = make_board(tr_active, (tr_bench,))
    giovanni = PROGRAMS["Team Rocket's Giovanni"]
    giovanni_tx = execute_paired_switch(
        tr_player, opponent, TurnActionBudget(), giovanni,
        opponent_promote_id="opp-fill", own_promote_id="tr-bench",
    )
    assert giovanni_tx is not None
    assert giovanni_tx.effect_sequence == ("own", "opponent")
    giovanni_start = begin_journal(tr_player, opponent)
    giovanni_event = committed("Team Rocket's Giovanni")
    giovanni_journal = record_paired_switch(
        giovanni_start, giovanni_tx, giovanni,
        action_id="giovanni-action", opponent_promote_id="opp-fill",
        own_promote_id="tr-bench", committed_supporter=giovanni_event,
    )
    assert giovanni_journal.boundaries[0].player_board.active_id == "tr-bench"
    assert giovanni_journal.boundaries[0].opponent_board.active_id == "wob"
    assert giovanni_journal.boundaries[1].opponent_board.active_id == "opp-fill"
    assert giovanni_journal.committed_plays == (giovanni_event,)
    assert replay_journal(giovanni_journal) == giovanni_journal
    print("paired_switch_event_journal regression: PASS; Guzma/Prime/Giovanni microsteps")


if __name__ == "__main__":
    main()
