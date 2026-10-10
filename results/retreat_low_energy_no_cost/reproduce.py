"""Low-Energy Abilities and Golisopod's nonempty threshold crossing."""
from __future__ import annotations

from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (
    EnergyAttachment, make_board, make_pokemon, knock_out, next_turn,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_attached_energy_free_cost import (
    LOW_ENERGY_NO_RETREAT_SOURCES, derive_attached_energy_threshold_no_cost,
)
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def source_tests() -> None:
    single = EnergyAttachment("basic", "Basic Energy", ("P",))
    double = EnergyAttachment("dce", "Double Colorless Energy", ("C", "C"))
    for source in LOW_ENERGY_NO_RETREAT_SOURCES:
        def holder(energy=(), enabled=True):
            return make_pokemon(
                "holder", source.card_name, print_id=source.print_id,
                energy=energy, abilities_enabled=enabled,
            )
        assert derive_attached_energy_threshold_no_cost(holder()) is not None
        assert derive_attached_energy_threshold_no_cost(holder(enabled=False)) is None
        if source.max_attached_units == 0:
            assert derive_attached_energy_threshold_no_cost(holder((single,))) is None
        else:
            assert derive_attached_energy_threshold_no_cost(holder((single,))) is not None
            assert derive_attached_energy_threshold_no_cost(holder((double,))) is not None
            assert derive_attached_energy_threshold_no_cost(
                holder((single, double))
            ) is None  # 3 Energy units, despite only two Energy cards.
    assert derive_attached_energy_threshold_no_cost(
        make_pokemon("holder", "Golisopod", print_id="unverified")
    ) is None


def physical_golisopod() -> None:
    energy = (
        EnergyAttachment("dce1", "Double Colorless Energy", ("C", "C"), "bw4-92"),
        EnergyAttachment("dce2", "Double Colorless Energy", ("C", "C"), "bw4-92"),
        EnergyAttachment("b1", "Basic Psychic Energy", ("P",)),
        EnergyAttachment("b2", "Basic Psychic Energy", ("P",)),
        EnergyAttachment("b3", "Basic Psychic Energy", ("P",)),
    )
    holder = make_pokemon(
        "golisopod", "Golisopod", print_id="sm11-51",
        tags=("Stage1",), energy=energy,
    )
    state = RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=ZoneCountState.from_mapping({
                ("basic", "attached"): 3, ("dce", "attached"): 2,
            }),
            board=make_board(holder, (
                make_pokemon("pivot", "Pivot"),
                make_pokemon("backup", "Backup"),
            )),
            instance_classes=(
                ("b1", "basic"), ("b2", "basic"), ("b3", "basic"),
                ("dce1", "dce"), ("dce2", "dce"),
            ),
        ),
    )
    opponent = make_board(make_pokemon("opponent", "Opponent"))
    first = enumerate_board_derived_retreat_actions(
        state, opponent, base_retreat_cost=4,
    )
    assert first.preflight is not None
    assert first.preflight.effective_retreat_cost == 4

    chosen = {}
    for action in first.actions:
        if action.bench_object_id != "pivot":
            continue
        payment = frozenset(action.discard_energy_ids)
        if payment in (
            frozenset(("dce1", "dce2")),
            frozenset(("dce1", "dce2", "b1")),
        ):
            chosen[payment] = action
    assert len(chosen) == 2

    for paid, action in chosen.items():
        tx = action.attempt.transaction
        assert tx is not None and tx.committed
        board, knocked = knock_out(
            tx.state.energy.board, "pivot", promote_object_id="golisopod"
        )
        assert board is not None and knocked.object_id == "pivot"
        board = next_turn(board)
        new = RetreatEnergyTransactionState(
            unified=make_state({}, turn_budget=TurnActionBudget()),
            energy=EnergyBoardState(
                zones=tx.state.energy.zones, board=board,
                instance_classes=tx.state.energy.instance_classes,
            ),
        )
        future = enumerate_board_derived_retreat_actions(
            new, opponent, base_retreat_cost=4,
            stadium_print_id="swsh2-160",  # Galar Mine +2
        )
        assert future.preflight is not None
        paid_extra = "b1" in paid
        remaining_units = sum(
            len(e.units) for e in board.get("golisopod").energy
        )
        assert remaining_units == (2 if paid_extra else 3)
        assert future.preflight.effective_retreat_cost == (
            0 if paid_extra else 6
        )
        assert (
            {(r.bench_object_id, r.discard_energy_ids) for r in future.actions}
            == ({("backup", ())} if paid_extra else set())
        )


def main() -> None:
    source_tests()
    physical_golisopod()
    print("Low-Energy free-Retreat source bridge: PASS")
    print({"recognized_prints": 10, "golisopod_before_payment_units": 7,
           "future_units_minimal_vs_larger": (3, 2),
           "future_cost_minimal_vs_larger_with_galar_mine": (6, 0)})


if __name__ == "__main__":
    main()
