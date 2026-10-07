"""Reproduce source-authorized Scoop-Up Block Retreat routing."""

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
    ToolAttachment,
    make_board,
    make_pokemon,
)
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_board_effects import (
    active_scoop_up_block_source_ids,
    retreat_with_opponent_board_effects,
)
from retreat_energy_transaction import RetreatEnergyTransactionState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def actor_state(*, damage_counters: int) -> RetreatEnergyTransactionState:
    dce = EnergyAttachment(
        "dce",
        "Double Colorless Energy",
        ("C", "C"),
    )
    pouch = ToolAttachment("pouch", "Dashing Pouch")
    active = make_pokemon(
        "actor-active",
        "Retreating Pokemon",
        energy=(dce,),
        tool=pouch,
        damage_counters=damage_counters,
    )
    pivot = make_pokemon("actor-pivot", "Pivot")
    energy = EnergyBoardState(
        zones=ZoneCountState.from_mapping({
            ("dce-class", "attached"): 1,
        }),
        board=make_board(active, (pivot,)),
        instance_classes=(("dce", "dce-class"),),
    )
    unified = make_state({}, turn_budget=TurnActionBudget())
    return RetreatEnergyTransactionState(unified=unified, energy=energy)


def opponent_board(
    *,
    abilities_enabled: bool = True,
    print_id: str = "sm9-66",
    mime_active: bool = False,
):
    mime = make_pokemon(
        "mime",
        "Mr. Mime",
        print_id=print_id,
        abilities_enabled=abilities_enabled,
    )
    other = make_pokemon("other", "Other Pokemon")
    if mime_active:
        return make_board(mime, (other,))
    return make_board(other, (mime,))


def destination(result) -> str:
    assert result is not None
    assert result.transaction.committed
    assert len(result.transaction.destinations) == 1
    return result.transaction.destinations[0].destination_zone


def main() -> None:
    benched_mime = opponent_board()
    assert active_scoop_up_block_source_ids(benched_mime) == ("mime",)

    blocked = retreat_with_opponent_board_effects(
        actor_state(damage_counters=1),
        "actor-pivot",
        retreat_cost=2,
        discard_energy_ids=("dce",),
        opponent_board=benched_mime,
    )
    assert blocked is not None
    assert blocked.scoop_up_block_source_ids == ("mime",)
    assert destination(blocked) == "discard"
    assert blocked.transaction.state.energy.zones.count(
        "dce-class", "hand"
    ) == 0

    active_mime = retreat_with_opponent_board_effects(
        actor_state(damage_counters=1),
        "actor-pivot",
        retreat_cost=2,
        discard_energy_ids=("dce",),
        opponent_board=opponent_board(mime_active=True),
    )
    assert destination(active_mime) == "discard"

    suppressed = retreat_with_opponent_board_effects(
        actor_state(damage_counters=1),
        "actor-pivot",
        retreat_cost=2,
        discard_energy_ids=("dce",),
        opponent_board=opponent_board(abilities_enabled=False),
    )
    assert suppressed is not None
    assert suppressed.scoop_up_block_source_ids == ()
    assert destination(suppressed) == "hand"

    wrong_print = retreat_with_opponent_board_effects(
        actor_state(damage_counters=1),
        "actor-pivot",
        retreat_cost=2,
        discard_energy_ids=("dce",),
        opponent_board=opponent_board(print_id="sm9-other"),
    )
    assert wrong_print is not None
    assert wrong_print.scoop_up_block_source_ids == ()
    assert destination(wrong_print) == "hand"

    undamaged = retreat_with_opponent_board_effects(
        actor_state(damage_counters=0),
        "actor-pivot",
        retreat_cost=2,
        discard_energy_ids=("dce",),
        opponent_board=benched_mime,
    )
    assert undamaged is not None
    assert undamaged.scoop_up_block_source_ids == ("mime",)
    assert destination(undamaged) == "hand"

    print(json.dumps({
        "exact_source_print": "sm9-66",
        "benched_source_active": True,
        "active_source_active": True,
        "suppressed_source_active": False,
        "wrong_print_active": False,
        "damaged_holder_destination_with_block": "discard",
        "undamaged_holder_destination_with_block": "hand",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
