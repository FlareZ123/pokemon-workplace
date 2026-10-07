"""Regression for board-derived Retreat execution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_derived_retreat import attempt_board_derived_retreat
from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_cost_semantics import RetreatCostModifier
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def actor(energies, *, tags=(), tool=None, damage=0):
    active = make_pokemon(
        "active", "Holder", tags=tags, energy=tuple(energies),
        tool=tool, damage_counters=damage,
    )
    pivot = make_pokemon("pivot", "Pivot")
    classes = tuple(
        sorted((energy.instance_id, "class-" + energy.instance_id)
               for energy in energies)
    )
    zones = ZoneCountState.from_mapping({
        (card_class, "attached"): 1
        for _instance_id, card_class in classes
    })
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=EnergyBoardState(
            zones=zones,
            board=make_board(active, (pivot,)),
            instance_classes=classes,
        ),
    )


def blank_opponent():
    return make_board(make_pokemon("opponent", "Opponent Active"))


def main() -> None:
    triple = EnergyAttachment(
        "triple", "Triple Acceleration Energy",
        ("C", "C", "C"), print_id="sm10-190",
    )
    attempt = attempt_board_derived_retreat(
        actor((triple,), tags=("Basic",)),
        "pivot",
        base_retreat_cost=3,
        discard_energy_ids=("triple",),
        opponent_board=blank_opponent(),
    )
    assert attempt.transaction is None
    assert attempt.normalization.state.energy.zones.count(
        "class-triple", "discard"
    ) == 1

    ignition = EnergyAttachment(
        "ignition", "Ignition Energy", ("C",), print_id="me2-124",
    )
    attempt = attempt_board_derived_retreat(
        actor((ignition,), tags=("Stage1",)),
        "pivot",
        base_retreat_cost=3,
        discard_energy_ids=("ignition",),
        opponent_board=blank_opponent(),
    )
    assert len(attempt.normalization.provider_refreshes) == 1
    assert attempt.transaction is not None and attempt.transaction.committed

    mystery = EnergyAttachment(
        "mystery", "Mystery Energy", ("P",), print_id="xy4-112",
    )
    attempt = attempt_board_derived_retreat(
        actor((mystery,), tags=("Psychic",)),
        "pivot",
        base_retreat_cost=2,
        discard_energy_ids=(),
        opponent_board=blank_opponent(),
    )
    assert attempt.effective_retreat_cost == 0
    assert attempt.transaction is not None and attempt.transaction.committed

    attempt = attempt_board_derived_retreat(
        actor((mystery,), tags=("Psychic",)),
        "pivot",
        base_retreat_cost=2,
        discard_energy_ids=("mystery",),
        opponent_board=blank_opponent(),
        external_modifiers=(RetreatCostModifier("Galar Mine", delta=2),),
    )
    assert attempt.effective_retreat_cost == 2
    assert attempt.transaction is None

    air = ToolAttachment("air", "Air Balloon", print_id="swsh1-156")
    attempt = attempt_board_derived_retreat(
        actor((), tool=air),
        "pivot",
        base_retreat_cost=2,
        discard_energy_ids=(),
        opponent_board=blank_opponent(),
    )
    assert attempt.effective_retreat_cost == 0
    assert attempt.unresolved_tool_conditions == ()
    assert attempt.transaction is not None and attempt.transaction.committed

    rescue = ToolAttachment("rescue", "Rescue Board", print_id="sv5-159")
    attempt = attempt_board_derived_retreat(
        actor((), tool=rescue),
        "pivot",
        base_retreat_cost=1,
        discard_energy_ids=(),
        opponent_board=blank_opponent(),
    )
    assert len(attempt.unresolved_tool_conditions) == 1
    assert attempt.transaction is None

    attempt = attempt_board_derived_retreat(
        actor((), tool=rescue),
        "pivot",
        base_retreat_cost=1,
        discard_energy_ids=(),
        opponent_board=blank_opponent(),
        active_remaining_hp=30,
    )
    assert attempt.effective_retreat_cost == 0
    assert attempt.unresolved_tool_conditions == ()
    assert attempt.transaction is not None and attempt.transaction.committed

    dce = EnergyAttachment("dce", "Double Colorless Energy", ("C", "C"))
    pouch = ToolAttachment("pouch", "Dashing Pouch")
    mime = make_pokemon("mime", "Mr. Mime", print_id="sm9-66")
    opponent = make_board(make_pokemon("opp", "Opponent"), (mime,))
    attempt = attempt_board_derived_retreat(
        actor((dce,), tool=pouch, damage=1),
        "pivot",
        base_retreat_cost=2,
        discard_energy_ids=("dce",),
        opponent_board=opponent,
    )
    assert attempt.scoop_up_block_source_ids == ("mime",)
    assert attempt.transaction is not None and attempt.transaction.committed
    assert attempt.transaction.destinations[0].destination_zone == "discard"

    print("board-derived Retreat regression: PASS")


if __name__ == "__main__":
    main()
