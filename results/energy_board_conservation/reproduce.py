"""Reproduce Energy conservation across zone counts and board topology."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon  # noqa: E402
from energy_board_conservation import (  # noqa: E402
    EnergyBoardState,
    materialize_energy_from_hand,
    retreat_with_energy_conservation,
)
from multicopy_zone_state import ZoneCountState  # noqa: E402


def main() -> None:
    zones = ZoneCountState.from_mapping(
        {
            ("dce-class", "hand"): 2,
        }
    )
    active = make_pokemon("active", "Active")
    bench = make_pokemon("bench", "Bench")
    state = EnergyBoardState(zones, make_board(active, (bench,)))

    first = materialize_energy_from_hand(
        state,
        object_id="active",
        card_class="dce-class",
        instance_id="dce-a",
        card_name="Double Colorless Energy",
        units=("C", "C"),
        print_id="xy-print",
    )
    assert first is not None
    second = materialize_energy_from_hand(
        first,
        object_id="active",
        card_class="dce-class",
        instance_id="dce-b",
        card_name="Double Colorless Energy",
        units=("C", "C"),
        print_id="xy-print",
    )
    assert second is not None

    assert second.zones.count("dce-class", "hand") == 0
    assert second.zones.count("dce-class", "attached") == 2
    assert len(second.board.get("active").energy) == 2
    assert {
        energy.instance_id for energy in second.board.get("active").energy
    } == {"dce-a", "dce-b"}

    retreated_both = retreat_with_energy_conservation(
        second,
        "bench",
        retreat_cost=2,
        discard_energy_ids=("dce-a", "dce-b"),
    )
    assert retreated_both is not None
    assert retreated_both.zones.count("dce-class", "attached") == 0
    assert retreated_both.zones.count("dce-class", "discard") == 2
    assert retreated_both.instance_classes == ()

    retreated = retreat_with_energy_conservation(
        second,
        "bench",
        retreat_cost=2,
        discard_energy_ids=("dce-a",),
    )
    assert retreated is not None
    assert retreated.zones.count("dce-class", "attached") == 1
    assert retreated.zones.count("dce-class", "discard") == 1
    assert retreated.board.active_id == "bench"
    assert retreated.board.bench_ids == ("active",)
    assert [
        energy.instance_id
        for energy in retreated.board.get("active").energy
    ] == ["dce-b"]
    assert retreated.instance_classes == (("dce-b", "dce-class"),)

    bad_zones = ZoneCountState.from_mapping(
        {
            ("dce-class", "attached"): 2,
        }
    )
    try:
        EnergyBoardState(
            bad_zones,
            retreated.board,
            retreated.instance_classes,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("inconsistent zone/board Energy state was accepted")

    print("Energy board conservation regressions passed")


if __name__ == "__main__":
    main()
