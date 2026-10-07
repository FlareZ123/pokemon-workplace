"""Exact Energy-route feasibility under action and resource budgets.

The model treats an already-compiled route as three distinct strategic effects:
energy units supplied to the attacker, attack-cost symbols removed, and finite
state resources consumed. This avoids collapsing Energy search, attachment,
transfer, multi-unit Special Energy, and cost reduction into one generic edge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


WILDCARD = "*"
COLORLESS = "C"


@dataclass(frozen=True)
class EnergyUnit:
    """One unit of Energy supplied by an attached card.

    `types` lists specific attack-cost symbols this unit can satisfy. Colorless
    requirements can be satisfied by any Energy unit. A wildcard unit can
    satisfy any specific type.
    """

    types: frozenset[str]


@dataclass(frozen=True)
class EnergyRouteProfile:
    """One state-valid way to use a route or action profile."""

    units: tuple[EnergyUnit, ...] = ()
    reductions: tuple[tuple[str, int], ...] = ()
    resource_costs: tuple[tuple[str, int], ...] = ()
    required_target_tags: frozenset[str] = frozenset()


@dataclass(frozen=True)
class EnergyRouteType:
    """Physical copies of a route, each choosing at most one profile."""

    name: str
    copies: int
    profiles: tuple[EnergyRouteProfile, ...]


@dataclass(frozen=True)
class EnergyRouteResult:
    """Feasibility at three semantic strengths."""

    exact_feasible: bool
    typed_resource_ignorant_feasible: bool
    raw_unit_count_reachable: bool
    minimum_unmet_symbols: int
    witness: tuple[tuple[str, EnergyRouteProfile], ...] | None


def unit(*types: str) -> EnergyUnit:
    """Construct one Energy unit with the given specific-type capabilities."""

    return EnergyUnit(frozenset(types))


def _normalize_cost(cost: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(cost))


def _validate(
    attack_cost: tuple[str, ...],
    resource_capacities: Mapping[str, int],
    routes: Sequence[EnergyRouteType],
) -> None:
    if not attack_cost:
        raise ValueError("attack_cost must contain at least one symbol")
    if any(not symbol for symbol in attack_cost):
        raise ValueError("attack-cost symbols must be non-empty")
    if any(value < 0 for value in resource_capacities.values()):
        raise ValueError("resource capacities must be non-negative")

    for route in routes:
        if route.copies < 0:
            raise ValueError("route copies must be non-negative")
        if not route.profiles:
            raise ValueError("route profiles cannot be empty")
        for profile in route.profiles:
            if any(amount <= 0 for _, amount in profile.reductions):
                raise ValueError("reduction amounts must be positive")
            if any(amount < 0 for _, amount in profile.resource_costs):
                raise ValueError("resource costs must be non-negative")
            if not profile.units and not profile.reductions:
                raise ValueError("each profile must change Energy supply or cost")


def _resource_cost_map(
    costs: tuple[tuple[str, int], ...],
) -> dict[str, int]:
    totals: dict[str, int] = {}
    for name, amount in costs:
        totals[name] = totals.get(name, 0) + amount
    return totals


def _cost_fits(
    costs: tuple[tuple[str, int], ...],
    resources: Mapping[str, int],
) -> bool:
    return all(
        resources.get(name, 0) >= amount
        for name, amount in _resource_cost_map(costs).items()
    )


def _spend(
    costs: tuple[tuple[str, int], ...],
    resources: Mapping[str, int],
) -> dict[str, int]:
    result = dict(resources)
    for name, amount in _resource_cost_map(costs).items():
        result[name] = result.get(name, 0) - amount
    return result


def _apply_reductions(
    cost: tuple[str, ...],
    reductions: tuple[tuple[str, int], ...],
) -> tuple[str, ...]:
    remaining = list(cost)
    for symbol, amount in reductions:
        for _ in range(amount):
            try:
                remaining.remove(symbol)
            except ValueError:
                break
    return _normalize_cost(remaining)


def _unit_matches(unit_: EnergyUnit, symbol: str) -> bool:
    if symbol == COLORLESS:
        return True
    return WILDCARD in unit_.types or symbol in unit_.types


def _remaining_costs_after_units(
    cost: tuple[str, ...],
    units: tuple[EnergyUnit, ...],
) -> set[tuple[str, ...]]:
    """Enumerate all legal remainders after assigning each unit at most once."""

    states = {cost}
    for unit_ in units:
        next_states = set(states)
        for current in states:
            for index, symbol in enumerate(current):
                if not _unit_matches(unit_, symbol):
                    continue
                next_states.add(current[:index] + current[index + 1 :])
        states = next_states
    return states


def _eligible(
    profile: EnergyRouteProfile,
    target_tags: frozenset[str],
) -> bool:
    return profile.required_target_tags <= target_tags


def _evaluate_exact(
    attack_cost: tuple[str, ...],
    resource_capacities: Mapping[str, int],
    target_tags: frozenset[str],
    routes: Sequence[EnergyRouteType],
) -> tuple[
    bool,
    int,
    tuple[tuple[str, EnergyRouteProfile], ...] | None,
]:
    resource_names = tuple(sorted(resource_capacities))
    start_resources = tuple(resource_capacities[name] for name in resource_names)
    states: dict[
        tuple[tuple[str, ...], tuple[int, ...]],
        tuple[tuple[str, EnergyRouteProfile], ...],
    ] = {(attack_cost, start_resources): ()}

    for route in routes:
        for _ in range(route.copies):
            next_states = dict(states)
            for (cost, resource_values), witness in states.items():
                resource_map = dict(zip(resource_names, resource_values))
                for profile in route.profiles:
                    if not _eligible(profile, target_tags):
                        continue
                    if not _cost_fits(profile.resource_costs, resource_map):
                        continue
                    reduced = _apply_reductions(cost, profile.reductions)
                    spent = _spend(profile.resource_costs, resource_map)
                    spent_tuple = tuple(spent[name] for name in resource_names)
                    for remainder in _remaining_costs_after_units(
                        reduced,
                        profile.units,
                    ):
                        key = (remainder, spent_tuple)
                        next_states.setdefault(
                            key,
                            witness + ((route.name, profile),),
                        )
            states = next_states

    feasible = [
        witness
        for (cost, _), witness in states.items()
        if not cost
    ]
    minimum_unmet = min(len(cost) for cost, _ in states)
    return bool(feasible), minimum_unmet, feasible[0] if feasible else None


def evaluate_energy_routes(
    attack_cost: Sequence[str],
    resource_capacities: Mapping[str, int],
    target_tags: Iterable[str],
    routes: Sequence[EnergyRouteType],
) -> EnergyRouteResult:
    """Evaluate exact attack readiness plus two progressively weaker baselines.

    `exact_feasible` respects target restrictions, Energy typing, route-copy
    counts, and finite resource budgets.

    `typed_resource_ignorant_feasible` preserves Energy typing and target
    restrictions but grants enough of every named resource to pay every route.

    `raw_unit_count_reachable` compares only maximum Energy-unit plus exact-cost-
    reduction counts against the attack's converted symbol count. It intentionally
    ignores typing, restrictions, and resource budgets.
    """

    normalized_cost = _normalize_cost(attack_cost)
    capacities = dict(resource_capacities)
    route_types = tuple(routes)
    tags = frozenset(target_tags)
    _validate(normalized_cost, capacities, route_types)

    exact, minimum_unmet, witness = _evaluate_exact(
        normalized_cost,
        capacities,
        tags,
        route_types,
    )

    resource_names = set(capacities)
    for route in route_types:
        for profile in route.profiles:
            resource_names.update(name for name, _ in profile.resource_costs)
    generous = {
        name: sum(
            route.copies
            * max(
                (
                    _resource_cost_map(profile.resource_costs).get(name, 0)
                    for profile in route.profiles
                ),
                default=0,
            )
            for route in route_types
        )
        for name in resource_names
    }
    typed_ignoring_resources, _, _ = _evaluate_exact(
        normalized_cost,
        generous,
        tags,
        route_types,
    )

    raw_capacity = 0
    for route in route_types:
        best = 0
        for profile in route.profiles:
            best = max(
                best,
                len(profile.units) + sum(amount for _, amount in profile.reductions),
            )
        raw_capacity += route.copies * best

    return EnergyRouteResult(
        exact_feasible=exact,
        typed_resource_ignorant_feasible=typed_ignoring_resources,
        raw_unit_count_reachable=raw_capacity >= len(normalized_cost),
        minimum_unmet_symbols=minimum_unmet,
        witness=witness,
    )
