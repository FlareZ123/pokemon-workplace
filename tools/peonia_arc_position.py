"""Exact positional value for a Peonia -> Arc Phone target line."""

from __future__ import annotations

from dataclasses import dataclass

from prize_position_belief import PrizePositionBelief


@dataclass(frozen=True)
class PeoniaArcPositionMetrics:
    prize_count: int
    peonia_count: int
    peonia_target_probability: float
    arc_target_given_peonia_miss: float
    combined_target_probability: float
    shuffled_arc_target_given_miss: float
    shuffled_combined_target_probability: float
    position_information_gain: float


def analyze_peonia_arc_position(
    *,
    prize_count: int = 6,
    peonia_count: int = 3,
) -> PeoniaArcPositionMetrics:
    """Analyze one singleton target under exact composition and unknown positions.

    Peonia chooses the first selected physical slots. Position labels are
    arbitrary under the initial exchangeable belief. If all selected Prizes are
    filler, their replacement cards are assumed to be known filler cards placed
    back into those same selected slots without a Prize shuffle.

    Arc Phone then chooses the best remaining face-down Prize position. The
    shuffled counterfactual applies a face-down position shuffle after Peonia's
    miss while preserving the same exact composition.
    """

    if prize_count <= 1:
        raise ValueError("prize_count must be at least 2")
    if not 1 <= peonia_count < prize_count:
        raise ValueError("peonia_count must be between 1 and prize_count - 1")

    initial = PrizePositionBelief.from_exact_composition(
        {"TARGET": 1},
        prize_count=prize_count,
    )
    selected = tuple(range(peonia_count))

    miss_probability = sum(
        probability
        for state, probability in initial.masses
        if all(state[position] != "TARGET" for position in selected)
    )
    peonia_target_probability = 1.0 - miss_probability

    miss_belief = initial
    for position in selected:
        miss_belief = miss_belief.condition_position(position, None)

    arc_target_given_peonia_miss = (
        miss_belief.best_position_probability("TARGET")
    )
    combined_target_probability = (
        peonia_target_probability
        + miss_probability * arc_target_given_peonia_miss
    )

    shuffled_miss = miss_belief.shuffle_positions()
    shuffled_arc_target_given_miss = (
        shuffled_miss.best_position_probability("TARGET")
    )
    shuffled_combined_target_probability = (
        peonia_target_probability
        + miss_probability * shuffled_arc_target_given_miss
    )

    return PeoniaArcPositionMetrics(
        prize_count=prize_count,
        peonia_count=peonia_count,
        peonia_target_probability=peonia_target_probability,
        arc_target_given_peonia_miss=arc_target_given_peonia_miss,
        combined_target_probability=combined_target_probability,
        shuffled_arc_target_given_miss=shuffled_arc_target_given_miss,
        shuffled_combined_target_probability=shuffled_combined_target_probability,
        position_information_gain=(
            combined_target_probability
            - shuffled_combined_target_probability
        ),
    )
