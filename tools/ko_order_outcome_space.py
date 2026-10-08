"""Exact material outcomes over permitted Knock Out destination-effect orders.

This analyzes precompiled per-instance destination programs under the existing
first-explicit-assignment semantics. It does not choose effect-order authority,
resolve trigger eligibility, or establish which effect orders are game-legal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class OrderOutcome:
    destinations: tuple[tuple[str, str], ...]
    order_count: int
    witness_order: tuple[str, ...]


def ko_order_outcomes(
    programs: Mapping[str, Mapping[str, str]],
    *,
    precedences: Iterable[tuple[str, str]] = (),
    default_destination: str = "discard",
) -> tuple[OrderOutcome, ...]:
    """Count distinct final material routes and legal-within-input orders.

    `precedences` contains only externally established requirements
    (before, after). All other relative effect orders are permitted by this
    model. Counts are integer numbers of permutations, not gameplay
    probabilities. An explicit assignment to the default destination blocks
    later competing redirections, just as any other explicit assignment does.

    The subset dynamic program merges identical partial assignments, retaining
    the number of effect-order prefixes and a representative witness.
    """
    if not default_destination:
        raise ValueError("default destination must be non-empty")
    effects = tuple(sorted(programs))
    if any(not name for name in effects):
        raise ValueError("effect IDs must be non-empty")
    for assignments in programs.values():
        if any(not instance or not zone for instance, zone in assignments.items()):
            raise ValueError("instance IDs and destinations must be non-empty")
    idx = {effect: i for i, effect in enumerate(effects)}
    prerequisites = [0] * len(effects)
    for before, after in precedences:
        if before not in idx or after not in idx or before == after:
            raise ValueError("precedence references unknown or identical effects")
        prerequisites[idx[after]] |= 1 << idx[before]

    instances = tuple(sorted({instance for p in programs.values() for instance in p}))
    updates = tuple(
        tuple(program.get(instance) for instance in instances)
        for _, program in sorted(programs.items())
    )
    # None means never explicitly assigned, even when default is discard.
    initial = tuple(None for _ in instances)
    # Key: (used-effects bitset, partial explicit routes).
    states: dict[tuple[int, tuple[str | None, ...]], tuple[int, tuple[str, ...]]] = {
        (0, initial): (1, ())
    }
    for _ in effects:
        next_states: dict[tuple[int, tuple[str | None, ...]], tuple[int, tuple[str, ...]]] = {}
        for (mask, routes), (count, witness) in states.items():
            for i, effect in enumerate(effects):
                bit = 1 << i
                if mask & bit or mask & prerequisites[i] != prerequisites[i]:
                    continue
                next_routes = tuple(
                    previous if previous is not None else proposed
                    for previous, proposed in zip(routes, updates[i])
                )
                key = (mask | bit, next_routes)
                option = witness + (effect,)
                prior = next_states.get(key)
                if prior is None:
                    next_states[key] = (count, option)
                else:
                    next_states[key] = (prior[0] + count, min(prior[1], option))
        states = next_states
        if not states:
            raise ValueError("precedence constraints contain a cycle")

    totals: dict[tuple[tuple[str, str], ...], tuple[int, tuple[str, ...]]] = {}
    for (_, routes), (count, witness) in states.items():
        destination = tuple(
            (instance, route if route is not None else default_destination)
            for instance, route in zip(instances, routes)
        )
        old = totals.get(destination)
        if old is None:
            totals[destination] = (count, witness)
        else:
            totals[destination] = (old[0] + count, min(old[1], witness))
    return tuple(
        OrderOutcome(destination, count, witness)
        for destination, (count, witness) in sorted(totals.items())
    )
