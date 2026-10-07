"""Reproduce Tool attachment conservation through evolution and Knock Out."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_attachment_conservation import (
    BoardMaterialState,
    attach_tool_from_hand,
    evolve_with_conservation,
    knock_out_with_conservation,
)
from board_object_kernel import make_board, make_pokemon
from identity_materialization import IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState


def main() -> None:
    initial_ledger = IdentityLedger(
        ZoneCountState.from_mapping({("muscle-band-class", "hand"): 2})
    )
    initial = BoardMaterialState(
        initial_ledger,
        make_board(
            make_pokemon("active", "Charmander"),
            (make_pokemon("bench", "Bidoof"),),
        ),
    )

    attached = attach_tool_from_hand(
        initial,
        object_id="active",
        card_class="muscle-band-class",
        instance_id="band-a",
        card_name="Muscle Band",
        print_id="xy-121",
    )
    assert attached is not None
    assert attached.ledger.exchangeable.count("muscle-band-class", "hand") == 1
    assert attached.ledger.instance("band-a").attached_to == "active"
    assert attached.board is not None
    assert attached.board.get("active").tool.instance_id == "band-a"

    assert attach_tool_from_hand(
        attached,
        object_id="active",
        card_class="muscle-band-class",
        instance_id="band-b",
        card_name="Muscle Band",
    ) is None

    evolved = evolve_with_conservation(
        attached,
        "active",
        new_card_name="Charmeleon",
    )
    assert evolved is not None
    assert evolved.board is not None
    assert evolved.board.get("active").card_name == "Charmeleon"
    assert evolved.board.get("active").tool.instance_id == "band-a"
    assert_conserved(initial.ledger, evolved.ledger)

    knocked_out = knock_out_with_conservation(
        evolved,
        "active",
        promote_object_id="bench",
    )
    assert knocked_out is not None
    assert knocked_out.board is not None
    assert knocked_out.board.active_id == "bench"
    assert knocked_out.ledger.exchangeable.count(
        "muscle-band-class", "discard"
    ) == 1
    assert knocked_out.ledger.exchangeable.count(
        "muscle-band-class", "hand"
    ) == 1
    assert knocked_out.ledger.instances == ()
    assert_conserved(initial.ledger, knocked_out.ledger)

    terminal_initial = BoardMaterialState(
        IdentityLedger(
            ZoneCountState.from_mapping({("muscle-band-class", "hand"): 1})
        ),
        make_board(make_pokemon("solo", "Charmander")),
    )
    terminal_attached = attach_tool_from_hand(
        terminal_initial,
        object_id="solo",
        card_class="muscle-band-class",
        instance_id="band-terminal",
        card_name="Muscle Band",
    )
    assert terminal_attached is not None
    terminal = knock_out_with_conservation(terminal_attached, "solo")
    assert terminal is not None
    assert terminal.board is None
    assert terminal.ledger.instances == ()
    assert terminal.ledger.exchangeable.count(
        "muscle-band-class", "discard"
    ) == 1

    print("board attachment conservation regressions passed")


if __name__ == "__main__":
    main()
