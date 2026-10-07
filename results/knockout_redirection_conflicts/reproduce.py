"""Reproduce same-instance conflicts between KO redirection programs."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from knockout_redirection_conflicts import (
    destination_conflicts,
    merge_compatible_programs,
)
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import (
    ALL_TO_LOST,
    ATTACHED_ENERGY_TO_HAND,
    POKEMON_TO_LOST,
    SELF_TO_HAND,
)
from results.knockout_redirection_routes.reproduce import build_pending


def program(pending, signature, selected=()):
    routes = destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=signature,
        selected_energy_ids=selected,
    )
    assert routes is not None
    return routes


def conflict_ids(programs):
    return tuple(row.instance_id for row in destination_conflicts(programs))


def main() -> None:
    _initial, pending = build_pending()

    aegislash = program(pending, SELF_TO_HAND)
    tyranitar = program(pending, ALL_TO_LOST)
    lost_city = program(pending, POKEMON_TO_LOST)
    huntail = program(
        pending,
        ATTACHED_ENERGY_TO_HAND,
        ("water-1", "water-2"),
    )

    stack_ids = ("aegislash-a", "doublade-a", "honedge-a")
    attachment_ids = ("band-a", "dce-a", "water-1", "water-2")
    water_ids = ("water-1", "water-2")

    # Durable Blade wants the whole Pokemon stack in hand while Lost City wants
    # that same stack in the Lost Zone. Both explicitly discard attachments.
    assert conflict_ids(
        {"durable-blade": aegislash, "lost-city": lost_city}
    ) == stack_ids

    # Lost Out and Lost City agree on the Pokemon stack but disagree on every
    # attachment: Lost Out sends them to the Lost Zone, Lost City discards them.
    assert conflict_ids(
        {"lost-out": tyranitar, "lost-city": lost_city}
    ) == attachment_ids

    # Diver's Catch conflicts only on the selected Basic Water Energy instances;
    # it makes no assignment to the Pokemon stack or non-selected attachments.
    assert conflict_ids(
        {"divers-catch": huntail, "lost-city": lost_city}
    ) == water_ids

    assert conflict_ids(
        {"lost-out": tyranitar, "divers-catch": huntail}
    ) == water_ids

    # Same-destination overlaps are compatible and can be merged.
    assert merge_compatible_programs(
        {"lost-city-a": lost_city, "lost-city-b": lost_city}
    ) == lost_city

    # Any same-instance destination disagreement prevents a semantics-free merge.
    assert merge_compatible_programs(
        {"durable-blade": aegislash, "lost-city": lost_city}
    ) is None
    assert merge_compatible_programs(
        {"lost-out": tyranitar, "divers-catch": huntail}
    ) is None

    # Preserve effect provenance in the conflict report.
    lost_out_water = next(
        row
        for row in destination_conflicts(
            {"lost-out": tyranitar, "divers-catch": huntail}
        )
        if row.instance_id == "water-1"
    )
    assert tuple(
        (row.effect_id, row.destination_zone)
        for row in lost_out_water.assignments
    ) == (
        ("divers-catch", "hand"),
        ("lost-out", "lost_zone"),
    )

    print("Knock Out redirection conflict regressions passed")


if __name__ == "__main__":
    main()
