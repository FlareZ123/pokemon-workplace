"""Exact 20-effect KO routing compressed through independence and exchangeability.

Ten identical Basic Water Energy instances start attached to one doomed
Pokemon. Each instance has an abstract competing keep-to-hand versus
lost-zone destination effect. The instance-level planner produces 1024
endpoints; the conserved terminal model only distinguishes how many cards
go to each zone, yielding 11 equivalence classes.
"""

from math import comb, factorial
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import (
    AttachmentKind, BoardPokemon, PokemonCard, make_state,
)
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from ko_order_component_factorization import (
    effect_dependency_components, factorized_ko_order_outcomes
)
from ko_order_signature_projection import project_with_zone_signatures
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def build_pending(card_count):
    initial = IdentityLedger(
        ZoneCountState.from_mapping({
            ("lapras", "hand"): 1,
            ("bidoof", "hand"): 1,
            ("basic-water", "hand"): card_count,
        })
    )
    ledger = initial
    for card_class, name, instance, holder in (
        ("lapras", "Lapras", "lapras-a", "a"),
        ("bidoof", "Bidoof", "bidoof-b", "b"),
    ):
        ledger = materialize(
            ledger, card_class=card_class, card_name=name,
            source_zone="hand", instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, holder)
    state = StackBoardMaterialState(
        ledger,
        make_state(
            (
                BoardPokemon(
                    "a", (PokemonCard("lapras-a", "Lapras"),),
                    retreat_cost=2,
                ),
                BoardPokemon(
                    "b", (PokemonCard("bidoof-b", "Bidoof"),),
                    retreat_cost=1,
                ),
            ),
            active_id="a",
        ),
    )
    for i in range(card_count):
        state = attach_from_hand(
            state,
            pokemon_id="a",
            card_class="basic-water",
            instance_id=f"water-{i}",
            card_name="Basic Water Energy",
            kind=AttachmentKind.ENERGY,
            retreat_units=1,
        )
        assert state is not None
    assert_conserved(initial, state.ledger)
    pending = prepare_knock_out_batch(state, ("a",))
    assert pending is not None
    return initial, pending


def competing_programs(n):
    return {
        effect_id: {f"water-{i}": zone}
        for i in range(n)
        for effect_id, zone in (
            (f"keep-{i}", "hand"),
            (f"lose-{i}", "lost_zone"),
        )
    }


def main():
    n = 10
    initial, pending = build_pending(n)
    programs = competing_programs(n)
    components = effect_dependency_components(programs)
    assert len(programs) == 2 * n
    assert len(components) == n
    assert all(len(component) == 2 for component in components)

    routes = factorized_ko_order_outcomes(programs)
    assert len(routes) == 1 << n
    orders_per_instance_destination = factorial(2 * n) // (1 << n)
    assert all(
        row.order_count == orders_per_instance_destination for row in routes
    )
    assert sum(row.order_count for row in routes) == factorial(2 * n)

    projected = project_with_zone_signatures(
        pending, programs, promote_id="b"
    )
    assert projected.instance_route_outcomes == 1 << n
    assert projected.physical_disposals == n + 1
    assert len(projected.outcomes) == n + 1

    seen = set()
    for endpoint in projected.outcomes:
        assert endpoint.state.board is not None
        assert endpoint.state.board.active_id == "b"
        assert [row.pokemon_id for row in endpoint.state.board.pokemon] == ["b"]
        assert_conserved(initial, endpoint.state.ledger)
        counts = endpoint.state.ledger.exchangeable
        k = counts.count("basic-water", "hand")
        assert k not in seen
        seen.add(k)
        assert counts.count("basic-water", "lost_zone") == n - k
        assert counts.count("lapras", "discard") == 1
        assert endpoint.distinct_instance_routes == comb(n, k)
        assert endpoint.order_count == comb(n, k) * orders_per_instance_destination
        assert len(endpoint.witness_orders) == comb(n, k)

    assert seen == set(range(n + 1))
    assert sum(row.order_count for row in projected.outcomes) == factorial(2 * n)
    assert sum(row.distinct_instance_routes for row in projected.outcomes) == 1 << n
    calls_saved = projected.instance_route_outcomes - projected.physical_disposals
    assert calls_saved == 1013
    print(
        f"20-effect exchangeable KO compression passed: "
        f"{projected.instance_route_outcomes} instance outcomes, "
        f"{projected.physical_disposals} distinct conserved end states, "
        f"{calls_saved} full physical disposals avoided; all 20! order "
        "multiplicities conserved exactly"
    )


if __name__ == "__main__":
    main()
