"""Melt Away: overpaying Retreat can create future zero-cost Retreat."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (
    EnergyAttachment, knock_out, make_board, make_pokemon, next_turn,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_cost_semantics import effective_retreat_cost
from retreat_energy_transaction import RetreatEnergyTransactionState
from retreat_environment_modifiers import derive_environment_retreat_modifiers
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def initial_state(print_id: str = "sv10-36") -> RetreatEnergyTransactionState:
    energies = (
        EnergyAttachment("dce", "Double Colorless Energy", ("C", "C"), "bw4-92"),
        EnergyAttachment("basic1", "Basic Psychic Energy", ("P",)),
        EnergyAttachment("basic2", "Basic Psychic Energy", ("P",)),
    )
    holder = make_pokemon(
        "magcargo", "Ethan's Magcargo", print_id=print_id,
        tags=("Stage1",), energy=energies,
    )
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                ("basic", "attached"): 2,
                ("dce", "attached"): 1,
            }),
            board=make_board(
                holder,
                (make_pokemon("pivot", "Pivot"), make_pokemon("backup", "Backup")),
            ),
            instance_classes=(
                ("basic1", "basic"), ("basic2", "basic"), ("dce", "dce"),
            ),
        ),
    )


def reestablish_as_active(
    state: RetreatEnergyTransactionState,
    *,
    suppress_melt_away: bool = False,
) -> RetreatEnergyTransactionState:
    # An opponent subsequently KOs Pivot and takes a Prize, causing
    # Magcargo to be promoted. This models board topology and
    # a new turn without inferring unrepresented combat damage.
    board, removed = knock_out(
        state.energy.board, "pivot", promote_object_id="magcargo"
    )
    assert board is not None and removed.object_id == "pivot"
    board = next_turn(board)
    if suppress_melt_away:
        board = replace(
            board,
            objects=tuple(
                replace(p, abilities_enabled=False)
                if p.object_id == "magcargo" else p
                for p in board.objects
            ),
        )
        board.validate()
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=state.energy.zones,
            board=board,
            instance_classes=state.energy.instance_classes,
        ),
    )


def main() -> None:
    start = initial_state()
    opponent = make_board(make_pokemon("opponent", "Opponent"))
    first = enumerate_board_derived_retreat_actions(
        start, opponent, base_retreat_cost=3,
    )
    assert first.information_complete
    assert first.preflight is not None
    assert first.preflight.effective_retreat_cost == 3

    pivot_actions = {
        frozenset(action.discard_energy_ids): action
        for action in first.actions if action.bench_object_id == "pivot"
    }
    assert set(pivot_actions) == {
        frozenset(("dce", "basic1")),
        frozenset(("dce", "basic2")),
        frozenset(("dce", "basic1", "basic2")),
    }

    overpayment = frozenset(("dce", "basic1", "basic2"))
    for payment, action in pivot_actions.items():
        tx = action.attempt.transaction
        assert tx is not None and tx.committed
        state = reestablish_as_active(tx.state)
        remaining = len(state.energy.board.get("magcargo").energy)
        expected = 0 if payment == overpayment else 1
        assert remaining == expected

        next_actions = enumerate_board_derived_retreat_actions(
            state, opponent, base_retreat_cost=3,
            stadium_print_id="swsh2-160",  # Galar Mine +2
        )
        assert next_actions.preflight is not None
        if payment == overpayment:
            assert next_actions.preflight.effective_retreat_cost == 0
            assert {
                (row.bench_object_id, row.discard_energy_ids)
                for row in next_actions.actions
            } == {("backup", ())}
            # D-13 no-cost wording takes priority even over Galar Mine.
            mods = derive_environment_retreat_modifiers(
                state.energy.board, opponent, stadium_print_id="swsh2-160"
            )
            assert effective_retreat_cost(3, mods) == 0

            denied = reestablish_as_active(
                tx.state, suppress_melt_away=True,
            )
            suppressed = enumerate_board_derived_retreat_actions(
                denied, opponent, base_retreat_cost=3,
                stadium_print_id="swsh2-160",
            )
            assert suppressed.preflight is not None
            assert suppressed.preflight.effective_retreat_cost == 5
            assert not suppressed.actions
        else:
            assert next_actions.preflight.effective_retreat_cost == 5
            assert not next_actions.actions

    decisive = pivot_actions[overpayment].attempt.transaction
    assert decisive is not None
    energy_free = reestablish_as_active(decisive.state)
    for recognized_print in ("sv10-36", "me2pt5-24", "me2pt5-222"):
        recognized_board = replace(
            energy_free.energy.board,
            objects=tuple(
                replace(p, print_id=recognized_print)
                if p.object_id == "magcargo" else p
                for p in energy_free.energy.board.objects
            ),
        )
        assert effective_retreat_cost(
            3, derive_environment_retreat_modifiers(
                recognized_board, opponent,
            )
        ) == 0
    unverified_board = replace(
        energy_free.energy.board,
        objects=tuple(
            replace(p, print_id="unverified")
            if p.object_id == "magcargo" else p
            for p in energy_free.energy.board.objects
        ),
    )
    assert not derive_environment_retreat_modifiers(
        unverified_board, opponent,
    )
    print("Ethan's Magcargo Melt Away payment reverses Energy-retention monotonicity: PASS")
    print({"initial_pivot_payments": len(pivot_actions),
           "future_cost_with_one_energy": 5,
           "future_cost_without_energy": 0,
           "future_free_retreat_actions": 1})


if __name__ == "__main__":
    main()
