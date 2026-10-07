"""Remove chosen Prize positions from joint top/Prize beliefs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_top_swap_belief import TopPrizeJointBelief


def _validate_position(
    belief: TopPrizeJointBelief,
    position: int,
) -> None:
    if not 0 <= position < belief.prize_count:
        raise IndexError("Prize position out of range")


def remove_unobserved_prize_position(
    belief: TopPrizeJointBelief,
    *,
    position: int,
) -> TopPrizeJointBelief:
    """Remove one chosen Prize slot without learning its identity."""

    _validate_position(belief, position)

    output: dict[
        tuple[PrizeGroup, tuple[PrizeGroup, ...]],
        float,
    ] = defaultdict(float)

    for (top_group, prize_state), probability in belief.masses:
        next_prizes = prize_state[:position] + prize_state[position + 1 :]
        output[(top_group, next_prizes)] += probability

    next_face_up = belief.face_up[:position] + belief.face_up[position + 1 :]
    return TopPrizeJointBelief(
        belief.groups,
        next_face_up,
        tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
    )


def remove_observed_prize_position(
    belief: TopPrizeJointBelief,
    *,
    position: int,
    observed_group: PrizeGroup,
) -> TopPrizeJointBelief:
    """Condition on one Prize identity, then remove that physical slot."""

    _validate_position(belief, position)

    evidence = sum(
        probability
        for (_top_group, prize_state), probability in belief.masses
        if prize_state[position] == observed_group
    )
    if evidence == 0.0:
        raise ValueError("Prize observation has zero probability")

    output: dict[
        tuple[PrizeGroup, tuple[PrizeGroup, ...]],
        float,
    ] = defaultdict(float)

    for (top_group, prize_state), probability in belief.masses:
        if prize_state[position] != observed_group:
            continue
        next_prizes = prize_state[:position] + prize_state[position + 1 :]
        output[(top_group, next_prizes)] += probability / evidence

    next_face_up = belief.face_up[:position] + belief.face_up[position + 1 :]
    return TopPrizeJointBelief(
        belief.groups,
        next_face_up,
        tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
    )


def remove_prize_position_for_observers(
    state: ObserverTopPrizeBeliefs,
    *,
    position: int,
    visible_groups: Mapping[str, PrizeGroup],
) -> ObserverTopPrizeBeliefs:
    """Remove one public Prize slot with observer-specific identity visibility."""

    observer_ids = {observer_id for observer_id, _ in state.beliefs}
    if not set(visible_groups) <= observer_ids:
        raise ValueError("visible_groups contains an unknown observer")

    updated = []
    for observer_id, belief in state.beliefs:
        if observer_id in visible_groups:
            belief = remove_observed_prize_position(
                belief,
                position=position,
                observed_group=visible_groups[observer_id],
            )
        else:
            belief = remove_unobserved_prize_position(
                belief,
                position=position,
            )
        updated.append((observer_id, belief))

    return ObserverTopPrizeBeliefs(tuple(updated))
