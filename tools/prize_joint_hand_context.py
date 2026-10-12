"""Joint deck-top/Prize/tag-conditioned hidden hand composition hypotheses.

This extends the tag-conditioned expansion in prize_unknown_hand_composition.
These are observer-model assumptions, not game-rule distributions.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from math import isclose, isfinite

from prize_acquired_hand_reveal import AcquiredPrizeHandState
from prize_position_belief import PrizeGroup
from prize_unknown_hand_composition import (
    HandWorld,
    LatentHandCompositionBelief,
    ObserverLatentHandCompositionBeliefs,
)

JointWorld = tuple[PrizeGroup, tuple[PrizeGroup, ...], PrizeGroup]


def expand_joint_private_prize_hand_composition(
    before: AcquiredPrizeHandState,
    *,
    conditional_other_counts_by_world: Mapping[
        str, Mapping[JointWorld, Mapping[tuple[int, ...], float]]
    ],
) -> ObserverLatentHandCompositionBeliefs:
    """Expand P(top, prizes, tagged) with P(other hand counts | joint world).

    Hypotheses must cover exactly the positive-prior joint worlds of each
    observer. They may differ across observers because information differs.
    The result is accepted by the existing physical random-discard executor.
    """
    result = []
    for observer_id, belief in before.beliefs.beliefs:
        hypotheses = conditional_other_counts_by_world[observer_id]
        supported = {world for world, mass in belief.masses if mass > 0.0}
        if set(hypotheses) != supported:
            raise ValueError(
                f"conditional composition must cover exactly {observer_id}'s "
                "positive-prior top/Prize/tag worlds"
            )

        expanded: dict[HandWorld, float] = defaultdict(float)
        for world, prior in belief.masses:
            if prior <= 0.0:
                continue
            probabilities = hypotheses[world]
            if not probabilities:
                raise ValueError("empty conditional hand composition")
            if any(
                len(counts) != len(belief.groups)
                or any(not isinstance(n, int) or n < 0 for n in counts)
                for counts in probabilities
            ):
                raise ValueError("invalid other-hand group counts")
            if any(
                not isfinite(probability) or probability < 0.0
                for probability in probabilities.values()
            ):
                raise ValueError("conditional probabilities must be finite and nonnegative")
            if not isclose(
                sum(probabilities.values()), 1.0, rel_tol=0.0, abs_tol=1e-12
            ):
                raise ValueError("conditional probabilities must sum to one")
            for counts, conditional in probabilities.items():
                if conditional > 0.0:
                    expanded[(*world, counts)] += prior * conditional

        result.append((
            observer_id,
            LatentHandCompositionBelief(
                belief.groups,
                belief.face_up,
                tuple(sorted(expanded.items(), key=lambda row: repr(row[0]))),
            ),
        ))
    return ObserverLatentHandCompositionBeliefs(tuple(result))
