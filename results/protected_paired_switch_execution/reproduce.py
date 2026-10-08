"""Verify source-dependent protection and asymmetric If-you-do direction."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from causal_event_journal import begin_journal
from paired_switch_event_bridge import record_paired_switch
from committed_play_event import from_supporter_execution
from supporter_play_event_history import (
    SupporterExecutionState, SupporterIdentity, play_supporter_from_hand,
)
from tools.paired_switch_order_catalog import PROGRAMS
from tools.paired_switch_physical_transaction import execute_paired_switch
from tools.turn_action_budget import TurnActionBudget
from protected_paired_switch_execution import execute_protected_paired_switch


def committed(name):
    before = SupporterExecutionState()
    after = play_supporter_from_hand(
        before, SupporterIdentity("giovanni-physical", name)
    )
    assert after is not None
    event = from_supporter_execution(before, after, player="A")
    assert event is not None
    return event


def main():
    own_active = make_pokemon(
        "own-a", "Rocket A", tags={"Basic", "team_rocket"},
    )
    own_bench = make_pokemon(
        "own-b", "Rocket B", tags={"Basic", "team_rocket"},
    )
    player = make_board(own_active, (own_bench,))
    defender_active = make_pokemon(
        "def-active", "Ordinary Active", tags={"Basic"},
    )
    axew = make_pokemon(
        "axew", "Axew", print_id="sm11-154", tags={"Basic"},
    )
    defender = make_board(defender_active, (axew,))
    budget = TurnActionBudget()

    # The board-only baseline lacks E-29 target-effect prevention.
    naive = execute_paired_switch(
        player, defender, budget, PROGRAMS["Team Rocket's Giovanni"],
        own_promote_id="own-b", opponent_promote_id="axew",
    )
    assert naive is not None
    assert naive.opponent_board.active_id == "axew"

    giovanni = execute_protected_paired_switch(
        player, defender, budget, PROGRAMS["Team Rocket's Giovanni"],
        own_promote_id="own-b", opponent_promote_id="axew",
    )
    tx = giovanni.transaction
    assert tx is not None
    assert not giovanni.denied_first_effect
    assert giovanni.denied_second_effect
    assert tx.effect_sequence == ("own",)
    assert tx.player_board.active_id == "own-b"
    assert tx.opponent_board == defender
    assert tx.turn_budget.supporter_plays_used == 1
    assert tx.source_copies_spent == 1

    event = committed("Team Rocket's Giovanni")
    journal = begin_journal(player, defender)
    journal = record_paired_switch(
        journal, tx, PROGRAMS["Team Rocket's Giovanni"],
        action_id="giovanni-partial", opponent_promote_id="axew",
        own_promote_id="own-b", committed_supporter=event,
    )
    assert journal.revision == 1
    assert journal.committed_plays == (event,)
    assert journal.boundaries[-1].player_board.active_id == "own-b"
    assert journal.boundaries[-1].opponent_board.active_id == "def-active"

    # First-opponent actions cannot execute their follow-up own switch
    # when the specified opposing target is protected.
    for name in ("Prime Catcher", "Cross Switcher", "Guzma"):
        program = PROGRAMS[name]
        denied = execute_protected_paired_switch(
            player, defender, budget, program,
            own_promote_id="own-b", opponent_promote_id="axew",
            copies_available=program.copies_together,
        )
        assert denied.transaction is None, name
        assert denied.denied_first_effect and not denied.denied_second_effect
        assert denied.protection is not None and not denied.protection.allowed

    # Positive counterfactual: a nonprotected target produces full two-sided
    # Giovanni, with actual printed order still own then opponent.
    ordinary = make_pokemon("plain", "Plain", tags={"Basic"})
    unprotected = make_board(defender_active, (ordinary,))
    full = execute_protected_paired_switch(
        player, unprotected, budget, PROGRAMS["Team Rocket's Giovanni"],
        own_promote_id="own-b", opponent_promote_id="plain",
    )
    assert full.transaction is not None
    assert full.transaction.effect_sequence == ("own", "opponent")
    assert not full.denied_second_effect
    assert full.transaction.opponent_board.active_id == "plain"

    # Active Togekiss protects Bench versus Items only.
    tog = make_pokemon(
        "tog", "Togekiss", print_id="bw8-104", tags={"Stage2"},
    )
    tog_board = make_board(tog, (ordinary,))
    for name, expect in (("Prime Catcher", False), ("Guzma", True)):
        action = execute_protected_paired_switch(
            player, tog_board, budget, PROGRAMS[name],
            own_promote_id="own-b", opponent_promote_id="plain",
        )
        assert (action.transaction is not None) == expect, name

    # Active Diancie reverses the Item/Supporter split for Basic Bench.
    dia = make_pokemon(
        "dia", "Diancie", print_id="swsh10-68", tags={"Basic"},
    )
    dia_board = make_board(dia, (ordinary,))
    for name, expect in (("Prime Catcher", True), ("Guzma", False)):
        action = execute_protected_paired_switch(
            player, dia_board, budget, PROGRAMS[name],
            own_promote_id="own-b", opponent_promote_id="plain",
        )
        assert (action.transaction is not None) == expect, name

    # Ordinary Supporter quota is still obeyed before the partial own switch.
    spent = TurnActionBudget(supporter_used=True)
    denied_quota = execute_protected_paired_switch(
        player, defender, spent, PROGRAMS["Team Rocket's Giovanni"],
        own_promote_id="own-b", opponent_promote_id="axew",
    )
    assert denied_quota.transaction is None

    print(
        "protected_paired_switch_execution regression: PASS; "
        "partial Giovanni pays Supporter and preserves own switch; "
        "opponent-first actions stop; Item/Supporter protections crossed"
    )


if __name__ == "__main__":
    main()
