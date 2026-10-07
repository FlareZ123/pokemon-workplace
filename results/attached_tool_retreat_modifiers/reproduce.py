"""Reproduce board-derived Pokémon Tool Retreat modifiers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from attached_tool_retreat_modifiers import (
    RETREAT_MODIFYING_TOOL_PRINT_IDS,
    derive_tool_retreat_modifiers,
)
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from retreat_cost_semantics import effective_retreat_cost


def board(
    *,
    card_name="Holder",
    tags=(),
    tool_name=None,
    tool_print=None,
    tool_enabled=True,
):
    tool = (
        ToolAttachment("tool", tool_name, print_id=tool_print)
        if tool_name is not None
        else None
    )
    active = make_pokemon(
        "active",
        card_name,
        tags=tags,
        tool=tool,
        tool_effect_enabled=tool_enabled,
    )
    return make_board(active)


def blank():
    return board(card_name="Blank")


def cost(own, opponent, base, **kwargs):
    derived = derive_tool_retreat_modifiers(own, opponent, **kwargs)
    return effective_retreat_cost(base, derived.modifiers), derived


def main() -> None:
    assert len(RETREAT_MODIFYING_TOOL_PRINT_IDS) == 20

    value, derived = cost(
        board(tool_name="Air Balloon", tool_print="swsh1-156"),
        blank(),
        3,
    )
    assert value == 1 and derived.exact

    value, _ = cost(
        board(tool_name="Float Stone", tool_print="xy8-137"),
        blank(),
        4,
    )
    assert value == 0

    value, _ = cost(
        board(tool_name="Escape Board", tool_print="sm5-122"),
        blank(),
        2,
    )
    assert value == 1

    value, _ = cost(
        board(
            tags=("Stage2",),
            tool_name="Big Air Balloon",
            tool_print="sv3pt5-155",
        ),
        blank(),
        4,
    )
    assert value == 0

    value, _ = cost(
        board(
            tags=("Future",),
            tool_name="Future Booster Energy Capsule",
            tool_print="sv4-164",
        ),
        blank(),
        4,
    )
    assert value == 0

    rescue = board(tool_name="Rescue Board", tool_print="sv5-159")
    value, derived = cost(rescue, blank(), 2)
    assert value == 1
    assert not derived.exact
    assert len(derived.unresolved_conditions) == 1

    value, derived = cost(
        rescue,
        blank(),
        2,
        active_remaining_hp=30,
    )
    assert value == 0 and derived.exact

    value, derived = cost(
        rescue,
        blank(),
        2,
        active_remaining_hp=40,
    )
    assert value == 1 and derived.exact

    own = board(
        tool_name="Gravity Gemstone",
        tool_print="sv7-137",
    )
    opposing = board(
        tool_name="Gravity Gemstone",
        tool_print="sv7-137",
    )
    value, _ = cost(own, opposing, 1)
    assert value == 3

    value, _ = cost(
        board(
            card_name="Leafeon V",
            tags=("Pokemon V",),
            tool_name="Snow Leaf Badge",
            tool_print="swsh7-159",
        ),
        blank(),
        2,
    )
    assert value == 0

    value, _ = cost(
        board(
            tool_name="Air Balloon",
            tool_print="swsh1-156",
            tool_enabled=False,
        ),
        blank(),
        3,
    )
    assert value == 3

    print(json.dumps({
        "retreat_modifying_tool_prints": len(RETREAT_MODIFYING_TOOL_PRINT_IDS),
        "air_balloon_base_3": 1,
        "float_stone_base_4": 0,
        "two_gravity_gemstones_base_1": 3,
        "rescue_board_unknown_hp_exact": False,
        "rescue_board_hp_30_base_2": 0,
        "suppressed_air_balloon_base_3": 3,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
