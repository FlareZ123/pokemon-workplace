"""Test structural starting-Active invariance in the Aichi ALS planner."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_active_choice import _sample_state, _state_for_active
from aichi_vileplume_als import ANY_ROUTE_ENDPOINTS


@dataclass(frozen=True)
class InvarianceResult:
    trials: int
    no_jirachi_multi_basic_states: int
    no_jirachi_disagreements: dict[str, int]
    jirachi_choice_states: int
    jirachi_improvements: dict[str, int]
    jirachi_losses: dict[str, int]


def simulate_invariance(
    trials: int,
    *,
    seed: int = 20261007,
) -> InvarianceResult:
    rng = random.Random(seed)
    no_jirachi_multi = 0
    no_jirachi_disagreements: Counter[str] = Counter()
    jirachi_choice_states = 0
    jirachi_improvements: Counter[str] = Counter()
    jirachi_losses: Counter[str] = Counter()

    for _ in range(trials):
        state = _sample_state(rng)
        choices = tuple(dict.fromkeys(state.opening_basics))
        if len(choices) <= 1:
            continue

        by_active = {
            active: _state_for_active(state, active)
            for active in choices
        }

        if "Jirachi" not in choices:
            no_jirachi_multi += 1
            for endpoint in ANY_ROUTE_ENDPOINTS:
                values = {
                    result[endpoint]
                    for result in by_active.values()
                }
                if len(values) > 1:
                    no_jirachi_disagreements[endpoint] += 1
            continue

        jirachi_choice_states += 1
        non_jirachi = [
            result
            for active, result in by_active.items()
            if active != "Jirachi"
        ]
        for endpoint in ANY_ROUTE_ENDPOINTS:
            jirachi_ok = by_active["Jirachi"][endpoint]
            non_jirachi_best = any(
                result[endpoint]
                for result in non_jirachi
            )
            if jirachi_ok and not non_jirachi_best:
                jirachi_improvements[endpoint] += 1
            if non_jirachi_best and not jirachi_ok:
                jirachi_losses[endpoint] += 1

    return InvarianceResult(
        trials=trials,
        no_jirachi_multi_basic_states=no_jirachi_multi,
        no_jirachi_disagreements=dict(no_jirachi_disagreements),
        jirachi_choice_states=jirachi_choice_states,
        jirachi_improvements=dict(jirachi_improvements),
        jirachi_losses=dict(jirachi_losses),
    )


def main() -> None:
    trials = 100_000
    result = simulate_invariance(trials)
    print(f"trials={trials}, seed=20261007")
    print(
        "no_jirachi_multi_basic_states="
        f"{result.no_jirachi_multi_basic_states}"
    )
    print(f"jirachi_choice_states={result.jirachi_choice_states}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        print(
            endpoint,
            "no_jirachi_disagreements="
            f"{result.no_jirachi_disagreements.get(endpoint, 0)}",
            "jirachi_improvements="
            f"{result.jirachi_improvements.get(endpoint, 0)}",
            "jirachi_losses="
            f"{result.jirachi_losses.get(endpoint, 0)}",
        )


if __name__ == "__main__":
    main()
