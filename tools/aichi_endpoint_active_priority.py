"""Evaluate a fixed endpoint-aware starting-Active priority in the Aichi ALS.

The policy is intentionally information-valid at setup: it depends only on
opening Basic identities and a preselected endpoint. It does not use exact
Prize placement, the first-turn draw, or other downstream sampled truth to
choose the Active.

Evaluation still uses downstream truth to measure the payment family after the
choice. An oracle that sees all downstream truth is reported only as a ceiling.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_active_choice import _sample_state, default_active
from aichi_active_discard_flexibility import route_flex
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS


ACTIVE_PRIORITIES: dict[str, tuple[str, ...]] = {
    "core": ("Bunnelby",),
    "pidgeot": ("Pidgey", "Bunnelby", "Fan Rotom"),
    "stoutland": ("Lillipup", "Bunnelby", "Fan Rotom"),
    "dual": ("Fan Rotom", "Pidgey", "Lillipup", "Bunnelby"),
    "item": ("Oddish", "Bunnelby"),
    "item_pidgeot": ("Oddish", "Fan Rotom", "Pidgey", "Bunnelby"),
    "item_stoutland": ("Oddish", "Fan Rotom", "Lillipup", "Bunnelby"),
}


def endpoint_active(opening_basics: tuple[str, ...], endpoint: str) -> str:
    unique = tuple(dict.fromkeys(opening_basics))
    for name in ACTIVE_PRIORITIES[endpoint]:
        if name in unique:
            return name
    return default_active(opening_basics)


@dataclass(frozen=True)
class EndpointActiveResult:
    trials: int
    comparable: dict[str, int]
    default_pair_total: dict[str, int]
    policy_pair_total: dict[str, int]
    oracle_pair_total: dict[str, int]
    policy_hits_oracle: dict[str, int]
    policy_better: dict[str, int]
    policy_worse: dict[str, int]
    policy_equal: dict[str, int]
    gain_total: dict[str, int]
    loss_total: dict[str, int]


def simulate_endpoint_active_policy(
    trials: int,
    *,
    seed: int = 20261008,
) -> EndpointActiveResult:
    rng = random.Random(seed)
    comparable: Counter[str] = Counter()
    default_total: Counter[str] = Counter()
    policy_total: Counter[str] = Counter()
    oracle_total: Counter[str] = Counter()
    hits: Counter[str] = Counter()
    better: Counter[str] = Counter()
    worse: Counter[str] = Counter()
    equal: Counter[str] = Counter()
    gain: Counter[str] = Counter()
    loss: Counter[str] = Counter()

    for _ in range(trials):
        state = _sample_state(rng)
        basics = tuple(dict.fromkeys(state.opening_basics))
        if "Jirachi" in basics or len(basics) < 2:
            continue

        default_name = default_active(state.opening_basics)

        for endpoint in ANY_ROUTE_ENDPOINTS:
            by_active = {
                active: route_flex(state, active, endpoint)
                for active in basics
            }

            if any(
                flex.natural or not flex.feasible_pairs
                for flex in by_active.values()
            ):
                continue

            counts = {
                active: len(flex.feasible_pairs)
                for active, flex in by_active.items()
            }
            policy_name = endpoint_active(state.opening_basics, endpoint)
            default_count = counts[default_name]
            policy_count = counts[policy_name]
            oracle_count = max(counts.values())

            comparable[endpoint] += 1
            default_total[endpoint] += default_count
            policy_total[endpoint] += policy_count
            oracle_total[endpoint] += oracle_count

            if policy_count == oracle_count:
                hits[endpoint] += 1

            if policy_count > default_count:
                better[endpoint] += 1
                gain[endpoint] += policy_count - default_count
            elif policy_count < default_count:
                worse[endpoint] += 1
                loss[endpoint] += default_count - policy_count
            else:
                equal[endpoint] += 1

    return EndpointActiveResult(
        trials=trials,
        comparable=dict(comparable),
        default_pair_total=dict(default_total),
        policy_pair_total=dict(policy_total),
        oracle_pair_total=dict(oracle_total),
        policy_hits_oracle=dict(hits),
        policy_better=dict(better),
        policy_worse=dict(worse),
        policy_equal=dict(equal),
        gain_total=dict(gain),
        loss_total=dict(loss),
    )


def main() -> None:
    result = simulate_endpoint_active_policy(50_000)
    print(f"trials={result.trials}, seed=20261008")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        total = result.comparable.get(endpoint, 0)
        if not total:
            continue
        print(
            endpoint,
            f"comparable={total}",
            f"default_mean={result.default_pair_total[endpoint] / total:.6f}",
            f"policy_mean={result.policy_pair_total[endpoint] / total:.6f}",
            f"oracle_mean={result.oracle_pair_total[endpoint] / total:.6f}",
            f"oracle_hit={result.policy_hits_oracle[endpoint] / total:.6%}",
            f"better={result.policy_better.get(endpoint, 0) / total:.6%}",
            f"worse={result.policy_worse.get(endpoint, 0) / total:.6%}",
        )


if __name__ == "__main__":
    main()
