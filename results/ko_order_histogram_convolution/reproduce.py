"""Cross-check exact KO histogram convolution and a 2^40 endpoint case."""

from math import comb, factorial
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_order_histogram_convolution import convolve_ko_terminal_states
from ko_order_signature_projection import project_with_zone_signatures
from knockout_redirection_ordering import (
    resolve_ordered_programs, resolved_route_map,
)
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending
from results.ko_exchangeable_factorization_stress.reproduce import (
    build_pending as build_energy_pending, competing_programs,
)
from results.tyranitar_double_ko_ordering.reproduce import (
    initial_materialized_state, programs_for,
)


def compare(pending, programs, precedence=(), promote="b"):
    fast = convolve_ko_terminal_states(
        pending, programs, promote_id=promote, precedences=precedence
    )
    oracle = project_with_zone_signatures(
        pending, programs, promote_id=promote, precedences=precedence
    )
    assert {row.state: row.order_count for row in fast.outcomes} == {
        row.state: row.order_count for row in oracle.outcomes
    }
    assert fast.full_disposals == oracle.physical_disposals
    assert fast.candidate_total_orders == sum(
        row.order_count for row in oracle.outcomes
    )
    for outcome in fast.outcomes:
        explicit = resolve_ordered_programs(
            programs, outcome.witness_order
        )
        assert explicit is not None
        state = discard_pending_with_zone_routes(
            pending, promote_id=promote,
            destinations=resolved_route_map(explicit),
        )
        assert state == outcome.state
    return fast


def main():
    initial, pending = build_pending()
    empty = compare(pending, {})
    assert empty.candidate_total_orders == 1
    assert empty.full_disposals == 1

    # Identity-distinct routes converge to one histogram.
    twin = {
        "a": {"water-1": "hand", "water-2": "discard"},
        "b": {"water-1": "discard", "water-2": "hand"},
    }
    same = compare(pending, twin)
    assert same.full_disposals == 1 and same.candidate_total_orders == 2
    assert same.outcomes[0].state.ledger.totals() == initial.totals()

    # Shared same-zone writers do not create a conflict component.
    overlap = compare(
        pending, {"a": {"water-1": "hand"}, "b": {"water-1": "hand"}}
    )
    assert overlap.component_count == 2 and overlap.full_disposals == 1

    # One externally constrained conflict yields one physical endpoint.
    constrained = compare(
        pending, {"a": {"water-1": "hand"}, "b": {"water-1": "lost_zone"}},
        (("a", "b"),),
    )
    assert constrained.full_disposals == 1

    # Real Tyranitar GX / Aegislash / Lapras / Huntail double KO setup.
    original, double_pending = initial_materialized_state()
    grouped, per_target = programs_for(double_pending)
    for programs in (grouped, per_target):
        confirmed = compare(double_pending, programs, promote="c")
        assert confirmed.full_disposals == 4
        assert confirmed.candidate_total_orders == factorial(len(programs))
        assert all(
            row.state.ledger.totals() == original.totals()
            for row in confirmed.outcomes
        )

    rng = Random(20261008)
    victim = next(p for p in pending.state.board.pokemon if p.pokemon_id == "a")
    ids = tuple(
        c.card_id for c in victim.stack + victim.attachments
    )
    checked = 0
    for n in range(1, 8):
        for _ in range(25):
            programs = {
                f"e{i}": {
                    card_id: rng.choice(("hand", "discard", "lost_zone"))
                    for card_id in ids
                    if rng.random() < 0.53
                }
                for i in range(n)
            }
            precedences = tuple(
                (f"e{i}", f"e{j}")
                for i in range(n)
                for j in range(i + 1, n)
                if rng.random() < 0.15
            )
            compare(pending, programs, precedences)
            checked += 1
    assert checked == 175

    # New scale: 40 independent binary conflicts have over one trillion
    # instance destinations, but only 41 exchangeable terminal histograms.
    n = 40
    initial_large, pending_large = build_energy_pending(n)
    effects = competing_programs(n)
    large = convolve_ko_terminal_states(
        pending_large, effects, promote_id="b"
    )
    assert len(effects) == 2 * n
    assert large.component_count == n
    assert large.local_route_outcomes_checked == 2 * n
    assert large.full_disposals == n + 1
    assert large.candidate_total_orders == factorial(2 * n)
    assert len(large.outcomes) == n + 1
    observed = set()
    for row in large.outcomes:
        counts = row.state.ledger.exchangeable
        k = counts.count("basic-water", "hand")
        assert k not in observed
        observed.add(k)
        assert counts.count("basic-water", "lost_zone") == n - k
        assert row.state.ledger.totals() == initial_large.totals()
        assert row.order_count == comb(n, k) * factorial(2 * n) // (1 << n)
    assert observed == set(range(n + 1))
    print(
        f"KO histogram convolution passed: {checked} random full-kernel "
        f"cross-checks; 2^{n} = {1 << n:,} instance endpoints become "
        f"{large.full_disposals} conserved states using "
        f"{large.local_route_outcomes_checked} local DP endpoints"
    )


if __name__ == "__main__":
    main()
