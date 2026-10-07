"""Reproduce order-sensitive KO redirection with an official Lost City case."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from knockout_redirection_ordering import (
    resolve_ordered_programs,
    resolved_route_map,
)
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import POKEMON_TO_LOST, SELF_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending


def program(pending, signature):
    routes = destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=signature,
    )
    assert routes is not None
    return routes


def dispose(pending, resolutions):
    result = discard_pending_with_zone_routes(
        pending,
        promote_id="b",
        destinations=resolved_route_map(resolutions),
    )
    assert result is not None
    assert result.board is not None
    assert result.board.active_id == "b"
    return result


def main() -> None:
    initial, pending = build_pending()
    return_to_hand = program(pending, SELF_TO_HAND)
    lost_city = program(pending, POKEMON_TO_LOST)
    programs = {
        "return-ability": return_to_hand,
        "lost-city": lost_city,
    }

    hand_first = resolve_ordered_programs(
        programs,
        ("return-ability", "lost-city"),
    )
    assert hand_first is not None
    hand_first_by_id = {row.instance_id: row for row in hand_first}
    for instance_id in ("honedge-a", "doublade-a", "aegislash-a"):
        row = hand_first_by_id[instance_id]
        assert row.destination_zone == "hand"
        assert row.effect_id == "return-ability"

    hand_result = dispose(pending, hand_first)
    for card_class in ("honedge", "doublade", "aegislash"):
        assert hand_result.ledger.exchangeable.count(card_class, "hand") == 1
    for card_class, count in (
        ("basic-water", 2),
        ("dce", 1),
        ("muscle-band", 1),
    ):
        assert hand_result.ledger.exchangeable.count(card_class, "discard") == count
    assert hand_result.ledger.totals() == initial.totals()

    lost_first = resolve_ordered_programs(
        programs,
        ("lost-city", "return-ability"),
    )
    assert lost_first is not None
    lost_first_by_id = {row.instance_id: row for row in lost_first}
    for instance_id in ("honedge-a", "doublade-a", "aegislash-a"):
        row = lost_first_by_id[instance_id]
        assert row.destination_zone == "lost_zone"
        assert row.effect_id == "lost-city"

    lost_result = dispose(pending, lost_first)
    for card_class in ("honedge", "doublade", "aegislash"):
        assert lost_result.ledger.exchangeable.count(card_class, "lost_zone") == 1
    for card_class, count in (
        ("basic-water", 2),
        ("dce", 1),
        ("muscle-band", 1),
    ):
        assert lost_result.ledger.exchangeable.count(card_class, "discard") == count
    assert lost_result.ledger.totals() == initial.totals()

    # Ordering must be an exact permutation of the supplied effect programs.
    assert resolve_ordered_programs(programs, ("lost-city",)) is None
    assert resolve_ordered_programs(
        programs,
        ("lost-city", "lost-city"),
    ) is None
    assert resolve_ordered_programs(
        programs,
        ("lost-city", "unknown"),
    ) is None

    print("Ordered Knock Out redirection regressions passed")


if __name__ == "__main__":
    main()
