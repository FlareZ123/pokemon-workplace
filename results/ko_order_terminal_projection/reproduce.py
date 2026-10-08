"""Verify exact KO order equivalence after full conserved physical disposal."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import assert_conserved
from ko_order_outcome_space import ko_order_outcomes
from ko_order_terminal_projection import project_terminal_outcomes
from knockout_redirection_ordering import resolve_ordered_programs, resolved_route_map
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import (
    ATTACHED_ENERGY_TO_HAND,
    POKEMON_TO_LOST,
    SELF_TO_HAND,
)
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending


def main():
    initial, pending = build_pending()

    def program(signature, selected=()):
        routes = destinations_for_redirection(
            pending,
            pokemon_id="a",
            routing_signature=signature,
            selected_energy_ids=selected,
        )
        assert routes is not None
        return routes

    programs = {
        "return": program(SELF_TO_HAND),
        "lost": program(POKEMON_TO_LOST),
    }
    results = project_terminal_outcomes(pending, programs, promote_id="b")
    assert len(results) == 2
    assert sum(row.order_count for row in results) == 2
    for outcome in results:
        assert outcome.distinct_instance_routes == 1
        assert_conserved(initial, outcome.state.ledger)
        assert outcome.state.board is not None
        assert outcome.state.board.active_id == "b"
        ordered = resolve_ordered_programs(programs, outcome.witness_orders[0])
        assert ordered is not None
        independently_disposed = discard_pending_with_zone_routes(
            pending,
            promote_id="b",
            destinations=resolved_route_map(ordered),
        )
        assert independently_disposed == outcome.state

    # Three hypothetical co-present destination programs have 4 exact
    # instance routes and four distinct conserved terminal states.
    programs["recover"] = program(
        ATTACHED_ENERGY_TO_HAND, ("water-1", "water-2")
    )
    routes = ko_order_outcomes(programs)
    physical = project_terminal_outcomes(pending, programs, promote_id="b")
    assert len(routes) == 4 and len(physical) == 4
    assert sorted(row.order_count for row in physical) == [1, 1, 2, 2]
    assert sum(row.order_count for row in physical) == 6
    for row in physical:
        assert_conserved(initial, row.state.ledger)

    # Two ID-distinct routes become the same terminal exchangeable zone state:
    # one of two identical Basic Water cards goes to hand, the other discard.
    # The source-order permissions in this construction are abstract inputs.
    copies = {
        "first": {"water-1": "hand", "water-2": "discard"},
        "second": {"water-1": "discard", "water-2": "hand"},
    }
    distinct_routes = ko_order_outcomes(copies)
    assert len(distinct_routes) == 2
    equivalent = project_terminal_outcomes(pending, copies, promote_id="b")
    assert len(equivalent) == 1
    only = equivalent[0]
    assert only.order_count == 2
    assert only.distinct_instance_routes == 2
    assert len(only.witness_orders) == 2
    assert only.state.ledger.exchangeable.count("basic-water", "hand") == 1
    assert only.state.ledger.exchangeable.count("basic-water", "discard") == 1
    assert_conserved(initial, only.state.ledger)

    # Without explicit redirections, all knocked-out cards route to discard.
    fallback = project_terminal_outcomes(pending, {}, promote_id="b")
    assert len(fallback) == 1 and fallback[0].order_count == 1
    assert fallback[0].state.ledger.exchangeable.count("aegislash", "discard") == 1

    # External precedence can eliminate one endpoint.
    restricted = project_terminal_outcomes(
        pending,
        {"return": program(SELF_TO_HAND), "lost": program(POKEMON_TO_LOST)},
        promote_id="b",
        precedences=(("return", "lost"),),
    )
    assert len(restricted) == 1 and restricted[0].order_count == 1

    try:
        project_terminal_outcomes(
            pending, {"invalid": {"not-in-batch": "hand"}}, promote_id="b"
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid physical route was accepted")

    print("Conserved KO terminal projection passed; two distinct instance routes share one exchangeable terminal state")


if __name__ == "__main__":
    main()
