"""Joint top-deck / Prize belief induced by a face-down Prize swap."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from prize_position_belief import PrizeGroup, PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief


@dataclass(frozen=True)
class TopPrizeJointBelief:
    """Joint belief over the new top-deck group and all Prize positions."""

    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    masses: tuple[tuple[tuple[PrizeGroup, tuple[PrizeGroup, ...]], float], ...]

    def __post_init__(self) -> None:
        if not self.masses:
            raise ValueError("joint belief must have support")
        if len(self.groups) != len(set(self.groups)):
            raise ValueError("groups must be unique")
        modeled = set(self.groups)
        total = 0.0
        for (top_group, prize_state), probability in self.masses:
            if len(prize_state) != len(self.face_up):
                raise ValueError("Prize state must align with visibility")
            if probability < 0.0:
                raise ValueError("probabilities must be non-negative")
            values = (top_group,) + prize_state
            if any(
                value is not None and value not in modeled
                for value in values
            ):
                raise ValueError("joint state contains an unmodeled group")
            total += probability

        if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("joint probability mass must equal one")

    @property
    def prize_count(self) -> int:
        return len(self.face_up)

    def top_probability(self, group: PrizeGroup) -> float:
        return sum(
            probability
            for (top_group, _), probability in self.masses
            if top_group == group
        )

    def prize_probability_at(
        self,
        position: int,
        group: PrizeGroup,
    ) -> float:
        if not 0 <= position < self.prize_count:
            raise IndexError("position out of range")
        return sum(
            probability
            for (_, state), probability in self.masses
            if state[position] == group
        )

    def joint_probability(
        self,
        *,
        top_group: PrizeGroup,
        prize_position: int,
        prize_group: PrizeGroup,
    ) -> float:
        if not 0 <= prize_position < self.prize_count:
            raise IndexError("position out of range")
        return sum(
            probability
            for (current_top, state), probability in self.masses
            if current_top == top_group
            and state[prize_position] == prize_group
        )

    def project_prizes(self) -> PrizeSlotVisibilityBelief:
        output: dict[tuple[PrizeGroup, ...], float] = {}
        for (_, state), probability in self.masses:
            output[state] = output.get(state, 0.0) + probability

        positions = PrizePositionBelief(
            self.groups,
            self.prize_count,
            tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
        )
        return PrizeSlotVisibilityBelief(positions, self.face_up)

    def condition_top(
        self,
        observed_group: PrizeGroup,
    ) -> "TopPrizeJointBelief":
        likelihood = self.top_probability(observed_group)
        if likelihood == 0.0:
            raise ValueError("top observation has zero probability")

        return TopPrizeJointBelief(
            self.groups,
            self.face_up,
            tuple(
                ((top_group, state), probability / likelihood)
                for (top_group, state), probability in self.masses
                if top_group == observed_group
            ),
        )


def swap_known_top_with_face_down_prize(
    state: PrizeSlotVisibilityBelief,
    *,
    position: int,
    incoming_group: PrizeGroup,
) -> TopPrizeJointBelief:
    """Model an Arc Phone-like swap from the acting player's perspective.

    The incoming top-deck group is known to the actor. The selected Prize card
    remains unseen, so its grouped identity becomes an uncertain new top card.
    """

    if not 0 <= position < state.positions.prize_count:
        raise IndexError("position out of range")
    if state.face_up[position]:
        raise ValueError("selected Prize position must be face down")
    if (
        incoming_group is not None
        and incoming_group not in state.positions.groups
    ):
        raise ValueError("incoming_group must be modeled or None")

    output: dict[tuple[PrizeGroup, tuple[PrizeGroup, ...]], float] = {}
    for prize_state, probability in state.positions.masses:
        outgoing_group = prize_state[position]
        next_state = list(prize_state)
        next_state[position] = incoming_group
        key = (outgoing_group, tuple(next_state))
        output[key] = output.get(key, 0.0) + probability

    return TopPrizeJointBelief(
        state.positions.groups,
        state.face_up,
        tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
    )
