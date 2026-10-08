"""Exact KO terminal-invariance certificate without enumerating global outcomes.

For fixed-batch destination-only KO transitions, independent effect groups
contribute independent multisets of (card-class, zone) assignments.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import factorial
from typing import Iterable, Mapping

from ko_order_component_factorization import (
    effect_dependency_components, lexicographic_interleaving,
)
from ko_order_outcome_space import ko_order_outcomes
from ko_order_zone_signature import terminal_zone_signature
from knockout_redirection_ordering import resolve_ordered_programs, resolved_route_map
from knockout_zone_routing import discard_pending_with_zone_routes
from simultaneous_knockout_conservation import PendingKnockOutBatch
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class ComponentInvariance:
    invariant: bool
    terminal_state: StackBoardMaterialState | None
    witness_order: tuple[str, ...] | None
    component_count: int
    local_route_outcomes_checked: int
    varying_components: tuple[tuple[str, ...], ...]
    candidate_total_orders: int


def certify_component_ko_invariance(
    pending: PendingKnockOutBatch,
    programs: Mapping[str, Mapping[str, str]],
    *,
    promote_id: str | None = None,
    precedences: Iterable[tuple[str, str]] = (),
) -> ComponentInvariance:
    """Certify exact conserved-state invariance using only local outcomes.

    Every precedence must be externally justified; this routine neither
    determines real triggered effect eligibility nor order-choice authority.
    """
    precedence = tuple(precedences)
    components = effect_dependency_components(
        programs, precedences=precedence
    )
    group_of = {
        effect: group
        for group, component in enumerate(components)
        for effect in component
    }

    # Check *all* input routes, even if the eventual certificate is negative.
    representative_routes: dict[str, str] = {}
    writers: dict[str, set[int]] = defaultdict(set)
    for effect, assignments in programs.items():
        for instance, zone in assignments.items():
            representative_routes.setdefault(instance, zone)
            writers[instance].add(group_of[effect])
    terminal_zone_signature(pending, destinations=representative_routes)

    varying: list[tuple[str, ...]] = []
    witnesses: list[tuple[str, ...]] = []
    checked = 0
    local_orders: list[int] = []
    for group, component in enumerate(components):
        local = ko_order_outcomes(
            {effect: programs[effect] for effect in component},
            precedences=tuple(
                (before, after) for before, after in precedence
                if group_of[before] == group
            ),
        )
        checked += len(local)
        local_orders.append(sum(row.order_count for row in local))
        witnesses.append(min(row.witness_order for row in local))

        exclusive = {
            instance for instance, groups in writers.items()
            if groups == {group}
        }
        histograms = set()
        for outcome in local:
            counts = Counter(
                (pending.state.ledger.instance(instance).card_class, zone)
                for instance, zone in outcome.destinations
                if instance in exclusive
            )
            histograms.add(tuple(sorted(
                (card_class, zone, amount)
                for (card_class, zone), amount in counts.items()
            )))
        if len(histograms) > 1:
            varying.append(component)

    interleavings = factorial(len(programs))
    for component in components:
        interleavings //= factorial(len(component))
    candidate_total_orders = interleavings
    for n in local_orders:
        candidate_total_orders *= n

    if varying:
        return ComponentInvariance(
            False, None, None, len(components), checked,
            tuple(varying), candidate_total_orders,
        )

    witness = lexicographic_interleaving(witnesses)
    resolved = resolve_ordered_programs(programs, witness)
    assert resolved is not None
    state = discard_pending_with_zone_routes(
        pending,
        promote_id=promote_id,
        destinations=resolved_route_map(resolved),
    )
    if state is None:
        raise ValueError("invalid fixed-batch KO promotion or destination")
    return ComponentInvariance(
        True, state, witness, len(components), checked, (),
        candidate_total_orders,
    )
