"""Audit card names present in every exact Secret Box payment option."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from aichi_secret_box_payment_families import state_payment_family
from aichi_vileplume_secret_box import (
    BASE_DECK,
    SECRET_BOX_DECK,
    _raw_state,
    _state_succeeds,
)


@dataclass(frozen=True)
class RequiredNameResult:
    trials: int
    incremental_successes: int
    states_with_required_name: int
    required_name_counts: tuple[tuple[str, int], ...]


def common_names(family) -> frozenset[str]:
    if not family:
        return frozenset()
    iterator = iter(family)
    common = set(next(iterator))
    for payment in iterator:
        common.intersection_update(payment)
    return frozenset(common)


def analyze_required_names(
    trials: int,
    *,
    seed: int = 20261007,
) -> RequiredNameResult:
    rng = random.Random(seed)
    incremental = 0
    states_with_required = 0
    counts: Counter[str] = Counter()

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline_state = _raw_state(BASE_DECK, order)
            if baseline_state is not None:
                break

        secret_state = _raw_state(SECRET_BOX_DECK, order)
        if secret_state is None:
            raise AssertionError("ACE SPEC substitution changed setup acceptance")

        if not _state_succeeds(secret_state) or _state_succeeds(baseline_state):
            continue

        incremental += 1
        family = state_payment_family(secret_state)
        if not family:
            raise AssertionError("incremental success has no payment family")

        common = common_names(family)
        states_with_required += int(bool(common))
        counts.update(common)

    return RequiredNameResult(
        trials=trials,
        incremental_successes=incremental,
        states_with_required_name=states_with_required,
        required_name_counts=tuple(
            sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ),
    )


def main() -> None:
    result = analyze_required_names(100_000)
    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"states_with_required_name={result.states_with_required_name}")
    print(f"required_name_counts={dict(result.required_name_counts)}")


if __name__ == "__main__":
    main()
