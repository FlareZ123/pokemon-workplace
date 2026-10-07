"""Measure starting-Active policy value in the Aichi Vileplume ALS model.

The underlying Aichi planner already models accepted openings, Prize cards, the
first-turn draw, Jirachi Stellar Wish, natural-resource routes, Guzma & Hala
discard costs, Artazon, Fan Rotom, and the named Evolution endpoints.

This module holds every sampled state fixed and changes only which opening Basic
is placed Active. It compares:
- the current planner heuristic;
- a simple Jirachi-first, otherwise Bunnelby-first heuristic;
- an endpoint-specific oracle that may choose any Basic actually present in the
  opening hand.

The oracle is a ceiling for Active selection inside the current model. It is not
a complete gameplay policy.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
import random

from aichi_vileplume_als import (
    ANY_ROUTE_ENDPOINTS,
    BASICS,
    DECK,
    evaluate_any_route_state,
)


@dataclass(frozen=True)
class RawOpeningState:
    opening: tuple[str, ...]
    prizes: tuple[str, ...]
    draw: str
    remaining: Counter[str]
    top_five: tuple[str, ...]
    mulligans: int

    @property
    def opening_basics(self) -> tuple[str, ...]:
        return tuple(card for card in self.opening if card in BASICS)


@dataclass(frozen=True)
class ActiveChoiceResult:
    trials: int
    default_successes: dict[str, int]
    bunnelby_first_successes: dict[str, int]
    oracle_successes: dict[str, int]
    bunnelby_first_gains: dict[str, int]
    bunnelby_first_losses: dict[str, int]
    oracle_gains: dict[str, int]
    mean_mulligans: float

    def probability(self, bucket: str, endpoint: str) -> float:
        counts = getattr(self, bucket)
        return counts.get(endpoint, 0) / self.trials

    def paired_gain_half_width(self, endpoint: str) -> float:
        p = self.oracle_gains.get(endpoint, 0) / self.trials
        return 1.96 * sqrt(p * (1.0 - p) / self.trials)


def _sample_state(rng: random.Random) -> RawOpeningState:
    mulligans = 0
    while True:
        order = rng.sample(range(60), 60)
        opening = tuple(DECK[index] for index in order[:7])
        if any(card in BASICS for card in opening):
            break
        mulligans += 1

    prizes = tuple(DECK[index] for index in order[7:13])
    draw = DECK[order[13]]
    top_five = tuple(DECK[index] for index in order[14:19])

    remaining = Counter(DECK)
    for card in opening + prizes + (draw,):
        remaining[card] -= 1

    return RawOpeningState(
        opening=opening,
        prizes=prizes,
        draw=draw,
        remaining=remaining,
        top_five=top_five,
        mulligans=mulligans,
    )


def _state_for_active(
    state: RawOpeningState,
    active: str,
) -> dict[str, bool]:
    if active not in state.opening_basics:
        raise ValueError(f"{active!r} is not an opening Basic")

    hand = Counter(state.opening + (state.draw,))
    hand[active] -= 1
    if hand[active] == 0:
        del hand[active]

    return evaluate_any_route_state(
        hand,
        state.remaining.copy(),
        active,
        state.top_five,
    )


def default_active(opening_basics: tuple[str, ...]) -> str:
    """Replicate the current Aichi planner's starting-Active heuristic."""
    if "Jirachi" in opening_basics:
        return "Jirachi"
    non_bunnelby = [card for card in opening_basics if card != "Bunnelby"]
    return non_bunnelby[0] if non_bunnelby else "Bunnelby"


def bunnelby_first_active(opening_basics: tuple[str, ...]) -> str:
    """Keep Jirachi priority, then prefer Bunnelby when available."""
    if "Jirachi" in opening_basics:
        return "Jirachi"
    if "Bunnelby" in opening_basics:
        return "Bunnelby"
    return opening_basics[0]


def simulate_active_choice(
    trials: int,
    *,
    seed: int = 20261007,
) -> ActiveChoiceResult:
    rng = random.Random(seed)
    default_successes: Counter[str] = Counter()
    bunnelby_successes: Counter[str] = Counter()
    oracle_successes: Counter[str] = Counter()
    bunnelby_gains: Counter[str] = Counter()
    bunnelby_losses: Counter[str] = Counter()
    oracle_gains: Counter[str] = Counter()
    mulligans = 0

    for _ in range(trials):
        state = _sample_state(rng)
        mulligans += state.mulligans
        basics = state.opening_basics

        choices = tuple(dict.fromkeys(basics))
        by_active = {
            active: _state_for_active(state, active)
            for active in choices
        }

        default_result = by_active[default_active(basics)]
        bunnelby_result = by_active[bunnelby_first_active(basics)]

        for endpoint in ANY_ROUTE_ENDPOINTS:
            default_ok = default_result[endpoint]
            bunnelby_ok = bunnelby_result[endpoint]
            oracle_ok = any(
                result[endpoint]
                for result in by_active.values()
            )

            if default_ok:
                default_successes[endpoint] += 1
            if bunnelby_ok:
                bunnelby_successes[endpoint] += 1
            if oracle_ok:
                oracle_successes[endpoint] += 1

            if bunnelby_ok and not default_ok:
                bunnelby_gains[endpoint] += 1
            if default_ok and not bunnelby_ok:
                bunnelby_losses[endpoint] += 1
            if oracle_ok and not default_ok:
                oracle_gains[endpoint] += 1

            if default_ok and not oracle_ok:
                raise AssertionError(("default exceeded oracle", endpoint))

    return ActiveChoiceResult(
        trials=trials,
        default_successes=dict(default_successes),
        bunnelby_first_successes=dict(bunnelby_successes),
        oracle_successes=dict(oracle_successes),
        bunnelby_first_gains=dict(bunnelby_gains),
        bunnelby_first_losses=dict(bunnelby_losses),
        oracle_gains=dict(oracle_gains),
        mean_mulligans=mulligans / trials,
    )


def find_bunnelby_rescue_witness(
    endpoint: str,
    *,
    seed: int = 20261007,
    max_trials: int = 1_000_000,
) -> RawOpeningState | None:
    """Return a state where Bunnelby-first rescues a default-policy miss."""
    if endpoint not in ANY_ROUTE_ENDPOINTS:
        raise ValueError(endpoint)

    rng = random.Random(seed)
    for _ in range(max_trials):
        state = _sample_state(rng)
        basics = state.opening_basics
        if "Jirachi" in basics or "Bunnelby" not in basics:
            continue

        default_name = default_active(basics)
        bunnelby_name = bunnelby_first_active(basics)
        if default_name == bunnelby_name:
            continue

        default_result = _state_for_active(state, default_name)
        bunnelby_result = _state_for_active(state, bunnelby_name)
        if bunnelby_result[endpoint] and not default_result[endpoint]:
            return state

    return None


def pct(value: float) -> str:
    return f"{100.0 * value:.4f}%"


def main() -> None:
    trials = 200_000
    result = simulate_active_choice(trials)
    print(f"trials={trials}, seed=20261007")
    print(f"mean mulligans={result.mean_mulligans:.6f}")
    print(
        "endpoint | default | Bunnelby-first | oracle | "
        "B-first net pp | oracle gain pp"
    )
    for endpoint in ANY_ROUTE_ENDPOINTS:
        default_p = result.probability("default_successes", endpoint)
        bunnelby_p = result.probability("bunnelby_first_successes", endpoint)
        oracle_p = result.probability("oracle_successes", endpoint)
        print(
            f"{endpoint:14s} | {pct(default_p):>9s} | "
            f"{pct(bunnelby_p):>14s} | {pct(oracle_p):>9s} | "
            f"{100.0 * (bunnelby_p - default_p):+10.4f} | "
            f"{100.0 * (oracle_p - default_p):+10.4f}"
        )


if __name__ == "__main__":
    main()
