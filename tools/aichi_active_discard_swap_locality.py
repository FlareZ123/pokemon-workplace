"""Audit locality of Aichi starting-Active changes to G&H discard families."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_active_choice import _sample_state, bunnelby_first_active, default_active
from aichi_active_discard_flexibility import route_flex
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS


@dataclass(frozen=True)
class SwapLocalityResult:
    trials: int
    policy_difference_states: int
    comparable: dict[str, int]
    added_edges: dict[str, int]
    removed_edges: dict[str, int]
    added_without_displaced_active: dict[str, int]
    removed_without_bunnelby: dict[str, int]
    violating_states: dict[str, int]


def simulate_swap_locality(trials: int, *, seed: int = 20261007) -> SwapLocalityResult:
    rng = random.Random(seed)
    policy_difference_states = 0
    comparable: Counter[str] = Counter()
    added_edges: Counter[str] = Counter()
    removed_edges: Counter[str] = Counter()
    added_violations: Counter[str] = Counter()
    removed_violations: Counter[str] = Counter()
    state_violations: Counter[str] = Counter()

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
            added = bunnelby.feasible_pairs - default.feasible_pairs
            removed = default.feasible_pairs - bunnelby.feasible_pairs
            added_edges[endpoint] += len(added)
            removed_edges[endpoint] += len(removed)
            bad_added = sum(default_name not in pair for pair in added)
            bad_removed = sum("Bunnelby" not in pair for pair in removed)
            added_violations[endpoint] += bad_added
            removed_violations[endpoint] += bad_removed
            if bad_added or bad_removed:
                state_violations[endpoint] += 1

    return SwapLocalityResult(
        trials, policy_difference_states, dict(comparable), dict(added_edges),
        dict(removed_edges), dict(added_violations), dict(removed_violations),
        dict(state_violations),
    )


def main() -> None:
    result = simulate_swap_locality(100_000)
    print(f"trials={result.trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable.get(endpoint, 0)
        added = result.added_edges.get(endpoint, 0)
        removed = result.removed_edges.get(endpoint, 0)
        add_bad = result.added_without_displaced_active.get(endpoint, 0)
        remove_bad = result.removed_without_bunnelby.get(endpoint, 0)
        state_bad = result.violating_states.get(endpoint, 0)
        print(endpoint, f"comparable={total}", f"added_edges={added}",
              f"removed_edges={removed}",
              f"net_per_state={(added - removed) / total if total else 0:.6f}",
              f"added_without_displaced_active={add_bad}",
              f"removed_without_bunnelby={remove_bad}",
              f"violating_states={state_bad}")
        assert add_bad == 0
        assert remove_bad == 0
        assert state_bad == 0


if __name__ == "__main__":
    main()
