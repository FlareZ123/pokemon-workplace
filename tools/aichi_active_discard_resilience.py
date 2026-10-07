"""Protection-threshold audit for Aichi G&H discard witness families."""

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
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS
from discard_family_resilience import minimum_protection_cut


@dataclass(frozen=True)
class AichiDiscardResilienceResult:
    trials: int
    policy_difference_states: int
    comparable_gnh: dict[str, int]
    cut_total_default: dict[str, int]
    cut_total_bunnelby: dict[str, int]
    bunnelby_higher_cut: dict[str, int]
    bunnelby_lower_cut: dict[str, int]
    more_pairs_lower_cut: dict[str, int]
    fewer_pairs_higher_cut: dict[str, int]
    cut_distribution_default: dict[str, dict[int, int]]
    cut_distribution_bunnelby: dict[str, dict[int, int]]


def simulate_discard_resilience(
    trials: int,
    *,
    seed: int = 20261007,
) -> AichiDiscardResilienceResult:
    rng = random.Random(seed)
    policy_difference_states = 0
    comparable: Counter[str] = Counter()
    cut_default: Counter[str] = Counter()
    cut_bunnelby: Counter[str] = Counter()
    b_higher: Counter[str] = Counter()
    b_lower: Counter[str] = Counter()
    more_pairs_lower: Counter[str] = Counter()
    fewer_pairs_higher: Counter[str] = Counter()
    dist_default = {
        endpoint: Counter()
        for endpoint in ANY_ROUTE_ENDPOINTS
    }
    dist_bunnelby = {
        endpoint: Counter()
        for endpoint in ANY_ROUTE_ENDPOINTS
    }

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
            d_cut = minimum_protection_cut(default.feasible_pairs)
            b_cut = minimum_protection_cut(bunnelby.feasible_pairs)
            cut_default[endpoint] += d_cut
            cut_bunnelby[endpoint] += b_cut
            dist_default[endpoint][d_cut] += 1
            dist_bunnelby[endpoint][b_cut] += 1

            if b_cut > d_cut:
                b_higher[endpoint] += 1
            elif b_cut < d_cut:
                b_lower[endpoint] += 1

            d_pairs = len(default.feasible_pairs)
            b_pairs = len(bunnelby.feasible_pairs)
            if b_pairs > d_pairs and b_cut < d_cut:
                more_pairs_lower[endpoint] += 1
            if b_pairs < d_pairs and b_cut > d_cut:
                fewer_pairs_higher[endpoint] += 1

    return AichiDiscardResilienceResult(
        trials=trials,
        policy_difference_states=policy_difference_states,
        comparable_gnh=dict(comparable),
        cut_total_default=dict(cut_default),
        cut_total_bunnelby=dict(cut_bunnelby),
        bunnelby_higher_cut=dict(b_higher),
        bunnelby_lower_cut=dict(b_lower),
        more_pairs_lower_cut=dict(more_pairs_lower),
        fewer_pairs_higher_cut=dict(fewer_pairs_higher),
        cut_distribution_default={
            endpoint: dict(counts)
            for endpoint, counts in dist_default.items()
        },
        cut_distribution_bunnelby={
            endpoint: dict(counts)
            for endpoint, counts in dist_bunnelby.items()
        },
    )


def main() -> None:
    trials = 100_000
    result = simulate_discard_resilience(trials)
    print(f"trials={trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable_gnh.get(endpoint, 0)
        d_total = result.cut_total_default.get(endpoint, 0)
        b_total = result.cut_total_bunnelby.get(endpoint, 0)
        print(
            endpoint,
            f"comparable={total}",
            f"mean_cut_default={d_total / total if total else 0:.6f}",
            f"mean_cut_bunnelby={b_total / total if total else 0:.6f}",
            f"b_higher={result.bunnelby_higher_cut.get(endpoint, 0)}",
            f"b_lower={result.bunnelby_lower_cut.get(endpoint, 0)}",
            f"more_pairs_lower_cut={result.more_pairs_lower_cut.get(endpoint, 0)}",
            f"fewer_pairs_higher_cut={result.fewer_pairs_higher_cut.get(endpoint, 0)}",
        )
        print(
            "  default_dist",
            sorted(result.cut_distribution_default.get(endpoint, {}).items()),
        )
        print(
            "  bunnelby_dist",
            sorted(result.cut_distribution_bunnelby.get(endpoint, {}).items()),
        )


if __name__ == "__main__":
    main()
