"""Finite-horizon value-of-information policy over physical Prize positions."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Iterable, Mapping

from prize_position_belief import PrizeGroup, PrizePositionBelief


@dataclass(frozen=True)
class PrizeProbePolicy:
    value: float
    best_position: int | None
    action_values: tuple[float, ...]


@dataclass(frozen=True)
class PrizeTerminalPolicy:
    """Finite-horizon policy for state-dependent terminal utility."""

    value: float
    best_position: int | None
    action_values: tuple[float, ...]
    stop_value: float

@dataclass(frozen=True)
class PrizeDeadlinePolicy:
    """Optimal probability of satisfying target acquisition deadlines."""

    success_probability: float
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

def optimal_prize_terminal_policy(
    state: PrizePositionBelief,
    terminal_utility: Callable[[frozenset[str]], float],
    probes: int,
    *,
    initial_acquired: Iterable[str] = (),
) -> PrizeTerminalPolicy:
    """Optimize position probes for utility evaluated at a finite deadline.

    Unlike ``optimal_prize_probe_policy``, utility need not decompose into a
    fixed reward for each card group. The caller receives the acquired group
    set and can assign conjunctive, threshold, fallback, or other
    state-dependent value.

    ``probes`` is an upper bound. The policy may stop early when the current
    terminal utility is at least as good as every probe continuation.
    """

    if probes < 0:
        raise ValueError("probes must be non-negative")

    acquired = frozenset(initial_acquired)

    @lru_cache(maxsize=None)
    def solve(
        current: PrizePositionBelief,
        remaining: int,
        current_acquired: frozenset[str],
    ) -> PrizeTerminalPolicy:
        stop_value = float(terminal_utility(current_acquired))

        if remaining == 0 or current.prize_count == 0:
            return PrizeTerminalPolicy(
                value=stop_value,
                best_position=None,
                action_values=(),
                stop_value=stop_value,
            )

        values: list[float] = []

        for position in range(current.prize_count):
            expected = 0.0

            for group in (None,) + current.groups:
                probability = current.group_probability_at(position, group)
                if probability <= 0.0:
                    continue

                next_acquired = current_acquired
                if group is not None:
                    next_acquired = current_acquired | {group}

                next_state = _replace_observed_position_with_filler(
                    current,
                    position=position,
                    observed_group=group,
                )
                future = solve(
                    next_state,
                    remaining - 1,
                    frozenset(next_acquired),
                ).value
                expected += probability * future

            values.append(expected)

        best_position = max(
            range(current.prize_count),
            key=values.__getitem__,
        )
        best_probe_value = values[best_position]

        if stop_value >= best_probe_value:
            return PrizeTerminalPolicy(
                value=stop_value,
                best_position=None,
                action_values=tuple(values),
                stop_value=stop_value,
            )

        return PrizeTerminalPolicy(
            value=best_probe_value,
            best_position=best_position,
            action_values=tuple(values),
            stop_value=stop_value,
        )

    return solve(state, probes, acquired)

def optimal_prize_acquisition_deadline_policy(
    state: PrizePositionBelief,
    deadlines: Mapping[str, int],
    *,
    initial_acquired: Iterable[str] = (),
) -> PrizeDeadlinePolicy:
    """Optimize position probes under per-target acquisition deadlines.

    A deadline is the number of additional probes allowed after the current
    action point before that target must be acquired. Deadline zero therefore
    makes the current probe the target's final acquisition opportunity.
    """

    required = tuple(sorted(deadlines))
    if not required:
        return PrizeDeadlinePolicy(1.0, None, ())
    if any(deadlines[group] < 0 for group in required):
        raise ValueError("deadlines must be non-negative")

    modeled = set(state.groups)
    acquired = frozenset(initial_acquired)
    missing_unmodeled = set(required) - modeled - acquired
    if missing_unmodeled:
        return PrizeDeadlinePolicy(
            success_probability=0.0,
            best_position=None,
            action_values=(),
        )

    initial_deadlines = tuple(deadlines[group] for group in required)

    @lru_cache(maxsize=None)
    def solve(
        current: PrizePositionBelief,
        current_deadlines: tuple[int, ...],
        current_acquired: frozenset[str],
    ) -> PrizeDeadlinePolicy:
        if all(group in current_acquired for group in required):
            return PrizeDeadlinePolicy(1.0, None, ())

        if any(
            deadline < 0
            for group, deadline in zip(required, current_deadlines)
            if group not in current_acquired
        ):
            return PrizeDeadlinePolicy(0.0, None, ())

        if current.prize_count == 0:
            return PrizeDeadlinePolicy(0.0, None, ())

        values: list[float] = []

        for position in range(current.prize_count):
            expected = 0.0

            for observed_group in (None,) + current.groups:
                probability = current.group_probability_at(
                    position,
                    observed_group,
                )
                if probability <= 0.0:
                    continue

                next_acquired = current_acquired
                if observed_group in required:
                    next_acquired = current_acquired | {observed_group}

                next_state = _replace_observed_position_with_filler(
                    current,
                    position=position,
                    observed_group=observed_group,
                )
                next_deadlines = tuple(
                    deadline
                    if group in next_acquired
                    else deadline - 1
                    for group, deadline in zip(required, current_deadlines)
                )
                expected += probability * solve(
                    next_state,
                    next_deadlines,
                    frozenset(next_acquired),
                ).success_probability

            values.append(expected)

        best_position = max(
            range(current.prize_count),
            key=values.__getitem__,
        )
        return PrizeDeadlinePolicy(
            success_probability=values[best_position],
            best_position=best_position,
            action_values=tuple(values),
        )

    return solve(state, initial_deadlines, acquired)

