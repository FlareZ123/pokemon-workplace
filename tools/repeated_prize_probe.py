"""Repeated face-down Prize probes with and without position memory."""

from __future__ import annotations

from dataclasses import dataclass

from prize_position_belief import PrizePositionBelief


@dataclass(frozen=True)
class RepeatedPrizeProbeMetrics:
    prize_count: int
    prechecked_positions: int
    probes: int
    precheck_success_probability: float
    probe_success_given_precheck_miss: float
    position_aware_success_probability: float
    composition_forgetting_success_probability: float
    position_memory_gain: float


def analyze_repeated_prize_probes(
    *,
    prize_count: int = 6,
    prechecked_positions: int = 3,
    probes: int = 1,
) -> RepeatedPrizeProbeMetrics:
    """Compare exact position memory with a composition-only recurrence.

    One singleton TARGET is known to be among prize_count face-down Prizes.

    prechecked_positions physical slots are checked first, representing a
    Peonia-like multi-card take. Conditional on missing the target, those slots
    are known filler.

    Each later probe chooses one physical position and reveals whether the
    outgoing card is TARGET, representing Arc Phone followed by a deterministic
    top-card observation such as Trekking Shoes.

    The position-aware policy remembers every failed slot. The comparator keeps
    only exact composition after each failed probe, so the same exchangeable
    one-TARGET composition state recurs and each probe is valued at 1/prize_count.
    """

    if prize_count <= 1:
        raise ValueError("prize_count must be at least 2")
    if not 0 <= prechecked_positions < prize_count:
        raise ValueError(
            "prechecked_positions must be between 0 and prize_count - 1"
        )
    if probes < 0:
        raise ValueError("probes must be non-negative")

    initial = PrizePositionBelief.from_exact_composition(
        {"TARGET": 1},
        prize_count=prize_count,
    )
    prechecked = tuple(range(prechecked_positions))
    precheck_miss_probability = sum(
        probability
        for state, probability in initial.masses
        if all(state[position] != "TARGET" for position in prechecked)
    )
    precheck_success_probability = 1.0 - precheck_miss_probability

    belief = initial
    for position in prechecked:
        belief = belief.condition_position(position, None)

    conditional_failure = 1.0
    conditional_success = 0.0

    for _ in range(probes):
        if conditional_failure <= 1e-15:
            break

        position_probabilities = tuple(
            belief.group_probability_at(position, "TARGET")
            for position in range(prize_count)
        )
        chosen_position = max(
            range(prize_count),
            key=position_probabilities.__getitem__,
        )
        hit_probability = position_probabilities[chosen_position]

        conditional_success += conditional_failure * hit_probability
        conditional_failure *= 1.0 - hit_probability

        if hit_probability >= 1.0 - 1e-15:
            break

        belief = belief.condition_position(chosen_position, None)

    position_aware_success_probability = (
        precheck_success_probability
        + precheck_miss_probability * conditional_success
    )

    forgetting_conditional_success = (
        1.0 - (1.0 - 1.0 / prize_count) ** probes
    )
    composition_forgetting_success_probability = (
        precheck_success_probability
        + precheck_miss_probability * forgetting_conditional_success
    )

    return RepeatedPrizeProbeMetrics(
        prize_count=prize_count,
        prechecked_positions=prechecked_positions,
        probes=probes,
        precheck_success_probability=precheck_success_probability,
        probe_success_given_precheck_miss=conditional_success,
        position_aware_success_probability=position_aware_success_probability,
        composition_forgetting_success_probability=(
            composition_forgetting_success_probability
        ),
        position_memory_gain=(
            position_aware_success_probability
            - composition_forgetting_success_probability
        ),
    )
