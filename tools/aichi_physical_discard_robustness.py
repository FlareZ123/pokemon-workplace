"""Refine Aichi discard robustness from card names to physical hand copies."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, product
import random

from aichi_active_choice import (
    _sample_state,
    bunnelby_first_active,
    default_active,
)
from aichi_active_discard_flexibility import _hand_for_active, route_flex
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS


def discard_pool(state, active: str) -> Counter[str] | None:
    hand = _hand_for_active(state, active)
    deck = state.remaining.copy()

    if hand["Guzma & Hala"] > 0:
        pass
    elif hand["Tag Call"] > 0 and deck["Guzma & Hala"] > 0:
        hand["Tag Call"] -= 1
        if hand["Tag Call"] == 0:
            del hand["Tag Call"]
        deck["Guzma & Hala"] -= 1
        hand["Guzma & Hala"] += 1
    else:
        return None

    hand["Guzma & Hala"] -= 1
    if hand["Guzma & Hala"] == 0:
        del hand["Guzma & Hala"]
    return hand


def expand_physical_edges(
    feasible_pairs: frozenset[tuple[str, str]],
    pool: Counter[str],
) -> frozenset[frozenset[str]]:
    ids = {
        name: tuple(f"{name}#{index + 1}" for index in range(count))
        for name, count in pool.items()
    }
    edges: set[frozenset[str]] = set()

    for first, second in feasible_pairs:
        if first == second:
            for pair in combinations(ids[first], 2):
                edges.add(frozenset(pair))
        else:
            for left, right in product(ids[first], ids[second]):
                edges.add(frozenset((left, right)))

    return frozenset(edges)


def minimum_physical_cut(edges: frozenset[frozenset[str]]) -> int:
    if not edges:
        return 0
    vertices = sorted(set().union(*edges))
    for size in range(1, len(vertices) + 1):
        for chosen in combinations(vertices, size):
            protected = set(chosen)
            if all(protected & edge for edge in edges):
                return size
    raise AssertionError("all physical cards together must hit every edge")


@dataclass(frozen=True)
class PhysicalCutResult:
    trials: int
    policy_difference_states: int
    comparable: dict[str, int]
    default_total: dict[str, int]
    bunnelby_total: dict[str, int]
    bunnelby_larger: dict[str, int]
    default_larger: dict[str, int]
    equal: dict[str, int]
    default_histogram: dict[str, dict[int, int]]
    bunnelby_histogram: dict[str, dict[int, int]]


def simulate_physical_cuts(
    trials: int,
    *,
    seed: int = 20261007,
) -> PhysicalCutResult:
    rng = random.Random(seed)
    policy_difference_states = 0
    comparable: Counter[str] = Counter()
    d_total: Counter[str] = Counter()
    b_total: Counter[str] = Counter()
    b_larger: Counter[str] = Counter()
    d_larger: Counter[str] = Counter()
    equal: Counter[str] = Counter()
    d_hist = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}
    b_hist = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}

    for _ in range(trials):
        state = _sample_state(rng)
        basics = state.opening_basics
        if "Jirachi" in basics or "Bunnelby" not in basics:
            continue

        default_name = default_active(basics)
        bunnelby_name = bunnelby_first_active(basics)
        if default_name == bunnelby_name:
            continue

        policy_difference_states += 1
        d_pool = discard_pool(state, default_name)
        b_pool = discard_pool(state, bunnelby_name)

        for endpoint in ANY_ROUTE_ENDPOINTS:
            default = route_flex(state, default_name, endpoint)
            bunnelby = route_flex(state, bunnelby_name, endpoint)
            if (
                default.natural
                or bunnelby.natural
                or not default.feasible_pairs
                or not bunnelby.feasible_pairs
            ):
                continue
            if d_pool is None or b_pool is None:
                raise AssertionError("G&H route succeeded without a discard pool")

            d_edges = expand_physical_edges(default.feasible_pairs, d_pool)
            b_edges = expand_physical_edges(bunnelby.feasible_pairs, b_pool)
            d_cut = minimum_physical_cut(d_edges)
            b_cut = minimum_physical_cut(b_edges)

            comparable[endpoint] += 1
            d_total[endpoint] += d_cut
            b_total[endpoint] += b_cut
            d_hist[endpoint][d_cut] += 1
            b_hist[endpoint][b_cut] += 1

            if b_cut > d_cut:
                b_larger[endpoint] += 1
            elif d_cut > b_cut:
                d_larger[endpoint] += 1
            else:
                equal[endpoint] += 1

    return PhysicalCutResult(
        trials,
        policy_difference_states,
        dict(comparable),
        dict(d_total),
        dict(b_total),
        dict(b_larger),
        dict(d_larger),
        dict(equal),
        {endpoint: dict(hist) for endpoint, hist in d_hist.items()},
        {endpoint: dict(hist) for endpoint, hist in b_hist.items()},
    )


def main() -> None:
    result = simulate_physical_cuts(100_000)
    print(f"trials={result.trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable.get(endpoint, 0)
        if not total:
            continue
        print(
            endpoint,
            f"comparable={total}",
            f"default_mean={result.default_total[endpoint] / total:.5f}",
            f"bunnelby_mean={result.bunnelby_total[endpoint] / total:.5f}",
            f"b_larger={result.bunnelby_larger.get(endpoint, 0)}",
            f"default_larger={result.default_larger.get(endpoint, 0)}",
            f"equal={result.equal.get(endpoint, 0)}",
        )
        print("  default_hist", sorted(result.default_histogram[endpoint].items()))
        print("  bunnelby_hist", sorted(result.bunnelby_histogram[endpoint].items()))


if __name__ == "__main__":
    main()
