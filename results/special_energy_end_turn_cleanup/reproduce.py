"""Reproduce Special Energy end-of-turn cleanup."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from special_energy_end_turn_catalog import build as build_catalog
from special_energy_end_turn_cleanup import (
    END_TURN_SPECIAL_ENERGY_RULES,
    cleanup_end_turn_special_energy,
)
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import make_state


def state(
    card_name: str,
    print_id: str,
    *,
    ended: bool,
) -> RetreatEnergyTransactionState:
    energy = EnergyAttachment(
        "energy",
        card_name,
        ("C",),
        print_id=print_id,
    )
    holder = make_pokemon(
        "holder",
        "Holder",
        energy=(energy,),
    )
    pivot = make_pokemon("pivot", "Pivot")
    energy_state = EnergyBoardState(
        zones=ZoneCountState.from_mapping({
            ("energy-class", "attached"): 1,
        }),
        board=make_board(holder, (pivot,)),
        instance_classes=(("energy", "energy-class"),),
    )
    budget = TurnActionBudget()
    if ended:
        budget = budget.consume(TurnAction.END_TURN)
        assert budget is not None
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=budget),
        energy=energy_state,
    )


def main() -> None:
    catalog = build_catalog(ROOT / "resources")
    catalog_rows = {
        (
            row["card_id"],
            row["card_name"],
            row["attachment_turn_only"],
        )
        for row in catalog["rows"]
    }
    runtime_rows = {
        (
            rule.print_id,
            rule.card_name,
            rule.attachment_turn_only,
        )
        for rule in END_TURN_SPECIAL_ENERGY_RULES
    }
    assert catalog["print_rows"] == 4
    assert catalog["distinct_names"] == 3
    assert catalog_rows == runtime_rows

    open_turn = cleanup_end_turn_special_energy(
        state("Triple Acceleration Energy", "sm10-190", ended=False)
    )
    assert open_turn is None

    triple = cleanup_end_turn_special_energy(
        state("Triple Acceleration Energy", "sm10-190", ended=True)
    )
    assert triple is not None
    assert [row.instance_id for row in triple.discarded] == ["energy"]
    assert triple.state.energy.instance_classes == ()
    assert triple.state.energy.zones.count("energy-class", "attached") == 0
    assert triple.state.energy.zones.count("energy-class", "discard") == 1

    aqua_attached_now = cleanup_end_turn_special_energy(
        state("Double Aqua Energy", "dc1-33", ended=True),
        attached_this_turn_ids=("energy",),
    )
    assert aqua_attached_now is not None
    assert [row.instance_id for row in aqua_attached_now.discarded] == ["energy"]

    aqua_old = cleanup_end_turn_special_energy(
        state("Double Aqua Energy", "dc1-33", ended=True),
        attached_this_turn_ids=(),
    )
    assert aqua_old is not None
    assert aqua_old.discarded == ()
    assert aqua_old.state.energy.zones.count("energy-class", "attached") == 1

    magma_attached_now = cleanup_end_turn_special_energy(
        state("Double Magma Energy", "dc1-34", ended=True),
        attached_this_turn_ids=("energy",),
    )
    assert magma_attached_now is not None
    assert [row.instance_id for row in magma_attached_now.discarded] == ["energy"]

    unknown = cleanup_end_turn_special_energy(
        state("Triple Acceleration Energy", "unknown", ended=True),
        attached_this_turn_ids=("energy",),
    )
    assert unknown is not None
    assert unknown.discarded == ()

    print(json.dumps({
        "catalog_print_rows": catalog["print_rows"],
        "catalog_distinct_names": catalog["distinct_names"],
        "triple_acceleration_end_turn": "discard",
        "double_aqua_attached_this_turn": "discard",
        "double_aqua_without_provenance": "preserve",
        "open_turn_cleanup": "rejected",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
