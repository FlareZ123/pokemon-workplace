"""Audit set-inclusion geometry of Aichi G&H discard witness families."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_active_choice import _sample_state, bunnelby_first_active, default_active
from aichi_active_discard_flexibility import route_flex
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS


@dataclass(frozen=True)
class InclusionResult:
    trials: int
    policy_difference_states: int
    comparable_gnh: dict[str, int]
    equal: dict[str, int]
    default_proper_subset: dict[str, int]
    bunnelby_proper_subset: dict[str, int]
    incomparable: dict[str, int]
    incomparable_b_more_pairs: dict[str, int]
    incomparable_b_fewer_pairs: dict[str, int]


def simulate_inclusion(
    trials: int,
    *,
    seed: int = 20261007,
) -> InclusionResult:
    rng = random.Random(seed)
    policy_difference_states = 0
    comparable: Counter[str] = Counter()
    equal: Counter[str] = Counter()
    d_subset: Counter[str] = Counter()
    b_subset: Counter[str] = Counter()
    incomparable: Counter[str] = Counter()
    inc_b_more: Counter[str] = Counter()
    inc_b_fewer: Counter[str] = Counter()

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
            d = default.feasible_pairs
            b = bunnelby.feasible_pairs
            if d == b:
                equal[endpoint] += 1
            elif d < b:
                d_subset[endpoint] += 1
            elif b < d:
                b_subset[endpoint] += 1
            else:
                incomparable[endpoint] += 1
                if len(b) > len(d):
                    inc_b_more[endpoint] += 1
                elif len(b) < len(d):
                    inc_b_fewer[endpoint] += 1

    return InclusionResult(
        trials=trials,
        policy_difference_states=policy_difference_states,
        comparable_gnh=dict(comparable),
        equal=dict(equal),
        default_proper_subset=dict(d_subset),
        bunnelby_proper_subset=dict(b_subset),
        incomparable=dict(incomparable),
        incomparable_b_more_pairs=dict(inc_b_more),
        incomparable_b_fewer_pairs=dict(inc_b_fewer),
    )


def main() -> None:
    result = simulate_inclusion(100_000)
    print(f"trials={result.trials}, seed=20261007")
    print(f"policy_difference_states={result.policy_difference_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable_gnh.get(endpoint, 0)
        print(
            endpoint,
            f"comparable={total}",
            f"equal={result.equal.get(endpoint, 0)}",
            f"default_subset_b={result.default_proper_subset.get(endpoint, 0)}",
            f"b_subset_default={result.bunnelby_proper_subset.get(endpoint, 0)}",
            f"incomparable={result.incomparable.get(endpoint, 0)}",
            f"incomparable_b_more={result.incomparable_b_more_pairs.get(endpoint, 0)}",
            f"incomparable_b_fewer={result.incomparable_b_fewer_pairs.get(endpoint, 0)}",
        )


if __name__ == "__main__":
    main()
