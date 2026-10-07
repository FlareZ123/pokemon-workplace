"""Observer-relative K0->K1 Prize-composition conditioning."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_top_swap_belief import TopPrizeJointBelief


def condition_exact_prize_composition(
    belief: TopPrizeJointBelief,
    *,
    group_counts: Mapping[str, int],
) -> TopPrizeJointBelief:
    """Condition on exact modeled Prize composition without learning positions."""

    if set(group_counts) != set(belief.groups):
        raise ValueError("group_counts must cover every modeled group exactly")
    if any(count < 0 for count in group_counts.values()):
        raise ValueError("group counts must be non-negative")
    if sum(group_counts.values()) > belief.prize_count:
        raise ValueError("modeled group counts exceed Prize count")

    expected = tuple(group_counts[group] for group in belief.groups)

    def matches(prize_state) -> bool:
        counts = Counter(prize_state)
        return tuple(counts[group] for group in belief.groups) == expected

    evidence = sum(
        probability
        for (_top_group, prize_state), probability in belief.masses
        if matches(prize_state)
    )
    if evidence == 0.0:
        raise ValueError("Prize composition has zero probability")

    return TopPrizeJointBelief(
        belief.groups,
        belief.face_up,
        tuple(
            ((top_group, prize_state), probability / evidence)
            for (top_group, prize_state), probability in belief.masses
            if matches(prize_state)
        ),
    )


def reveal_exact_prize_composition_to_observers(
    state: ObserverTopPrizeBeliefs,
    *,
    visible_compositions: Mapping[str, Mapping[str, int]],
) -> ObserverTopPrizeBeliefs:
    """Apply exact-composition knowledge only to observers who receive it."""

    observer_ids = {observer_id for observer_id, _belief in state.beliefs}
    if not set(visible_compositions) <= observer_ids:
        raise ValueError("visible_compositions contains an unknown observer")

    updated = []
    for observer_id, belief in state.beliefs:
        composition = visible_compositions.get(observer_id)
        if composition is not None:
            belief = condition_exact_prize_composition(
                belief,
                group_counts=composition,
            )
        updated.append((observer_id, belief))

    return ObserverTopPrizeBeliefs(tuple(updated))
