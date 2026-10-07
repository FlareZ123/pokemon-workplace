"""Reproduce holder-restricted Special Energy revalidation."""

from __future__ import annotations

from dataclasses import replace
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from board_object_kernel import (
    EnergyAttachment,
    make_board,
    make_pokemon,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from restricted_special_energy_attachment import (
    RESTRICTED_SPECIAL_ENERGY_RULES,
    revalidate_restricted_special_energy,
)
from restricted_special_energy_catalog import build as build_catalog
from retreat_energy_transaction import (
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def energy_state(
    *,
    card_name: str,
    print_id: str,
    units: int,
    holder_tags: tuple[str, ...],
) -> EnergyBoardState:
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
    return EnergyBoardState(
        zones=ZoneCountState.from_mapping({
            ("energy-class", "attached"): 1,
        }),
        board=make_board(holder, (pivot,)),
        instance_classes=(("energy", "energy-class"),),
    )


def retag_holder(
    state: EnergyBoardState,
    tags: tuple[str, ...],
) -> EnergyBoardState:
    holder = state.board.get("holder")
    next_holder = replace(holder, tags=frozenset(tags))
    board = replace(
        state.board,
        objects=tuple(
            next_holder if row.object_id == "holder" else row
            for row in state.board.objects
        ),
    )
    board.validate()
    return EnergyBoardState(
        zones=state.zones,
        board=board,
        instance_classes=state.instance_classes,
    )


def retreat_state(state: EnergyBoardState) -> RetreatEnergyTransactionState:
    return RetreatEnergyTransactionState(
        unified=make_state({}, turn_budget=TurnActionBudget()),
        energy=state,
    )


def main() -> None:
    catalog = build_catalog(ROOT / "resources")
    catalog_rows = {
        (row["card_id"], row["card_name"], row["required_tag"])
        for row in catalog["rows"]
    }
    runtime_rows = {
        (rule.print_id, rule.card_name, rule.required_tag)
        for rule in RESTRICTED_SPECIAL_ENERGY_RULES
    }
    assert catalog["print_rows"] == 24
    assert catalog["distinct_names"] == 19
    assert catalog_rows == runtime_rows

    # Triple Acceleration is legal on an Evolution holder.
    legal_tae = energy_state(
        card_name="Triple Acceleration Energy",
        print_id="sm10-190",
        units=3,
        holder_tags=("Stage1",),
    )
    legal_result = revalidate_restricted_special_energy(legal_tae)
    assert legal_result.state == legal_tae
    assert legal_result.discarded == ()

    # Model a completed holder mutation such as devolution. The physical Energy
    # attachment persists in the raw state, then its own restriction must
    # normalize it away before subsequent actions.
    stale_basic = retag_holder(legal_tae, ("Basic",))

    raw_retreat = retreat_with_energy_destinations(
        retreat_state(stale_basic),
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("energy",),
    )
    assert raw_retreat is not None and raw_retreat.committed

    normalized = revalidate_restricted_special_energy(stale_basic)
    assert [row.instance_id for row in normalized.discarded] == ["energy"]
    assert normalized.state.board.get("holder").energy == ()
    assert normalized.state.instance_classes == ()
    assert normalized.state.zones.count("energy-class", "attached") == 0
    assert normalized.state.zones.count("energy-class", "discard") == 1

    blocked_retreat = retreat_with_energy_destinations(
        retreat_state(normalized.state),
        "pivot",
        retreat_cost=3,
        discard_energy_ids=("energy",),
    )
    assert blocked_retreat is None

    # Type-restricted Energy remains when the current holder has the exact tag.
    dragon = energy_state(
        card_name="Double Dragon Energy",
        print_id="xy6-97",
        units=2,
        holder_tags=("Dragon",),
    )
    assert revalidate_restricted_special_energy(dragon).state == dragon

    non_dragon = retag_holder(dragon, ("Colorless",))
    removed_dde = revalidate_restricted_special_energy(non_dragon)
    assert [row.print_id for row in removed_dde.discarded] == ["xy6-97"]
    assert removed_dde.state.zones.count("energy-class", "discard") == 1

    # Same-name unknown prints are conservative: they are left untouched.
    unknown = energy_state(
        card_name="Double Dragon Energy",
        print_id="unknown-print",
        units=2,
        holder_tags=("Colorless",),
    )
    assert revalidate_restricted_special_energy(unknown).state == unknown

    print(json.dumps({
        "restricted_print_rows": catalog["print_rows"],
        "restricted_distinct_names": catalog["distinct_names"],
        "triple_acceleration_post_basic": "discard",
        "double_dragon_post_non_dragon": "discard",
        "unknown_print_policy": "preserve",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
