"""Finite-horizon value-of-information policy over physical Prize positions."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Mapping

from prize_position_belief import PrizeGroup, PrizePositionBelief


@dataclass(frozen=True)
class PrizeProbePolicy:
    value: float
    best_position: int | None
    action_values: tuple[float, ...]


def _replace_observed_position_with_filler(
    state: PrizePositionBelief,
    *,
    position: int,
    observed_group: PrizeGroup,
) -> PrizePositionBelief:
    """Condition on one observed outgoing Prize, then replace that slot with filler."""

    conditioned = state.condition_position(position, observed_group)
    output: dict[tuple[PrizeGroup, ...], float] = {}

    for row, probability in conditioned.masses:
        next_row = list(row)
        next_row[position] = None
        key = tuple(next_row)
        output[key] = output.get(key, 0.0) + probability

    return PrizePositionBelief(
        state.groups,
        state.prize_count,
        tuple(sorted(output.items(), key=lambda item: repr(item[0]))),
    )


def optimal_prize_probe_policy(
    state: PrizePositionBelief,
    rewards: Mapping[str, float],
    probes: int,
) -> PrizeProbePolicy:
    """Return the exact finite-horizon optimal physical-position probe policy.

    A probe reveals the grouped identity in its chosen Prize slot, earns the
    supplied reward for that outgoing group, and replaces the selected Prize
    position with an unmodeled filler card.

    This matches an Arc Phone-like swap followed by deterministic observation
    of the outgoing top card when all strategically valued groups are known to
    remain in the Prize zone before the probe.
    """

    if probes < 0:
        raise ValueError("probes must be non-negative")
    unknown_rewards = set(rewards) - set(state.groups)
    if unknown_rewards:
        raise ValueError("rewards contains groups absent from the belief")

    reward_rows = tuple(sorted((group, float(value)) for group, value in rewards.items()))

    @lru_cache(maxsize=None)
    def solve(
        current: PrizePositionBelief,
        remaining: int,
    ) -> PrizeProbePolicy:
        if remaining == 0:
            return PrizeProbePolicy(
                value=0.0,
                best_position=None,
                action_values=(),
            )

        values: list[float] = []

        for position in range(current.prize_count):
            expected = 0.0
            for group in (None,) + current.groups:
                probability = current.group_probability_at(position, group)
                if probability <= 0.0:
                    continue

                immediate = 0.0
                if group is not None:
                    immediate = dict(reward_rows).get(group, 0.0)

                next_state = _replace_observed_position_with_filler(
                    current,
                    position=position,
                    observed_group=group,
                )
                future = solve(next_state, remaining - 1).value
                expected += probability * (immediate + future)

            values.append(expected)

        best_position = max(range(current.prize_count), key=values.__getitem__)
        return PrizeProbePolicy(
            value=values[best_position],
            best_position=best_position,
            action_values=tuple(values),
        )

    return solve(state, probes)
