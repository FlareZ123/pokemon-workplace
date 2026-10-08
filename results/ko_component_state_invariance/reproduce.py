"""Independently compare local KO invariance with full conserved-state outcomes."""

from math import factorial
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_component_state_invariance import certify_component_ko_invariance
from ko_order_signature_projection import project_with_zone_signatures
from ko_order_outcome_space import ko_order_outcomes
from results.knockout_redirection_routes.reproduce import build_pending
from results.ko_exchangeable_factorization_stress.reproduce import (
    build_pending as build_large_pending, competing_programs,
)


def compare(pending, programs, precedence=(), promote="b"):
    local = certify_component_ko_invariance(
        pending, programs, promote_id=promote, precedences=precedence
    )
    full = project_with_zone_signatures(
        pending, programs, promote_id=promote, precedences=precedence
    )
    assert local.invariant == (len(full.outcomes) == 1)
    assert local.candidate_total_orders == sum(
        outcome.order_count for outcome in full.outcomes
    )
    assert local.local_route_outcomes_checked >= local.component_count
    if local.invariant:
        assert local.terminal_state == full.outcomes[0].state
        assert local.witness_order is not None
        assert local.varying_components == ()
    else:
        assert local.terminal_state is None
        assert local.witness_order is None
        assert local.varying_components
    return local


def main():
    initial, pending = build_pending()
    # Both instance-distinct outcomes have the same class-zone histogram.
    swappable = {
        "first": {"water-1": "hand", "water-2": "discard"},
        "second": {"water-1": "discard", "water-2": "hand"},
    }
    exchangeable = compare(pending, swappable)
    assert exchangeable.invariant
    assert exchangeable.component_count == 1
    assert exchangeable.local_route_outcomes_checked == 2
    assert exchangeable.terminal_state is not None
    assert exchangeable.terminal_state.ledger.totals() == initial.totals()
    assert exchangeable.terminal_state.ledger.exchangeable.count(
        "basic-water", "hand"
    ) == 1

    # Shared writes of exactly the same zone do not cause dependencies.
    same_zone = {"a": {"water-1": "hand"}, "b": {"water-1": "hand"}}
    consistent = compare(pending, same_zone)
    assert consistent.invariant and consistent.component_count == 2

    # Conflict among independent sources is detectable without global product.
    disjoint = {
        "a": {"water-1": "hand"}, "b": {"water-1": "lost_zone"},
        "c": {"water-2": "hand"}, "d": {"water-2": "lost_zone"},
    }
    conflicting = compare(pending, disjoint)
    assert not conflicting.invariant
    assert conflicting.component_count == 2
    assert conflicting.local_route_outcomes_checked == 4
    assert conflicting.candidate_total_orders == factorial(4)

    # Without effects, all removed cards follow their default disposal.
    blank = compare(pending, {})
    assert blank.invariant and blank.candidate_total_orders == 1
    assert blank.witness_order == ()

    # External precedence can force an otherwise variable component.
    constrained = compare(
        pending, {"a": {"water-1": "hand"}, "b": {"water-1": "lost_zone"}},
        (("a", "b"),),
    )
    assert constrained.invariant and constrained.candidate_total_orders == 1

    board = pending.state.board
    assert board is not None
    victim = next(row for row in board.pokemon if row.pokemon_id == "a")
    ids = tuple(
        [c.card_id for c in victim.stack]
        + [c.card_id for c in victim.attachments]
    )
    rng = Random(20261008)
    checks = 0
    for n in range(1, 8):
        for _ in range(25):
            programs = {
                f"e{i}": {
                    instance: rng.choice(("hand", "discard", "lost_zone"))
                    for instance in ids
                    if rng.random() < 0.43
                }
                for i in range(n)
            }
            precedence = tuple(
                (f"e{i}", f"e{j}")
                for i in range(n)
                for j in range(i + 1, n)
                if rng.random() < 0.13
            )
            compare(pending, programs, precedence)
            checks += 1
    assert checks == 175

    # 10 independent pairs, 1024 instance routes, but only 20 local
    # route outcomes needed for an exact noninvariance certificate.
    _, large_pending = build_large_pending(10)
    large_programs = competing_programs(10)
    large = certify_component_ko_invariance(
        large_pending, large_programs, promote_id="b"
    )
    assert not large.invariant
    assert large.component_count == 10
    assert len(large.varying_components) == 10
    assert large.local_route_outcomes_checked == 20
    assert large.candidate_total_orders == factorial(20)
    print(
        "KO local invariance certificate passed: "
        f"{checks} randomized full-disposal cross-checks; 20 local "
        "outcomes certify variation across 1024 global instance routes"
    )


if __name__ == "__main__":
    main()
