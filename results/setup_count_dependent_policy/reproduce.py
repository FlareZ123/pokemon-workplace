"""Validate and demonstrate count-dependent setup policy optimization."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.setup_count_dependent_policy import (  # noqa: E402
    count_dependent_prize_distribution,
    count_dependent_specific_class_prize_probability,
    final_acceptance_source_masses,
    optimize_count_dependent_mulligan_penalty,
)
from tools.setup_hand_value_policy import (  # noqa: E402
    SetupHandState,
    conditioned_prize_hand_distribution,
    opening_hand_distribution,
    optimize_linear_mulligan_penalty,
)


def value(state: SetupHandState) -> float:
    return float(state.feature_counts[0] > 0)


def policy_name(step, optional_states) -> str:
    kept = step.optional_keep_states
    if len(kept) == len(optional_states):
        return "accept-all"
    if not kept:
        return "decline-all"
    good = {state for state in optional_states if value(state) > 0}
    if kept == good:
        return "selective-key"
    return "mixed"


def validate_small_exhaustive() -> None:
    distribution = opening_hand_distribution(
        8, 2, (2,), (2,), opening_hand_size=3
    )
    forced_mass = 0.0
    forced_value_mass = 0.0
    optional = []
    for state, mass in distribution:
        terminal = (
            0.55 * float(state.feature_counts[0] > 0)
            + 0.08 * state.feature_counts[0]
            + 0.03 * state.optional_counts[0]
        )
        if state.forced_in_hand > 0:
            forced_mass += mass
            forced_value_mass += mass * terminal
        elif sum(state.optional_counts) > 0:
            optional.append((state, mass, terminal))

    def small_value(state: SetupHandState) -> float:
        return (
            0.55 * float(state.feature_counts[0] > 0)
            + 0.08 * state.feature_counts[0]
            + 0.03 * state.optional_counts[0]
        )

    tail = optimize_linear_mulligan_penalty(
        8,
        2,
        (2,),
        (2,),
        small_value,
        opening_hand_size=3,
        mulligan_penalty=0.11,
    )
    best = None
    for mask1 in range(2 ** len(optional)):
        keep1 = {
            state
            for index, (state, _, _) in enumerate(optional)
            if mask1 // (2 ** index) % 2
        }
        reject1 = tail.metrics.expected_utility - 0.31
        j1 = forced_value_mass
        accepted1 = forced_mass
        for state, mass, terminal in optional:
            if state in keep1:
                j1 += mass * terminal
                accepted1 += mass
        j1 += (1.0 - accepted1) * reject1

        for mask0 in range(2 ** len(optional)):
            keep0 = {
                state
                for index, (state, _, _) in enumerate(optional)
                if mask0 // (2 ** index) % 2
            }
            reject0 = j1 - 0.17
            j0 = forced_value_mass
            accepted0 = forced_mass
            for state, mass, terminal in optional:
                if state in keep0:
                    j0 += mass * terminal
                    accepted0 += mass
            j0 += (1.0 - accepted0) * reject0
            if best is None or j0 > best:
                best = j0

    optimized = optimize_count_dependent_mulligan_penalty(
        8,
        2,
        (2,),
        (2,),
        small_value,
        prefix_marginal_penalties=(0.17, 0.31),
        tail_marginal_penalty=0.11,
        opening_hand_size=3,
    )
    assert abs(optimized.start.expected_utility - best) < 1e-14


def main() -> None:
    validate_small_exhaustive()

    optional_states = {
        state
        for state, _ in opening_hand_distribution(60, 4, (4,), (4,))
        if state.forced_in_hand == 0 and sum(state.optional_counts) > 0
    }

    stationary = optimize_linear_mulligan_penalty(
        60, 4, (4,), (4,), value, mulligan_penalty=0.1
    )
    constant = optimize_count_dependent_mulligan_penalty(
        60,
        4,
        (4,),
        (4,),
        value,
        prefix_marginal_penalties=(0.1, 0.1, 0.1),
        tail_marginal_penalty=0.1,
    )
    for step in (*constant.prefix_steps, constant.tail_step):
        assert abs(
            step.expected_utility - stationary.metrics.expected_utility
        ) < 1e-14
        assert abs(
            step.acceptance_probability
            - stationary.metrics.acceptance_probability
        ) < 1e-14
        assert step.optional_keep_states == stationary.optional_keep_states

    loosen = optimize_count_dependent_mulligan_penalty(
        60,
        4,
        (4,),
        (4,),
        value,
        prefix_marginal_penalties=(0.1, 0.1),
        tail_marginal_penalty=0.3,
    )
    assert [
        policy_name(step, optional_states)
        for step in loosen.prefix_steps
    ] == ["selective-key", "selective-key"]
    assert policy_name(
        loosen.tail_step, optional_states
    ) == "accept-all"

    tighten = optimize_count_dependent_mulligan_penalty(
        60,
        4,
        (4,),
        (4,),
        value,
        prefix_marginal_penalties=(0.4,),
        tail_marginal_penalty=0.1,
    )
    assert policy_name(
        tighten.prefix_steps[0], optional_states
    ) == "accept-all"
    assert policy_name(
        tighten.tail_step, optional_states
    ) == "selective-key"

    # Final accepted-opening Prize priors are an exact mixture of the
    # count-specific acceptance distributions. A constant schedule must reduce
    # to the stationary selective distribution.
    selective_distribution = dict(
        conditioned_prize_hand_distribution(
            60,
            6,
            forced_starters=4,
            optional_group_sizes=(4,),
            feature_group_sizes=(4,),
            optional_policy=lambda state: float(
                state in stationary.optional_keep_states
            ),
        )
    )
    constant_distribution = dict(
        count_dependent_prize_distribution(
            60,
            6,
            forced_starters=4,
            optional_group_sizes=(4,),
            feature_group_sizes=(4,),
            policy=constant,
        )
    )
    assert selective_distribution.keys() == constant_distribution.keys()
    for counts in selective_distribution:
        assert abs(
            selective_distribution[counts] - constant_distribution[counts]
        ) < 1e-14

    loosen_sources = final_acceptance_source_masses(loosen)
    tighten_sources = final_acceptance_source_masses(tighten)
    assert abs(sum(mass for _, mass in loosen_sources) - 1.0) < 1e-14
    assert abs(sum(mass for _, mass in tighten_sources) - 1.0) < 1e-14

    print("loosen schedule")
    for step in (*loosen.prefix_steps, loosen.tail_step):
        print(
            step.failed_mulligans,
            policy_name(step, optional_states),
            step.expected_utility,
            step.acceptance_probability,
            step.expected_future_mulligans,
            step.reject_continuation_value,
        )

    print("tighten schedule")
    for step in (*tighten.prefix_steps, tighten.tail_step):
        print(
            step.failed_mulligans,
            policy_name(step, optional_states),
            step.expected_utility,
            step.acceptance_probability,
            step.expected_future_mulligans,
            step.reject_continuation_value,
        )

    print("loosen final acceptance source masses", loosen_sources)
    print("tighten final acceptance source masses", tighten_sources)
    for name, policy in (("loosen", loosen), ("tighten", tighten)):
        prize_rates = tuple(
            count_dependent_specific_class_prize_probability(
                60,
                6,
                forced_starters=4,
                optional_group_sizes=(4,),
                feature_group_sizes=(4,),
                policy=policy,
                class_index=index,
            )
            for index in range(4)
        )
        print(name, "final Prize rates", prize_rates)


if __name__ == "__main__":
    main()
