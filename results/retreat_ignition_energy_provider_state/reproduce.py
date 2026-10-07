"""Reproduce dynamic Ignition Energy Retreat provider state."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_object_kernel import (
    EnergyAttachment,
    evolve,
    make_board,
    make_pokemon,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_dynamic_energy_units import (
    IGNITION_ENERGY_PRINT_IDS,
    refresh_active_retreat_energy_units,
    retreat_with_dynamic_energy_units,
)
from retreat_energy_transaction import (
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def make_actor(
    *,
    tags=("Basic",),
    units=("C",),
    print_id="me2-124",
) -> RetreatEnergyTransactionState:
    ignition = EnergyAttachment(
        "ignition",
        "Ignition Energy",
        tuple(units),
        print_id=print_id,
    )
    active = make_pokemon(
        "holder",
        "Holder",
        tags=tags,
        energy=(ignition,),
    )
    pivot = make_pokemon("pivot", "Pivot")
    board = make_board(active, (pivot,))
    energy = EnergyBoardState(
        zones=ZoneCountState.from_mapping({
            ("ignition-class", "attached"): 1,
        }),
        board=board,
        instance_classes=(("ignition", "ignition-class"),),
    )
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=energy,
    )


def with_evolved_holder(
    state: RetreatEnergyTransactionState,
) -> RetreatEnergyTransactionState:
    evolved = evolve(
        state.energy.board,
        "holder",
        new_card_name="Stage 1 Holder",
        new_tags=("Stage1",),
    )
    assert evolved is not None
    return RetreatEnergyTransactionState(
        unified=state.unified,
        energy=EnergyBoardState(
            zones=state.energy.zones,
            board=evolved,
            instance_classes=state.energy.instance_classes,
        ),
    )


def main() -> None:
    assert IGNITION_ENERGY_PRINT_IDS == frozenset({
        "rsv10pt5-86",
        "me2-124",
    })

    basic = make_actor()
    evolved = with_evolved_holder(basic)

    # Evolution preserves the physical attachment, so the stored one-unit
    # snapshot is stale immediately after the holder changes Stage.
    assert evolved.energy.board.get("holder").energy[0].units == ("C",)

    stale_false_negative = retreat_with_energy_destinations(
        evolved,
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("ignition",),
    )
    assert stale_false_negative is None

    refreshed = refresh_active_retreat_energy_units(evolved)
    assert refreshed.energy.board.get("holder").energy[0].units == (
        "C", "C", "C"
    )

    resolved = retreat_with_dynamic_energy_units(
        evolved,
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("ignition",),
    )
    assert resolved is not None and resolved.committed
    assert resolved.state.energy.zones.count(
        "ignition-class", "discard"
    ) == 1

    # The opposite stale snapshot would create a false positive on a Basic.
    stale_basic = make_actor(tags=("Basic",), units=("C", "C", "C"))
    direct_false_positive = retreat_with_energy_destinations(
        stale_basic,
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("ignition",),
    )
    assert direct_false_positive is not None

    corrected_basic = retreat_with_dynamic_energy_units(
        stale_basic,
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("ignition",),
    )
    assert corrected_basic is None

    # Exact print identity is required; a same-name unknown print is not
    # silently rewritten.
    unknown_print = make_actor(
        tags=("Stage1",),
        units=("C",),
        print_id="unknown-ignition",
    )
    unchanged = refresh_active_retreat_energy_units(unknown_print)
    assert unchanged.energy.board.get("holder").energy[0].units == ("C",)
    assert retreat_with_dynamic_energy_units(
        unknown_print,
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("ignition",),
    ) is None

    print(json.dumps({
        "supported_prints": sorted(IGNITION_ENERGY_PRINT_IDS),
        "basic_units": 1,
        "evolution_units": 3,
        "stale_post_evolution_core_result": "illegal",
        "refreshed_post_evolution_result": "legal",
        "stale_basic_core_result": "legal",
        "refreshed_basic_result": "illegal",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
