"""Opponent-side belief updates when a Prize is taken without revealing its identity.

The Prize-taking player can use the observed-removal transition from
prize_take_conservation. An observer who learns only that a Prize left the zone
must instead marginalize over every possible removed identity.
"""

from __future__ import annotations

from typing import Iterable

from prize_belief_kernel import PrizeBelief


def remove_unobserved_random_prize(
    belief: PrizeBelief,
) -> PrizeBelief:
    """Remove one exchangeable Prize position without observing its group."""

    if belief.prize_count <= 0:
        raise ValueError("cannot remove a Prize card when prize_count is zero")

    output: dict[tuple[int, ...], float] = {}
    for state, mass in belief.masses:
        filler_count = belief.prize_count - sum(state)
        choices = [(None, filler_count)]
        choices.extend(
            (index, count)
            for index, count in enumerate(state)
        )

        for index, count in choices:
            if count == 0:
                continue

            next_state = list(state)
            if index is not None:
                next_state[index] -= 1
            key = tuple(next_state)
            output[key] = (
                output.get(key, 0.0)
                + mass * count / belief.prize_count
            )

    return PrizeBelief(
        belief.groups,
        belief.prize_count - 1,
        tuple(sorted(output.items())),
    )


def remove_unobserved_prizes(
    belief: PrizeBelief,
    count: int,
) -> PrizeBelief:
    """Remove several unseen Prize identities sequentially."""

    if count < 0:
        raise ValueError("count must be non-negative")
    if count > belief.prize_count:
        raise ValueError("cannot remove more Prize cards than remain")

    current = belief
    for _ in range(count):
        current = remove_unobserved_random_prize(current)
    return current


def group_probability(
    belief: PrizeBelief,
    group: str,
    *,
    at_least: int = 1,
) -> float:
    """Probability that at least a threshold count of one group remains Prized."""

    if group not in belief.groups:
        raise ValueError("group must be modeled")
    if at_least < 0:
        raise ValueError("at_least must be non-negative")

    index = belief.groups.index(group)
    return sum(
        mass
        for state, mass in belief.masses
        if state[index] >= at_least
    )


def expected_group_count(
    belief: PrizeBelief,
    group: str,
) -> float:
    """Posterior expected number of copies of one group still Prized."""

    if group not in belief.groups:
        raise ValueError("group must be modeled")
    index = belief.groups.index(group)
    return sum(state[index] * mass for state, mass in belief.masses)
