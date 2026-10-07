"""Measure robustness of Aichi G&H discard families to new UDP protection."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
import random

from aichi_active_choice import (
    _sample_state,
    bunnelby_first_active,
    default_active,
)
from aichi_active_discard_flexibility import route_flex
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS


def minimum_name_protection_cut(
    pairs: frozenset[tuple[str, str]],
) -> int:
    """Minimum card-name set intersecting every feasible discard pair."""
    if not pairs:
        return 0

    names = sorted({name for pair in pairs for name in pair})
    pair_sets = [set(pair) for pair in pairs]

    for size in range(1, len(names) + 1):
        for chosen in combinations(names, size):
            protected = set(chosen)
            if all(protected & pair for pair in pair_sets):
                return size

    raise AssertionError("all names together must hit every pair")


@dataclass(frozen=True)
class RobustnessResult:
    trials: int
    policy_difference_states: int
    comparable_gnh: dict[str, int]
    default_cut_total: dict[str, int]
    bunnelby_cut_total: dict[str, int]
    bunnelby_larger_cut: dict[str, int]
    default_larger_cut: dict[str, int]
    equal_cut: dict[str, int]
    default_cut_histogram: dict[str, dict[int, int]]
    bunnelby_cut_histogram: dict[str, dict[int, int]]


def simulate_robustness(
    trials: int,
    *,
    seed: int = 20261007,
) -> RobustnessResult:
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

            d_cut = minimum_name_protection_cut(default.feasible_pairs)
            b_cut = minimum_name_protection_cut(bunnelby.feasible_pairs)

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

    return RobustnessResult(
        trials=trials,
        policy_difference_states=policy_difference_states,
        comparable_gnh=dict(comparable),
        default_cut_total=dict(d_total),
        bunnelby_cut_total=dict(b_total),
        bunnelby_larger_cut=dict(b_larger),
        default_larger_cut=dict(d_larger),
        equal_cut=dict(equal),
        default_cut_histogram={
            endpoint: dict(hist) for endpoint, hist in d_hist.items()
        },
        bunnelby_cut_histogram={
            endpoint: dict(hist) for endpoint, hist in b_hist.items()
        },
    )


def main() -> None:
    result = simulate_robustness(100_000)
    print(f"trials={result.trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")

    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable_gnh.get(endpoint, 0)
        if not total:
            continue
        d_mean = result.default_cut_total[endpoint] / total
        b_mean = result.bunnelby_cut_total[endpoint] / total
        print(
            endpoint,
            f"comparable={total}",
            f"default_mean_cut={d_mean:.5f}",
            f"bunnelby_mean_cut={b_mean:.5f}",
            f"b_larger={result.bunnelby_larger_cut.get(endpoint, 0)}",
            f"default_larger={result.default_larger_cut.get(endpoint, 0)}",
            f"equal={result.equal_cut.get(endpoint, 0)}",
        )
        print(
            "  default_hist",
            sorted(result.default_cut_histogram[endpoint].items()),
        )
        print(
            "  bunnelby_hist",
            sorted(result.bunnelby_cut_histogram[endpoint].items()),
        )


if __name__ == "__main__":
    main()
