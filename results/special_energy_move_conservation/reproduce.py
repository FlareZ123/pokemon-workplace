"""Reproduce Special Energy movement to legal and illegal destinations."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_attachment_conservation import BoardMaterialState
from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    attach_instance,
    materialize,
)
from multicopy_zone_state import ZoneCountState
from special_energy_move_conservation import (
    move_special_energy_with_conservation,
)


def make_state(target_name: str) -> tuple[IdentityLedger, BoardMaterialState]:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("dde-class", "hand"): 1,
            }
        )
    )
    ledger = materialize(
        initial,
        card_class="dde-class",
        card_name="Double Dragon Energy",
        source_zone="hand",
        instance_id="dde-a",
    )
    ledger = attach_instance(ledger, "dde-a", "dragon")
    energy = EnergyAttachment(
        "dde-a",
        "Double Dragon Energy",
        ("any", "any"),
        print_id="xy6-97",
    )
    board = make_board(
        make_pokemon("dragon", "Dragon Pokemon", energy=(energy,)),
        (
            make_pokemon("other", target_name),
        ),
    )
    return initial, BoardMaterialState(ledger, board)


def main() -> None:
    initial, state = make_state("Dragon Pokemon 2")

    legal = move_special_energy_with_conservation(
        state,
        "dde-a",
        source_object_id="dragon",
        target_object_id="other",
        destination_accepts_card=True,
    )
    assert legal is not None
    assert legal.board is not None
    assert legal.board.get("dragon").energy == ()
    assert [e.instance_id for e in legal.board.get("other").energy] == ["dde-a"]
    assert legal.board.get("other").energy[0].units == ("any", "any")
    assert legal.ledger.instance("dde-a").attached_to == "other"
    assert_conserved(initial, legal.ledger)

    initial, state = make_state("Non-Dragon Pokemon")
    rejected_destination = move_special_energy_with_conservation(
        state,
        "dde-a",
        source_object_id="dragon",
        target_object_id="other",
        destination_accepts_card=False,
    )
    assert rejected_destination is not None
    assert rejected_destination.board is not None
    assert rejected_destination.board.get("dragon").energy == ()
    assert rejected_destination.board.get("other").energy == ()
    assert rejected_destination.ledger.instances == ()
    assert rejected_destination.ledger.exchangeable.count(
        "dde-class", "discard"
    ) == 1
    assert_conserved(initial, rejected_destination.ledger)

    print("Special Energy move conservation regressions passed")


if __name__ == "__main__":
    main()
