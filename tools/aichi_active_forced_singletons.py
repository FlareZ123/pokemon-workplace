"""Identify named singleton cards forced into Aichi G&H discard pairs.

This extends aichi_active_discard_flexibility by asking which one-copy deck card
names occur in every endpoint-preserving discard pair for a sampled state.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_active_choice import (
    _sample_state,
    bunnelby_first_active,
    default_active,
)
from aichi_active_discard_flexibility import route_flex
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS, DECK_COUNTS


SINGLETONS = frozenset(
    name for name, copies in DECK_COUNTS.items() if copies == 1
)


@dataclass(frozen=True)
class ForcedSingletonResult:
    trials: int
    policy_difference_states: int
    comparable_gnh: dict[str, int]
    default_any_forced: dict[str, int]
    bunnelby_any_forced: dict[str, int]
    default_forced_names: dict[str, dict[str, int]]
    bunnelby_forced_names: dict[str, dict[str, int]]
    bunnelby_rescues_singleton_free: dict[str, int]
    default_rescues_singleton_free: dict[str, int]


def forced_singletons(pairs: frozenset[tuple[str, str]]) -> frozenset[str]:
    """Return singleton names that appear in every feasible discard pair."""
    if not pairs:
        return frozenset()
    return frozenset(
        name
        for name in SINGLETONS
        if all(name in pair for pair in pairs)
    )


def has_singleton_free_pair(pairs: frozenset[tuple[str, str]]) -> bool:
    return any(
        all(name not in SINGLETONS for name in pair)
        for pair in pairs
    )


def simulate_forced_singletons(
    trials: int,
    *,
    seed: int = 20261007,
) -> ForcedSingletonResult:
    rng = random.Random(seed)
    policy_difference_states = 0
    comparable: Counter[str] = Counter()
    default_any: Counter[str] = Counter()
    bunnelby_any: Counter[str] = Counter()
    default_names = {
        endpoint: Counter()
        for endpoint in ANY_ROUTE_ENDPOINTS
    }
    bunnelby_names = {
        endpoint: Counter()
        for endpoint in ANY_ROUTE_ENDPOINTS
    }
    b_rescues_free: Counter[str] = Counter()
    d_rescues_free: Counter[str] = Counter()

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

            if (
                default.natural
                or bunnelby.natural
                or not default.feasible_pairs
                or not bunnelby.feasible_pairs
            ):
                continue

            comparable[endpoint] += 1
            d_forced = forced_singletons(default.feasible_pairs)
            b_forced = forced_singletons(bunnelby.feasible_pairs)

            if d_forced:
                default_any[endpoint] += 1
            if b_forced:
                bunnelby_any[endpoint] += 1

            default_names[endpoint].update(d_forced)
            bunnelby_names[endpoint].update(b_forced)

            d_free = has_singleton_free_pair(default.feasible_pairs)
            b_free = has_singleton_free_pair(bunnelby.feasible_pairs)
            if b_free and not d_free:
                b_rescues_free[endpoint] += 1
            if d_free and not b_free:
                d_rescues_free[endpoint] += 1

    return ForcedSingletonResult(
        trials=trials,
        policy_difference_states=policy_difference_states,
        comparable_gnh=dict(comparable),
        default_any_forced=dict(default_any),
        bunnelby_any_forced=dict(bunnelby_any),
        default_forced_names={
            endpoint: dict(counts)
            for endpoint, counts in default_names.items()
        },
        bunnelby_forced_names={
            endpoint: dict(counts)
            for endpoint, counts in bunnelby_names.items()
        },
        bunnelby_rescues_singleton_free=dict(b_rescues_free),
        default_rescues_singleton_free=dict(d_rescues_free),
    )


def _top_names(counts: dict[str, int], n: int = 8) -> str:
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{name}:{count}" for name, count in ranked[:n]) or "-"


def main() -> None:
    result = simulate_forced_singletons(100_000)
    print(f"trials={result.trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable_gnh.get(endpoint, 0)
        d_forced = result.default_any_forced.get(endpoint, 0)
        b_forced = result.bunnelby_any_forced.get(endpoint, 0)
        print(
            endpoint,
            f"comparable={total}",
            f"default_any_forced={d_forced}",
            f"bunnelby_any_forced={b_forced}",
            "b_rescues_free="
            f"{result.bunnelby_rescues_singleton_free.get(endpoint, 0)}",
            "default_rescues_free="
            f"{result.default_rescues_singleton_free.get(endpoint, 0)}",
        )
        print(
            "  default_names",
            _top_names(result.default_forced_names.get(endpoint, {})),
        )
        print(
            "  bunnelby_names",
            _top_names(result.bunnelby_forced_names.get(endpoint, {})),
        )


if __name__ == "__main__":
    main()
