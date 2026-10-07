"""Reproduce conserved Retreat Energy destination transactions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_object_kernel import (
    EnergyAttachment,
    ToolAttachment,
    make_board,
    make_pokemon,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_energy_transaction import (
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import make_state


def dce_state(*, damage_counters: int = 0) -> RetreatEnergyTransactionState:
    dce_a = EnergyAttachment(
        "dce-a",
        "Double Colorless Energy",
        ("C", "C"),
    )
    dce_b = EnergyAttachment(
        "dce-b",
        "Double Colorless Energy",
        ("C", "C"),
    )
    pouch = ToolAttachment("pouch", "Dashing Pouch")
    active = make_pokemon(
        "active",
        "Retreating Pokemon",
        energy=(dce_a, dce_b),
        tool=pouch,
        damage_counters=damage_counters,
        special_conditions=("Poisoned",),
        temporary_attack_lock=True,
    )
    bench = make_pokemon("bench", "Pivot")
    energy = EnergyBoardState(
        zones=ZoneCountState.from_mapping({
            ("dce-class", "attached"): 2,
        }),
        board=make_board(active, (bench,)),
        instance_classes=(
            ("dce-a", "dce-class"),
            ("dce-b", "dce-class"),
        ),
    )
    unified = make_state({}, turn_budget=TurnActionBudget())
    return RetreatEnergyTransactionState(unified=unified, energy=energy)


def prism_state(*, damage_counters: int = 0) -> RetreatEnergyTransactionState:
    prism = EnergyAttachment(
        "prism",
        "Super Boost Energy Prism Star",
        ("C",),
    )
    pouch = ToolAttachment("pouch-prism", "Dashing Pouch")
    active = make_pokemon(
        "active-prism",
        "Prism Holder",
        energy=(prism,),
        tool=pouch,
        damage_counters=damage_counters,
    )
    bench = make_pokemon("bench-prism", "Pivot")
    energy = EnergyBoardState(
        zones=ZoneCountState.from_mapping({
            ("prism-class", "attached"): 1,
        }),
        board=make_board(active, (bench,)),
        instance_classes=(("prism", "prism-class"),),
    )
    unified = make_state({}, turn_budget=TurnActionBudget())
    return RetreatEnergyTransactionState(unified=unified, energy=energy)


def main() -> None:
    start = dce_state()

    both = retreat_with_energy_destinations(
        start,
        "bench",
        retreat_cost=2,
        discard_energy_ids=("dce-a", "dce-b"),
    )
    assert both is not None and both.committed
    assert both.state.energy.zones.count("dce-class", "hand") == 2
    assert both.state.energy.zones.count("dce-class", "attached") == 0
    assert both.state.energy.instance_classes == ()
    assert both.state.unified.turn_budget is not None
    assert both.state.unified.turn_budget.retreats_used == 1
    assert not both.state.unified.turn_budget.can(TurnAction.RETREAT)
    assert both.state.energy.board.retreat_used
    moved = both.state.energy.board.get("active")
    assert moved.tool is not None and moved.tool.card_name == "Dashing Pouch"
    assert not moved.special_conditions
    assert not moved.pokemon_state.temporary_attack_lock
    assert {row.destination_zone for row in both.destinations} == {"hand"}

    one = retreat_with_energy_destinations(
        start,
        "bench",
        retreat_cost=2,
        discard_energy_ids=("dce-a",),
    )
    assert one is not None and one.committed
    assert one.state.energy.zones.count("dce-class", "hand") == 1
    assert one.state.energy.zones.count("dce-class", "attached") == 1
    assert one.state.energy.instance_classes == (("dce-b", "dce-class"),)
    assert [
        row.instance_id
        for row in one.state.energy.board.get("active").energy
    ] == ["dce-b"]

    blocked_start = dce_state(damage_counters=1)
    blocked = retreat_with_energy_destinations(
        blocked_start,
        "bench",
        retreat_cost=2,
        discard_energy_ids=("dce-a",),
        opposing_scoop_up_block_active=True,
    )
    assert blocked is not None and blocked.committed
    assert blocked.state.energy.zones.count("dce-class", "discard") == 1
    assert blocked.state.energy.zones.count("dce-class", "hand") == 0

    prism_start = prism_state()
    unresolved = retreat_with_energy_destinations(
        prism_start,
        "bench-prism",
        retreat_cost=1,
        discard_energy_ids=("prism",),
        prism_star_energy_ids=("prism",),
    )
    assert unresolved is not None and not unresolved.committed
    assert unresolved.state == prism_start
    assert unresolved.state.unified.turn_budget is not None
    assert unresolved.state.unified.turn_budget.retreats_used == 0
    assert len(unresolved.conflicts) == 1

    prism_blocked_start = prism_state(damage_counters=1)
    prism_blocked = retreat_with_energy_destinations(
        prism_blocked_start,
        "bench-prism",
        retreat_cost=1,
        discard_energy_ids=("prism",),
        opposing_scoop_up_block_active=True,
        prism_star_energy_ids=("prism",),
    )
    assert prism_blocked is not None and prism_blocked.committed
    assert prism_blocked.state.energy.zones.count(
        "prism-class",
        "lost_zone",
    ) == 1
    assert prism_blocked.state.energy.zones.count(
        "prism-class",
        "attached",
    ) == 0

    print("retreat Energy transaction regression: PASS")


if __name__ == "__main__":
    main()
