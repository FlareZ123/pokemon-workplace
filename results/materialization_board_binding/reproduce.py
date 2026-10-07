"""Check IdentityLedger bindings against the live board-object kernel."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    attach_instance,
    materialize,
    validate_board_attachment_bindings,
)
from multicopy_zone_state import ZoneCountState


def main():
    initial = IdentityLedger(
        ZoneCountState.from_mapping({("dce-class", "hand"): 2})
    )

    one = materialize(
        initial,
        card_class="dce-class",
        card_name="Double Colorless Energy",
        source_zone="hand",
        instance_id="dce-a",
    )
    one = attach_instance(one, "dce-a", "active")

    two = materialize(
        one,
        card_class="dce-class",
        card_name="Double Colorless Energy",
        source_zone="hand",
        instance_id="dce-b",
    )
    two = attach_instance(two, "dce-b", "active")
    assert_conserved(initial, two)
    assert two.total("dce-class") == 2

    active = make_pokemon(
        "active",
        "Active",
        energy=(
            EnergyAttachment(
                "dce-a",
                "Double Colorless Energy",
                ("C", "C"),
                print_id="same-print",
            ),
            EnergyAttachment(
                "dce-b",
                "Double Colorless Energy",
                ("C", "C"),
                print_id="same-print",
            ),
        ),
    )
    board = make_board(active)
    validate_board_attachment_bindings(two, board)

    wrong = make_pokemon(
        "active",
        "Active",
        energy=(
            EnergyAttachment(
                "different-id",
                "Double Colorless Energy",
                ("C", "C"),
                print_id="same-print",
            ),
        ),
    )
    try:
        validate_board_attachment_bindings(two, make_board(wrong))
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched board binding was accepted")

    print("materialization board binding regressions passed")


if __name__ == "__main__":
    main()
