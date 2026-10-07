"""Reproduce board-derived Special Energy Retreat Cost modifiers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from attached_energy_retreat_modifiers import (
    ATTACHED_ENERGY_RETREAT_RULES,
    attached_energy_retreat_modifiers,
)
from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_cost_semantics import effective_retreat_cost
from retreat_energy_normalization import normalize_retreat_energy_state
from retreat_energy_transaction import (
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def state(
    card_name: str,
    print_id: str,
    *,
    holder_tags: tuple[str, ...],
    units: int = 1,
) -> RetreatEnergyTransactionState:
    energy = EnergyAttachment(
        "energy",
        card_name,
        ("C",) * units,
        print_id=print_id,
    )
    holder = make_pokemon(
        "holder",
        "Holder",
        tags=holder_tags,
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
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=energy_state,
    )


def cost(state: RetreatEnergyTransactionState, base: int) -> int:
    active = state.energy.board.get(state.energy.board.active_id)
    return effective_retreat_cost(
        base,
        attached_energy_retreat_modifiers(active),
    )


def main() -> None:
    assert {
        (rule.print_id, rule.card_name)
        for rule in ATTACHED_ENERGY_RETREAT_RULES
    } == {
        ("me4-85", "Magnetic Metal Energy"),
        ("swsh3-175", "Hiding Darkness Energy"),
        ("xy4-112", "Mystery Energy"),
    }

    psychic = state(
        "Mystery Energy",
        "xy4-112",
        holder_tags=("Psychic",),
    )
    assert cost(psychic, 2) == 0
    free = retreat_with_energy_destinations(
        psychic,
        "pivot",
        retreat_cost=cost(psychic, 2),
        discard_energy_ids=(),
    )
    assert free is not None and free.committed
    assert free.state.energy.zones.count("energy-class", "attached") == 1

    # A stale Mystery attachment on a non-Psychic holder must self-discard
    # during normalization before its -2 modifier can be derived.
    stale = state(
        "Mystery Energy",
        "xy4-112",
        holder_tags=("Colorless",),
    )
    assert cost(stale, 2) == 2
    normalized = normalize_retreat_energy_state(stale)
    assert normalized.state.energy.board.get("holder").energy == ()
    assert normalized.state.energy.zones.count("energy-class", "discard") == 1
    assert cost(normalized.state, 2) == 2
    assert retreat_with_energy_destinations(
        normalized.state,
        "pivot",
        retreat_cost=2,
        discard_energy_ids=(),
    ) is None

    metal = state(
        "Magnetic Metal Energy",
        "me4-85",
        holder_tags=("Metal",),
    )
    assert cost(metal, 4) == 0

    non_metal = state(
        "Magnetic Metal Energy",
        "me4-85",
        holder_tags=("Colorless",),
    )
    assert cost(non_metal, 4) == 4

    darkness = state(
        "Hiding Darkness Energy",
        "swsh3-175",
        holder_tags=("Darkness",),
    )
    assert cost(darkness, 3) == 0

    print(json.dumps({
        "attached_energy_retreat_modifier_prints": 3,
        "mystery_psychic_base_2": 0,
        "mystery_non_psychic_base_2": 2,
        "magnetic_metal_base_4": 0,
        "hiding_darkness_base_3": 0,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
