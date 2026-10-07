"""Partition Prize knowledge into exact face-up cards and uncertain face-down cards."""

from __future__ import annotations

from dataclasses import dataclass

from prize_belief_kernel import PrizeBelief
from prize_take_conservation import take_observed_random_prize


@dataclass(frozen=True)
class PrizeVisibilityBelief:
    """One observer's belief over a Prize zone with public position visibility."""

    groups: tuple[str, ...]
    face_up_counts: tuple[int, ...]
    face_up_filler: int
    face_down: PrizeBelief

    def __post_init__(self) -> None:
        if self.face_down.groups != self.groups:
            raise ValueError("face-down belief groups must match visibility groups")
        if len(self.face_up_counts) != len(self.groups):
            raise ValueError("face_up_counts must align with groups")
        if any(count < 0 for count in self.face_up_counts):
            raise ValueError("face-up group counts must be non-negative")
        if self.face_up_filler < 0:
            raise ValueError("face_up_filler must be non-negative")

    @classmethod
    def all_face_down(cls, belief: PrizeBelief) -> "PrizeVisibilityBelief":
        return cls(
            belief.groups,
            tuple(0 for _ in belief.groups),
            0,
            belief,
        )

    @property
    def face_up_count(self) -> int:
        return sum(self.face_up_counts) + self.face_up_filler

    @property
    def total_prize_count(self) -> int:
        return self.face_up_count + self.face_down.prize_count

    def face_up_group_count(self, group: str) -> int:
        if group not in self.groups:
            raise ValueError("group must be modeled")
        return self.face_up_counts[self.groups.index(group)]

    def probability_group_in_face_down(
        self,
        group: str,
        *,
        at_least: int = 1,
    ) -> float:
        if group not in self.groups:
            raise ValueError("group must be modeled")
        if at_least < 0:
            raise ValueError("at_least must be non-negative")
        index = self.groups.index(group)
        return sum(
            mass
            for state, mass in self.face_down.masses
            if state[index] >= at_least
        )

    def collapse_total_composition(self) -> PrizeBelief:
        """Forget which Prize cards are face up and recover composition only."""

        output: dict[tuple[int, ...], float] = {}
        for state, mass in self.face_down.masses:
            total_state = tuple(
                hidden + visible
                for hidden, visible in zip(state, self.face_up_counts)
            )
            output[total_state] = output.get(total_state, 0.0) + mass

        return PrizeBelief(
            self.groups,
            self.total_prize_count,
            tuple(sorted(output.items())),
        )


def reveal_random_face_down_prize(
    state: PrizeVisibilityBelief,
    observed_group: str | None,
) -> PrizeVisibilityBelief:
    """Turn one exchangeable face-down Prize face up after observing its group."""

    if state.face_down.prize_count <= 0:
        raise ValueError("no face-down Prize card remains")

    next_face_down = take_observed_random_prize(
        state.face_down,
        observed_group,
    )
    counts = list(state.face_up_counts)
    filler = state.face_up_filler

    if observed_group is None:
        filler += 1
    else:
        if observed_group not in state.groups:
            raise ValueError("observed_group must be modeled or None")
        counts[state.groups.index(observed_group)] += 1

    next_state = PrizeVisibilityBelief(
        state.groups,
        tuple(counts),
        filler,
        next_face_down,
    )
    if next_state.total_prize_count != state.total_prize_count:
        raise AssertionError("revealing a Prize card changed total Prize count")
    return next_state


def reveal_all_face_down_prizes(
    state: PrizeVisibilityBelief,
    observed_groups: tuple[str | None, ...],
) -> PrizeVisibilityBelief:
    """Reveal every currently face-down Prize in an observed order."""

    if len(observed_groups) != state.face_down.prize_count:
        raise ValueError("must observe exactly every face-down Prize")

    current = state
    for group in observed_groups:
        current = reveal_random_face_down_prize(current, group)
    return current
