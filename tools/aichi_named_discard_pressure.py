"""Measure named-card discard pressure from Aichi starting-Active choice."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_active_choice import _sample_state, bunnelby_first_active, default_active
from aichi_active_discard_flexibility import route_flex
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS, DECK_COUNTS

SINGLETONS = frozenset(name for name, copies in DECK_COUNTS.items() if copies == 1)

def discardable_names(pairs: frozenset[tuple[str, str]]) -> frozenset[str]:
    return frozenset(name for pair in pairs for name in pair)

def forced_names(pairs: frozenset[tuple[str, str]]) -> frozenset[str]:
    if not pairs:
        return frozenset()
    iterator = iter(pairs)
    common = set(next(iterator))
    for pair in iterator:
        common.intersection_update(pair)
        if not common:
            break
    return frozenset(common)

@dataclass(frozen=True)
class NamedPressureResult:
    trials: int
    policy_difference_states: int
    comparable: dict[str, int]
    any_forced_singleton_default: dict[str, int]
    any_forced_singleton_bunnelby: dict[str, int]
    forced_singleton_total_default: dict[str, int]
    forced_singleton_total_bunnelby: dict[str, int]
    bunnelby_clears_all_forced_singletons: dict[str, int]
    bunnelby_creates_forced_singletons: dict[str, int]
    forced_default_by_name: dict[str, dict[str, int]]
    forced_bunnelby_by_name: dict[str, dict[str, int]]
    newly_forced_bunnelby_by_name: dict[str, dict[str, int]]
    newly_avoidable_bunnelby_by_name: dict[str, dict[str, int]]
    newly_exposed_bunnelby_by_name: dict[str, dict[str, int]]
    newly_protected_bunnelby_by_name: dict[str, dict[str, int]]

def _nested(source: dict[str, Counter[str]]) -> dict[str, dict[str, int]]:
    return {endpoint: dict(counts) for endpoint, counts in source.items()}

def simulate_named_pressure(trials: int, *, seed: int = 20261007) -> NamedPressureResult:
    rng = random.Random(seed)
    policy_difference_states = 0
    comparable: Counter[str] = Counter()
    any_d: Counter[str] = Counter()
    any_b: Counter[str] = Counter()
    total_d: Counter[str] = Counter()
    total_b: Counter[str] = Counter()
    clears: Counter[str] = Counter()
    creates: Counter[str] = Counter()
    forced_d = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}
    forced_b = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}
    newly_forced = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}
    newly_avoidable = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}
    newly_exposed = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}
    newly_protected = {endpoint: Counter() for endpoint in ANY_ROUTE_ENDPOINTS}

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

        for endpoint in ANY_ROUTE_ENDPOINTS:
            default = route_flex(state, default_name, endpoint)
            bunnelby = route_flex(state, bunnelby_name, endpoint)
            if default.natural or bunnelby.natural or not default.feasible_pairs or not bunnelby.feasible_pairs:
                continue
            comparable[endpoint] += 1
            d_forced = forced_names(default.feasible_pairs)
            b_forced = forced_names(bunnelby.feasible_pairs)
            d_singletons = d_forced & SINGLETONS
            b_singletons = b_forced & SINGLETONS
            d_discardable = discardable_names(default.feasible_pairs)
            b_discardable = discardable_names(bunnelby.feasible_pairs)
            if d_singletons:
                any_d[endpoint] += 1
            if b_singletons:
                any_b[endpoint] += 1
            total_d[endpoint] += len(d_singletons)
            total_b[endpoint] += len(b_singletons)
            if d_singletons and not b_singletons:
                clears[endpoint] += 1
            if b_singletons and not d_singletons:
                creates[endpoint] += 1
            for name in d_singletons:
                forced_d[endpoint][name] += 1
            for name in b_singletons:
                forced_b[endpoint][name] += 1
            for name in b_singletons - d_singletons:
                newly_forced[endpoint][name] += 1
            for name in d_singletons - b_singletons:
                newly_avoidable[endpoint][name] += 1
            for name in b_discardable - d_discardable:
                newly_exposed[endpoint][name] += 1
            for name in d_discardable - b_discardable:
                newly_protected[endpoint][name] += 1

    return NamedPressureResult(
        trials, policy_difference_states, dict(comparable), dict(any_d), dict(any_b),
        dict(total_d), dict(total_b), dict(clears), dict(creates),
        _nested(forced_d), _nested(forced_b), _nested(newly_forced),
        _nested(newly_avoidable), _nested(newly_exposed), _nested(newly_protected),
    )

def _top(counts: dict[str, int], limit: int = 8) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]

def main() -> None:
    result = simulate_named_pressure(100_000)
    print(f"trials={result.trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable.get(endpoint, 0)
        if not total:
            continue
        d_any = result.any_forced_singleton_default.get(endpoint, 0)
        b_any = result.any_forced_singleton_bunnelby.get(endpoint, 0)
        d_names = result.forced_singleton_total_default.get(endpoint, 0)
        b_names = result.forced_singleton_total_bunnelby.get(endpoint, 0)
        print(endpoint, f"comparable={total}", f"any_forced_singleton_default={d_any}",
              f"any_forced_singleton_bunnelby={b_any}",
              f"mean_forced_singletons_default={d_names / total:.6f}",
              f"mean_forced_singletons_bunnelby={b_names / total:.6f}",
              f"clears_all={result.bunnelby_clears_all_forced_singletons.get(endpoint, 0)}",
              f"creates_any={result.bunnelby_creates_forced_singletons.get(endpoint, 0)}")
        print("  forced_default", _top(result.forced_default_by_name.get(endpoint, {})))
        print("  forced_bunnelby", _top(result.forced_bunnelby_by_name.get(endpoint, {})))
        print("  newly_forced_bunnelby", _top(result.newly_forced_bunnelby_by_name.get(endpoint, {})))
        print("  newly_avoidable_bunnelby", _top(result.newly_avoidable_bunnelby_by_name.get(endpoint, {})))
        print("  newly_exposed_bunnelby", _top(result.newly_exposed_bunnelby_by_name.get(endpoint, {})))
        print("  newly_protected_bunnelby", _top(result.newly_protected_bunnelby_by_name.get(endpoint, {})))

if __name__ == "__main__":
    main()
