"""Observer-indexed Prize beliefs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from prize_belief_kernel import PrizeBelief
from prize_take_conservation import take_observed_random_prize
from prize_take_information_asymmetry import remove_unobserved_random_prize


@dataclass(frozen=True)
class ObserverPrizeBeliefs:
    prize_owner_id: str
    beliefs: tuple[tuple[str, PrizeBelief], ...]

    def __post_init__(self) -> None:
        if not self.prize_owner_id:
            raise ValueError("prize_owner_id must be non-empty")
        observer_ids = tuple(observer_id for observer_id, _ in self.beliefs)
        if not observer_ids:
            raise ValueError("at least one observer belief is required")
        if len(observer_ids) != len(set(observer_ids)):
            raise ValueError("observer IDs must be unique")
        if len({belief.prize_count for _, belief in self.beliefs}) != 1:
            raise ValueError("all observers must track the same Prize count")

    @property
    def prize_count(self) -> int:
        return self.beliefs[0][1].prize_count

    def belief_for(self, observer_id: str) -> PrizeBelief:
        for current_id, belief in self.beliefs:
            if current_id == observer_id:
                return belief
        raise KeyError(observer_id)


def update_for_prize_removal(
    state: ObserverPrizeBeliefs,
    *,
    visible_groups: Mapping[str, str | None],
) -> ObserverPrizeBeliefs:
    if state.prize_count <= 0:
        raise ValueError("cannot remove a Prize card when none remain")
    observer_ids = {observer_id for observer_id, _ in state.beliefs}
    if not set(visible_groups) <= observer_ids:
        raise ValueError("visible_groups contains an unknown observer")

    updated = []
    for observer_id, belief in state.beliefs:
        if observer_id in visible_groups:
            next_belief = take_observed_random_prize(
                belief,
                visible_groups[observer_id],
            )
        else:
            next_belief = remove_unobserved_random_prize(belief)
        updated.append((observer_id, next_belief))

    return ObserverPrizeBeliefs(state.prize_owner_id, tuple(updated))
