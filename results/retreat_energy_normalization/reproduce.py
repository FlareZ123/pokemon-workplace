"""Reproduce attachment validation plus provider refresh before Retreat."""

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
from retreat_energy_normalization import normalize_retreat_energy_state
from retreat_energy_transaction import (
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def state(
    energies: tuple[EnergyAttachment, ...],
    *,
    holder_tags: tuple[str, ...],
    classes: tuple[tuple[str, str], ...],
) -> RetreatEnergyTransactionState:
    holder = make_pokemon(
        "holder",
        "Holder",
        tags=holder_tags,
        energy=energies,
    )
    pivot = make_pokemon("pivot", "Pivot")
    counts = {}
    for _instance_id, card_class in classes:
        counts[(card_class, "attached")] = (
            counts.get((card_class, "attached"), 0) + 1
        )
    energy_state = EnergyBoardState(
        zones=ZoneCountState.from_mapping(counts),
        board=make_board(holder, (pivot,)),
        instance_classes=tuple(sorted(classes)),
    )
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=energy_state,
    )


def main() -> None:
    # Stale illegal Triple Acceleration must disappear before provider refresh.
    triple = EnergyAttachment(
        "triple",
        "Triple Acceleration Energy",
        ("C", "C", "C"),
        print_id="sm10-190",
    )
    illegal = state(
        (triple,),
        holder_tags=("Basic",),
        classes=(("triple", "triple-class"),),
    )
    normalized_illegal = normalize_retreat_energy_state(illegal)
    assert [row.instance_id for row in normalized_illegal.restriction_discards] == [
        "triple"
    ]
    assert normalized_illegal.provider_refreshes == ()
    assert normalized_illegal.state.energy.board.get("holder").energy == ()
    assert normalized_illegal.state.energy.zones.count(
        "triple-class", "discard"
    ) == 1
    assert retreat_with_energy_destinations(
        normalized_illegal.state,
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("triple",),
    ) is None

    # A surviving Ignition Energy changes provider mode after the holder evolves.
    ignition = EnergyAttachment(
        "ignition",
        "Ignition Energy",
        ("C",),
        print_id="me2-124",
    )
    evolution = state(
        (ignition,),
        holder_tags=("Stage1",),
        classes=(("ignition", "ignition-class"),),
    )
    normalized_evolution = normalize_retreat_energy_state(evolution)
    assert normalized_evolution.restriction_discards == ()
    assert len(normalized_evolution.provider_refreshes) == 1
    refresh = normalized_evolution.provider_refreshes[0]
    assert refresh.instance_id == "ignition"
    assert len(refresh.before_units) == 1
    assert len(refresh.after_units) == 3

    legal = retreat_with_energy_destinations(
        normalized_evolution.state,
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("ignition",),
    )
    assert legal is not None and legal.committed

    # Mixed state proves discarded cards cannot be resurrected by refresh.
    mixed = state(
        (triple, ignition),
        holder_tags=("Stage1",),
        classes=(
            ("ignition", "ignition-class"),
            ("triple", "triple-class"),
        ),
    )
    mixed_norm = normalize_retreat_energy_state(mixed)
    assert mixed_norm.restriction_discards == ()
    assert [row.instance_id for row in mixed_norm.provider_refreshes] == [
        "ignition"
    ]

    print(json.dumps({
        "normalization_order": [
            "attachment_restriction",
            "provider_refresh",
        ],
        "illegal_triple_acceleration_removed_before_payment": True,
        "ignition_stage1_refreshed_to_units": 3,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
