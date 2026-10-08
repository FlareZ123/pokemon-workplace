"""Factor exact KO destination-order analysis across independent effect components.

Build an undirected dependency graph from conflicting explicit assignments
and caller-specified precedence edges. An effect group with no dependency
edge to another group can be ordered independently of that group. The global
order multiplicity is the product of local counts times the number of
interleavings of local effect sequences.
"""

from __future__ import annotations

from itertools import product
from math import factorial
from typing import Iterable, Mapping, Sequence

from ko_order_outcome_space import OrderOutcome, ko_order_outcomes


def effect_dependency_components(
    programs: Mapping[str, Mapping[str, str]],
    *,
    precedences: Iterable[tuple[str, str]] = (),
) -> tuple[tuple[str, ...], ...]:
    """Connect conflicting destination writers and precedence dependencies."""
    effects = tuple(sorted(programs))
    if any(not effect for effect in effects):
        raise ValueError("effect identifiers must be non-empty")
    edges = {effect: set() for effect in effects}
    writers: dict[str, list[tuple[str, str]]] = {}
    for effect, routes in programs.items():
        for instance_id, zone in routes.items():
            if not instance_id or not zone:
                raise ValueError("instance and destination must be non-empty")
            writers.setdefault(instance_id, []).append((effect, zone))

    for assignments in writers.values():
        for i, (left, zone_a) in enumerate(assignments):
            for right, zone_b in assignments[i + 1:]:
                if zone_a != zone_b:
                    edges[left].add(right)
                    edges[right].add(left)

    for before, after in precedences:
        if before not in edges or after not in edges or before == after:
            raise ValueError("invalid effect precedence")
        edges[before].add(after)
        edges[after].add(before)

    components: list[tuple[str, ...]] = []
    unseen = set(effects)
    while unseen:
        visit = [min(unseen)]
        component = set()
        while visit:
            effect = visit.pop()
            if effect not in unseen:
                continue
            unseen.remove(effect)
            component.add(effect)
            visit.extend(edges[effect] & unseen)
        components.append(tuple(sorted(component)))
    return tuple(components)


def lexicographic_interleaving(
    orders: Sequence[Sequence[str]],
) -> tuple[str, ...]:
    """Lexicographically smallest interleaving preserving each input order."""
    positions = [0] * len(orders)
    merged: list[str] = []
    while True:
        possible = [
            (order[pos], group)
            for group, (order, pos) in enumerate(zip(orders, positions))
            if pos < len(order)
        ]
        if not possible:
            return tuple(merged)
        effect, group = min(possible)
        merged.append(effect)
        positions[group] += 1


def factorized_ko_order_outcomes(
    programs: Mapping[str, Mapping[str, str]],
    *,
    precedences: Iterable[tuple[str, str]] = (),
) -> tuple[OrderOutcome, ...]:
    """Return exact outcomes, counts and minimal order witnesses.

    The absence of cross-component edges certifies that relative interleaving
    between effect groups cannot change any card's final destination and
    imposes no ordering restriction. This function does not infer real-world
    trigger coexistence or source-authority policy.
    """
    precedence = tuple(precedences)
    components = effect_dependency_components(
        programs, precedences=precedence
    )
    component_solvers = tuple(
        ko_order_outcomes(
            {effect: programs[effect] for effect in component},
            precedences=tuple(
                (before, after) for before, after in precedence
                if before in component and after in component
            ),
        )
        for component in components
    )
    total_effects = sum(len(component) for component in components)
    interleavings = factorial(total_effects)
    for component in components:
        interleavings //= factorial(len(component))

    accumulated: dict[
        tuple[tuple[str, str], ...],
        tuple[int, tuple[str, ...]],
    ] = {}
    for local_outcomes in product(*component_solvers):
        routes: dict[str, str] = {}
        order_count = interleavings
        for local in local_outcomes:
            order_count *= local.order_count
            for instance, zone in local.destinations:
                previous = routes.get(instance)
                if previous is not None and previous != zone:
                    raise AssertionError("incompatible cross-component routes")
                routes[instance] = zone

        route_vector = tuple(sorted(routes.items()))
        witness = lexicographic_interleaving([
            local.witness_order for local in local_outcomes
        ])
        earlier = accumulated.get(route_vector)
        if earlier is None:
            accumulated[route_vector] = (order_count, witness)
        else:
            accumulated[route_vector] = (
                earlier[0] + order_count,
                min(earlier[1], witness),
            )
    return tuple(
        OrderOutcome(destinations, count, witness)
        for destinations, (count, witness) in sorted(accumulated.items())
    )
