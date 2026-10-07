"""Reproduce Forest Seal Stone recovery of Harto's backup Gladion."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (
    ToolAttachment,
    make_board,
    make_pokemon,
)
from forest_seal_star_alchemy import (
    ForestSealSearchState,
    attach_forest_seal_stone,
    use_star_alchemy,
)
from gladion_supporter_physical_transaction import (
    execute_gladion_supporter_physical,
)
from identity_materialization import IdentityLedger, materialize, move_instance
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from top_prize_physical_bridge import TopPrizePhysicalState


def base_state(
    *,
    channels: PlayerChannels | None = None,
    crobat_tool: ToolAttachment | None = None,
) -> ForestSealSearchState:
    pivot = make_pokemon(
        "pivot",
        "Pivot",
        tags=("Basic",),
    )
    crobat = make_pokemon(
        "crobat",
        "Crobat V",
        print_id="swsh3-104",
        tags=("Basic", "V"),
        tool=crobat_tool,
    )
    return ForestSealSearchState(
        zones=ZoneCountState.from_mapping(
            {
                ("pivot", "active"): 1,
                ("crobat_v", "bench"): 1,
                ("forest_seal_stone", "hand"): 1,
                ("backup_gladion", "deck"): 1,
                ("top_filler", "deck"): 1,
                ("alolan_raichu", "prize"): 1,
            }
        ),
        board=make_board(pivot, (crobat,)),
        channels=channels or PlayerChannels(),
    )


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def physical_gladion_rescue(state: ForestSealSearchState):
    ledger = IdentityLedger(state.zones)
    ledger = materialize(
        ledger,
        card_class="backup_gladion",
        card_name="Gladion",
        source_zone="hand",
        instance_id="backup-gladion-1",
    )
    ledger = materialize(
        ledger,
        card_class="alolan_raichu",
        card_name="Alolan Raichu",
        source_zone="prize",
        instance_id="prize-raichu",
    )
    ledger = materialize(
        ledger,
        card_class="top_filler",
        card_name="Top filler",
        source_zone="deck",
        instance_id="top-1",
    )
    ledger = move_instance(ledger, "top-1", "deck_top")
    physical = TopPrizePhysicalState(
        ledger,
        "top-1",
        ("prize-raichu",),
        (False,),
    )
    outcomes = execute_gladion_supporter_physical(
        physical,
        state.budget,
        state.channels,
        gladion_instance_id="backup-gladion-1",
        selected_position=0,
    )
    assert len(outcomes) == 1
    return outcomes[0]


def main() -> None:
    initial = base_state()
    attached = attach_forest_seal_stone(
        initial,
        holder_object_id="crobat",
    )
    searched = use_star_alchemy(
        attached,
        holder_object_id="crobat",
        target_card_class="backup_gladion",
    )

    assert searched.vstar_power_used
    assert searched.zones.count("forest_seal_stone", "attached") == 1
    assert searched.zones.count("backup_gladion", "hand") == 1
    assert searched.zones.count("backup_gladion", "deck") == 0
    assert searched.board.get("crobat").tool is not None

    rescue = physical_gladion_rescue(searched)
    final = rescue.physical.physical_after
    assert final.ledger.instance("prize-raichu").zone == "hand"
    assert final.ledger.instance("backup-gladion-1").zone == "prize"
    assert rescue.budget_after.supporter_used

    tool_locked = expect_value_error(
        lambda: attach_forest_seal_stone(
            base_state(channels=PlayerChannels(tool_play=False)),
            holder_object_id="crobat",
        )
    )
    assert tool_locked

    occupied = expect_value_error(
        lambda: attach_forest_seal_stone(
            base_state(
                crobat_tool=ToolAttachment(
                    "other-tool-1",
                    "Other Tool",
                )
            ),
            holder_object_id="crobat",
        )
    )
    assert occupied

    spent_vstar = expect_value_error(
        lambda: use_star_alchemy(
            replace(attached, vstar_power_used=True),
            holder_object_id="crobat",
            target_card_class="backup_gladion",
        )
    )
    assert spent_vstar

    crobat = attached.board.get("crobat")
    ability_suppressed_board = replace(
        attached.board,
        objects=tuple(
            replace(row, abilities_enabled=False)
            if row.object_id == "crobat"
            else row
            for row in attached.board.objects
        ),
    )
    ability_suppressed_board.validate()
    ability_suppressed = expect_value_error(
        lambda: use_star_alchemy(
            replace(attached, board=ability_suppressed_board),
            holder_object_id="crobat",
            target_card_class="backup_gladion",
        )
    )
    assert ability_suppressed

    tool_suppressed_board = replace(
        attached.board,
        objects=tuple(
            replace(
                row,
                pokemon_state=replace(
                    row.pokemon_state,
                    tool_effect_enabled=False,
                ),
            )
            if row.object_id == "crobat"
            else row
            for row in attached.board.objects
        ),
    )
    tool_suppressed_board.validate()
    tool_suppressed = expect_value_error(
        lambda: use_star_alchemy(
            replace(attached, board=tool_suppressed_board),
            holder_object_id="crobat",
            target_card_class="backup_gladion",
        )
    )
    assert tool_suppressed

    non_v_attached = attach_forest_seal_stone(
        initial,
        holder_object_id="pivot",
        tool_instance_id="forest-seal-stone-pivot",
    )
    non_v_rejected = expect_value_error(
        lambda: use_star_alchemy(
            non_v_attached,
            holder_object_id="pivot",
            target_card_class="backup_gladion",
        )
    )
    assert non_v_rejected

    missing_target = expect_value_error(
        lambda: use_star_alchemy(
            replace(
                attached,
                zones=attached.zones.move(
                    "backup_gladion",
                    "deck",
                    "prize",
                ),
            ),
            holder_object_id="crobat",
            target_card_class="backup_gladion",
        )
    )
    assert missing_target

    print(
        json.dumps(
            {
                "forest_seal_attached_to_crobat_v": True,
                "star_alchemy_backup_gladion_to_hand": True,
                "vstar_power_consumed": True,
                "backup_gladion_rescues_prized_raichu": True,
                "supporter_window_consumed_by_gladion": True,
                "tool_lock_rejected": tool_locked,
                "occupied_tool_slot_rejected": occupied,
                "spent_vstar_rejected": spent_vstar,
                "ability_suppression_rejected": ability_suppressed,
                "tool_effect_suppression_rejected": tool_suppressed,
                "non_v_holder_cannot_use_star_alchemy": non_v_rejected,
                "prized_backup_not_searchable": missing_target,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
